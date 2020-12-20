#-*-coding:utf-8-*-

import re
from bs4 import BeautifulSoup


def cleansing_html(text):
    pattern = r"(P|TD|LI|BODY)\s{[,:;=a-zA-Z가-힣0-9\-\n\t\s]*}[\n\s\t]*"
    text = re.sub(pattern=pattern, repl=" ", string=text).strip()

    text = BeautifulSoup(text, "lxml").get_text(strip=True)
    return text


def transform_lower_case(text):
    return text.lower()


def transform_upper_case(text):
    return text.upper()


def cleansing_datetime(text):
    pattern = r"\d{2,4}[-/]{0,1}\d{2}[-/]\d{2}[^가-힣]+"
    text = re.sub(pattern=pattern, repl=" ", string=text).strip()

    pattern = r"\d{1,2}[-/]\d{1,2}"
    text = re.sub(pattern=pattern, repl=" ", string=text).strip()

    pattern = r"[오전후]{0,2}\s{0,1}\d{1,2}:\d{1,2}:{0,1}\d{0,2}\s{0,1}[apm]{0,2}[^가-힣]+"
    text = re.sub(pattern=pattern, repl=" ", string=text).strip()

    pattern = r"([0-9]{2,4}년){0,1}\s{0,1}[0-9]{1,2}월\s{0,1}([0-9]{1,2}일){0,1}\s{0,1}([월,화,수,목,금,토,일]요일){0,1}"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_query(text):
    pattern = r"(select|insert|update|delete|create|alter)[^ㄱ-ㅎ가-힣]+;{0,1}"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_url(text):
    pattern = r"(http|ftp|https)://(\w*:\w*@)?[-\w.]+((:\d+)?(\[\w/_.]*(\?\S+)?)?)?"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_email(text):
    pattern = r"[a-zA-Z0-9_-]+@[a-z]+(.[a-z]+){1,2}"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_phone_number(text):
    pattern = r"\d{2,3}-\d{3,4}-\d{4}"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_ip(text):
    pattern = r"([0-9]{2,3}\.){3}[0-9]{2,3}"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()


def cleansing_many_whitespace(text):
    return re.sub(pattern=" +", repl=" ", string=text).strip()


def cleansing_characters(text, save_characters):
    save_ch = ".?!"
    for ch in save_characters:
        save_ch += ch

    pattern = r"[^" + save_ch + r"a-zA-Z0-9가-힣\s]"
    return re.sub(pattern=pattern, repl=" ", string=text).strip()
