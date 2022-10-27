import asyncio
import unicodedata
import aiohttp_retry
import aiofiles
import aiohttp
import os
import json

from .models import Tender
from aiohttp import ClientConnectorError, ClientConnectionError
from django.http import JsonResponse
from http import HTTPStatus
from bs4 import BeautifulSoup
from asgiref.sync import sync_to_async
from datetime import datetime



async def download_async(title, number, href):
    destination_folder = "media\docs\{}".format(number)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    destination_file = destination_folder + "/{}".format(title)

    if not os.path.exists(destination_file):
        r = await asyncio.gather(get_bytes_payload_async(href))
        r=r[0]

        if r:
            async with aiofiles.open(
                destination_file, "wb"
                ) as outfile:
                    await outfile.write(r)


async def get_doc(attachment_element, num):
    attachment_element = attachment_element.find("span", {"class": "section__value"}) 
    attachment_element = attachment_element.find_next('a')
    doc_name = attachment_element['title']
    href = attachment_element['href']

    if href:
        await download_async(doc_name, num,href)

    return doc_name
   

async def save_tender_info_to_db(number=None, placed=None, end_date=None, object_to_buy=None, customer=None, price=None):
    try:
        await Tender.objects.aget(number=int(number))
    except Tender.DoesNotExist:
        start_date = datetime.strptime(placed, "%d.%m.%Y").date()
        end_date = datetime.strptime(end_date, "%d.%m.%Y").date()
        await Tender.objects.acreate(number=int(number), placement_date=start_date, end_date=end_date, name=object_to_buy, price=float(price), platform=customer)



async def get_info_from_each_header(header):
    data = []
    url_base = "https://zakupki.gov.ru"
    num= header.find("div", {"class": "registry-entry__header-mid__number"}) 
    num=num.text.strip()
    num=num.replace("№ ", "")
    object_to_buy = header.find("div", {"class": "registry-entry__body-value"}) 
    object_to_buy = object_to_buy.text
    customer = header.find("div", {"class": "registry-entry__body-href"}) 
    customer = customer.find("a")
    customer = customer.text.strip()
    price = header.find("div", {"class": "price-block__value"})
    price = price.text
    price = unicodedata.normalize("NFKD", price)
    price = price.replace(",", ".").replace(" ", "")
    price = price.replace("₽", "").strip()
    placed_prev = header.find(text='Размещено')
    placed = placed_prev.find_next('div')
    end_date_prev = header.find(text='Окончание подачи заявок')
    end_date = end_date_prev.find_next('div')
    docs = header.find("div", {"class": "href-block mt-auto d-none"})
    docs = docs.find("a", {"target": "_blank"})
    link = docs.get('href')

    data = [num, placed.text, end_date.text, object_to_buy, customer, price, link ]
    doc_page = url_base + link
    
    r = await asyncio.gather(get_html_async(doc_page))

    if r is not None:
        
        await save_tender_info_to_db(number=num, placed=placed.text, end_date=end_date.text, object_to_buy=object_to_buy, customer=customer, price=price)
        soup = BeautifulSoup(r[0], 'html.parser')

        attachments = soup.find("div", {"class":"blockFilesTabDocs"})
        if attachments is None:
            print(data)
            return num

        else:
            all_attachments = attachments.find_all("div", {"class": "attachment row"}) 
            attachments2 = attachments.find_all("div", {"class": "attachment row "}) 
            attachments3 = attachments.find_all("div", {"class": "attachment row displayNone closedFilesDocs"}) 
            for att in attachments3:
                all_attachments.append(att)
            for att in attachments2:
                all_attachments.append(att)
        
            docs_list = await asyncio.gather(*[get_doc(attachment, num) for attachment in all_attachments])
        
            for doc in docs_list:
                data.append(doc)
       
    print(data)
    return num
    
    

