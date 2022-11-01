import math
import re

import textract
from pdfminer.high_level import extract_text
from pathlib import Path


def file_tech_search(folders: list, tech_on: list, tech_off: list) -> dict:
    """ Searches for matches with technologies in the tender files.

    In the specified tender folders, selects files with the extension [*.pdf, *.doc, *docx] -> searched for
    matches with two types of technologies (include/on, exclude/off).

    :param folders: A list containing folder names where the tender documentation is stored
    :param tech_on: Necessary technologies for the user
    :param tech_off: Unnecessary technologies to the user
    :return: dictionary containing the number of on/off technology matches for tenders
    """
    encoding = 'utf-8'
    tender_file_path = Path("tenders")
    reg_ex_on = "".join([(t + "|") if (i != len(tech_on) - 1) else t for i, t in enumerate(tech_on)]).lower()
    reg_ex_off = "".join([(t + "|") if (i != len(tech_off) - 1) else t for i, t in enumerate(tech_off)]).lower()
    matches = {}

    for folder in folders:
        folder_path = tender_file_path.joinpath(folder)
        if folder_path.is_dir():
            matches.update(
                {
                    str(folder):
                        {
                            "on": {},
                            "off": {},
                        }
                 }
            )
        for file in folder_path.glob("**/*"):
            if file.suffix == '.pdf':
                tmp_text = extract_text(file, codec=encoding)
            elif file.suffix == '.docx':
                tmp_text = textract.process(file).decode(encoding)
            else:
                continue

            text = "".join("".join(tmp_text.split('\t')).split('\n')).strip().lower()

            if reg_ex_on:
                for res in re.finditer(reg_ex_on, text):
                    if val := matches[str(folder)]['on'].get(res.group(0)):
                        matches[str(folder)]['on'].update({res.group(0): val + 1})
                    else:
                        matches[str(folder)]['on'].update({res.group(0): 1})

            if reg_ex_off:
                for res in re.finditer(reg_ex_off, text):
                    if val := matches[str(folder)]['off'].get(res.group(0)):
                        matches[str(folder)]['off'].update({res.group(0): val + 1})
                    else:
                        matches[str(folder)]['off'].update({res.group(0): 1})

    re.purge()
    return matches


def compute_tf(matches_t: dict) -> dict:
    """Counts TF for TF-IDF method"""
    tf_text = matches_t.copy()
    max_val = max(matches_t.values())

    for key in matches_t.keys():
        tf_text[key] = 0.5 + (0.5 * (tf_text[key] / max_val))

    return tf_text


def compute_idf(word: str, matches_all: dict) -> float:
    """Counts IDF for TF-IDF method"""
    word_count = 0

    for key in matches_all.keys():
        if matches_all[key]['on'].get(word):
            word_count += 1

    return math.log10(len(matches_all) / word_count)


def relevance(matches: dict) -> dict:
    """Assessment of data relevance by TF-IDF method"""
    tenders_list = {}

    for i in matches.keys():
        rel_t = compute_tf(matches[i]['on'])
        for j in rel_t.keys():
            rel_t[j] *= compute_idf(j, matches)
        tenders_list.update({i: sum(rel_t.values())})

    return tenders_list
