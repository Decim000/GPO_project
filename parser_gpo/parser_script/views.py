import asyncio
import json
import os
from datetime import datetime
from http import HTTPStatus

import aiofiles
import aiohttp
import aiohttp_retry
import unicodedata
from aiohttp import ClientConnectorError, ClientConnectionError
from bs4 import BeautifulSoup
from django.http import JsonResponse

from .models import Tender


async def download_async(title: str, number: str, href: str):
    """ Downloads document in async way and saves it to media/docs/<num>

    Args:
        title (str): Title of the document
        number (str): Number of the tender that document related to
        href (str): URL for downloading document
    """
    destination_folder = "media\docs\{}".format(number)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    destination_file = destination_folder + "/{}".format(title)

    if not os.path.exists(destination_file):
        r = await asyncio.gather(get_bytes_payload_async(href))
        try:
            r = r[0]
            async with aiofiles.open(
                    destination_file, "wb"
            ) as outfile:
                await outfile.write(r)
        except Exception as e:
            print(e)


async def get_doc(attachment_element: BeautifulSoup, num: str):
    """ Finds documents's name and starts downloading.

    Args:
        attachment_element (BeautifulSoup): Object where BS4 looks for title and URL
        num (str): Number of the tender

    Returns:
        str: Full name of the document
    """
    attachment_element = attachment_element.find(
        "span", {"class": "section__value"})
    attachment_element = attachment_element.find_next('a')
    doc_name = attachment_element['title']
    href = attachment_element['href']

    if href:
        await download_async(doc_name, num, href)

    return doc_name


async def save_tender_info_to_db(number: str = None, placed: str = None, end_date: str = None, object_to_buy: str = None, customer: str = None,
                                 price: str = None):
    """ Saves the tender's collected info into database.

    Args:
        number (str, optional): Number of the tender. Defaults to None.
        placed (str, optional): Tender's placement date. Defaults to None.
        end_date (str, optional): Tender's end date. Defaults to None.
        object_to_buy (str, optional): Full name of the tender. Defaults to None.
        customer (str, optional): Full name of the customer. Defaults to None.
        price (str, optional): Price of the tender. Defaults to None.
    """
    try:
        await Tender.objects.aget(number=int(number))
    except Tender.DoesNotExist:
        start_date = datetime.strptime(placed, "%d.%m.%Y").date()
        end_date = datetime.strptime(end_date, "%d.%m.%Y").date()
        await Tender.objects.acreate(number=int(number), placement_date=start_date, end_date=end_date,
                                     name=object_to_buy, price=float(price), platform=customer)


async def get_info_from_each_header(header: BeautifulSoup):
    """ Collects info from header (object, number of the tender, price, placement date and end date) and extended page. 
    Finds all attachments and starts their downloading.

    Args:
        header (BeautifulSoup): Object where BS4 looks for information to collect

    Returns:
        str: Number of the tender
    """
    data = []
    url_base = "https://zakupki.gov.ru"
    num = header.find("div", {"class": "registry-entry__header-mid__number"})
    num = num.text.strip()
    num = num.replace("№ ", "")
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

    data = [num, placed.text, end_date.text,
            object_to_buy, customer, price, link]
    doc_page = url_base + link

    r = await asyncio.gather(get_html_async(doc_page))

    if r is not None:

        await save_tender_info_to_db(number=num, placed=placed.text, end_date=end_date.text,
                                     object_to_buy=object_to_buy, customer=customer, price=price)
        soup = BeautifulSoup(r[0], 'html.parser')

        attachments = soup.find("div", {"class": "blockFilesTabDocs"})
        if attachments is None:
            print(data)
            return num

        else:
            all_attachments = attachments.find_all(
                "div", {"class": "attachment row"})
            attachments2 = attachments.find_all(
                "div", {"class": "attachment row "})
            attachments3 = attachments.find_all(
                "div", {"class": "attachment row displayNone closedFilesDocs"})
            for att in attachments3:
                all_attachments.append(att)
            for att in attachments2:
                all_attachments.append(att)

            docs_list = await asyncio.gather(*[get_doc(attachment, num) for attachment in all_attachments])

            for doc in docs_list:
                data.append(doc)

    print(data)
    return num