async def get_items_list(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    coll = soup.find_all("div", {"class": "row no-gutters registry-entry__form mr-0"})
    data_list = await asyncio.gather(*[get_info_from_each_header(header) for header in coll])
    return data_list
    
 
async def get_html_async(test_url):
    flag_success = False
    session = aiohttp.ClientSession(trust_env=True)
    while not flag_success:
        try:
            async with session.get(test_url, headers={'User-Agent': 'Custom'}) as response:
                text = await response.text()
                flag_success = True
                await session.close()
                return text    

        except (ClientConnectorError, ClientConnectionError):
            retry_options = aiohttp_retry.ExponentialRetry(attempts=10)
            retry_client = aiohttp_retry.RetryClient(session, retry_options=retry_options)
            try:
                async with retry_client.get(test_url) as response: 
                    text = await response.text()
                    flag_success = True
                    await retry_client.close()
                    return text
                    
            except:
                return None

        except Exception as e:
            print(e)


async def get_bytes_payload_async(test_url):
    flag_success = False
    session = aiohttp.ClientSession(trust_env=True)
    while not flag_success:
        try:
            async with session.get(test_url, headers={'User-Agent': 'Custom'}) as response:
                if response.status == 200:
                    data = await response.read()
                    flag_success = True
                    await session.close()
                    return data

        except (ClientConnectorError, ClientConnectionError):
            retry_options = aiohttp_retry.ExponentialRetry(attempts=10)
            retry_client = aiohttp_retry.RetryClient(session, retry_options=retry_options)
            try:
                async with retry_client.get(test_url) as response:
                    if response.status == 200:
                        data = await response.read()
                        flag_success = True
                        await retry_client.close()
                        return data
            except:
                return None
        except Exception as e:
            print(e)


async def crawler(request):
    if request.body:
        body = json.loads(request.body)
        url = await generate_url(body)
        print(url)

        r = await asyncio.gather(get_html_async(url))
        r=r[0]

        if r is not None:
            soup = BeautifulSoup(r, 'html.parser')
            soup.find("div", {"class": "paginator align-self-center m-0"}) 
            list_items = soup.find_all("span", {"class": "link-text"}) 
            print(list_items)

            if len(list_items) != 0:
    
                last_page = list_items[-1].text
                urls = [url]
                for num in range (2, int(last_page)+1):
                    urls.append(url.replace("pageNumber={}".format(num-1), "pageNumber={}".format(num)))
                sources = []
                sources = await asyncio.gather(*[get_html_async(url) for url in urls])

                list(filter(lambda a: a != None, sources))
                result = await asyncio.gather(*[get_items_list(source) for source in sources])

            else:
                result = await get_items_list(r) 

            if result:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, unite_list, result)
                print(result)
                return JsonResponse({'status': HTTPStatus.OK})

            else:
                result = []
                return JsonResponse({'status': HTTPStatus.NO_CONTENT})

    return JsonResponse({'status': HTTPStatus.BAD_REQUEST})


def unite_list(original):
    united_list = []
    
    for item in original:
        if isinstance(item, list):
            for nested_item in item:
                united_list.append(nested_item)
        else: 
            united_list.append(item)
    return united_list


async def generate_url(body):
    keywords = body.get("search")
    technologies_list = body.get("technologies")
    unwanted_technologies_list = body.get("unwantedTechnologies")
    stage = body.get("purchaseStage")
    law_type_list = body.get("federalLaw")
    price_dict = body.get("price")
    date_dict = body.get("date")

    basic_url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?'
    search_url='searchString='
    url_tail = '&morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&currencyIdGeneral=-1'
    law_url = ""
    stage_url=""
    price_url=""
    date_url=""
        
    keywords = keywords.replace(" ", "+")
    if "44-ФЗ" in law_type_list:
        law_url+="&fz44=on"
    if "223-ФЗ" in law_type_list:
        law_url+="&fz223=on"
    if stage == "Подача заявок":
        stage_url += "&af=on"

    min_price=price_dict.get('minPrice')
    if min_price is not None:
        price_url+="&priceFromGeneral=" + str(min_price)

    max_price=price_dict.get('maxPrice')
    if max_price != 0:
        price_url+="&priceToGeneral=" + str(max_price)
    
    start_date=date_dict.get('beginDate')
    if start_date != "":
        date_url+="&publishDateFrom=" + str(start_date)

    end_date=date_dict.get('endDate')
    if end_date != "":
        date_url+="&applSubmissionCloseDateFrom=" + str(end_date)

    generated_url = basic_url + search_url + keywords + url_tail + law_url + stage_url+ price_url + date_url 

    return generated_url


        