async def get_items_list(page_source: str):
    """ Starts a search in each header and returns collected info about tenders numbers in list format. 

    Args:
        page_source (str): Page where the function will start search

    Returns:
        list: List of tenders numbers (str)
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    coll = soup.find_all(
        "div", {"class": "row no-gutters registry-entry__form mr-0"})
    data_list = await asyncio.gather(*[get_info_from_each_header(header) for header in coll])
    return data_list


async def get_html_async(test_url: str):
    """ Function that returns the content of the page.

    Args:
        test_url (str): Page's URL

    Returns:
        str: Content of the page
    """
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
            retry_client = aiohttp_retry.RetryClient(
                session, retry_options=retry_options)
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


async def get_bytes_payload_async(test_url: str) -> bytes:
    """ Sends request to the site and returns response payload in binary format using for downloading files.

    Args:
        test_url (str): URL where request will be send to

    Returns:
        bytes: Payload in binary format
    """
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
            retry_client = aiohttp_retry.RetryClient(
                session, retry_options=retry_options)
            try:
                async with retry_client.get(test_url) as response:
                    if response.status == 200:
                        data = await response.read()
                        flag_success = True
                        await retry_client.close()
                        return data
            except:
                return None


async def crawler(request):
    """ Crawler for zakupki.gov.ru

    Crawler asynchronously sends requests to the site, searches for information and collects numbers of tenders in result.

    Args:
        request (HTTPRequest): Request sending from clients to the server

    Returns:
        JSONResponse: Currently returns HTTP-status according to found information
    """
    if request.body:
        body = json.loads(request.body)
        url = await generate_url(body)
        print(url)

        r = await asyncio.gather(get_html_async(url))
        r = r[0]

        if r is not None:
            soup = BeautifulSoup(r, 'html.parser')
            soup.find("div", {"class": "paginator align-self-center m-0"})
            list_items = soup.find_all("span", {"class": "link-text"})
            print(list_items)

            if len(list_items) != 0:

                last_page = list_items[-1].text
                urls = [url]
                for num in range(2, int(last_page) + 1):
                    urls.append(url.replace("pageNumber={}".format(
                        num - 1), "pageNumber={}".format(num)))
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


def unite_list(original: list):
    """ Unites list of lists (one level) in single list.

    Args:
        original (list): List with nested list

    Returns:
        list: Single list without nested lists
    """
    united_list = []

    for item in original:
        if isinstance(item, list):
            for nested_item in item:
                united_list.append(nested_item)
        else:
            united_list.append(item)
    return united_list


async def generate_url(body: dict):
    """ Function that generates URL according to preferences for "zakupki.gov.ru" site.

    Args:
        body (dict): Dictionary with keywords, technologies, stage, law, price and date

    Returns:
        str: URL string
    """
    keywords = body.get("search")
    technologies_list = body.get("technologies")
    unwanted_technologies_list = body.get("unwantedTechnologies")
    stage = body.get("purchaseStage")
    law_type_list = body.get("federalLaw")
    price_dict = body.get("price")
    date_dict = body.get("date")

    basic_url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?'
    search_url = 'searchString='
    url_tail = '&morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&currencyIdGeneral=-1'
    law_url = ""
    stage_url = ""
    price_url = ""
    date_url = ""

    keywords = keywords.replace(" ", "+")
    if "44-ФЗ" in law_type_list:
        law_url += "&fz44=on"
    if "223-ФЗ" in law_type_list:
        law_url += "&fz223=on"
    if stage == "Подача заявок":
        stage_url += "&af=on"

    min_price = price_dict.get('minPrice')
    if min_price is not None:
        price_url += "&priceFromGeneral=" + str(min_price)

    max_price = price_dict.get('maxPrice')
    if max_price != 0:
        price_url += "&priceToGeneral=" + str(max_price)

    start_date = date_dict.get('beginDate')
    if start_date != "":
        date_url += "&publishDateFrom=" + str(start_date)

    end_date = date_dict.get('endDate')
    if end_date != "":
        date_url += "&applSubmissionCloseDateFrom=" + str(end_date)

    generated_url = basic_url + search_url + keywords + \
        url_tail + law_url + stage_url + price_url + date_url

    return generated_url
