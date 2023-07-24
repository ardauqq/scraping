import json
import re
import bs4
import requests
import lxml
from bs4 import BeautifulSoup
from fake_headers import Headers
from tqdm import tqdm

headers = Headers(browser='chrome', os='win')
headers_data = headers.generate()
all_vacancys = []

for p in tqdm(range(0, 40), bar_format="{l_bar}{bar:20}{r_bar}", desc=f'Поиск...'):
    main_page = requests.get(
        f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={p}', headers=headers_data).text
    main_page_soup = BeautifulSoup(main_page, 'lxml')

    vacancy_list_pars = main_page_soup.find_all(class_='vacancy-serp-item__layout')

    for vacancy in vacancy_list_pars:
        lay_1 = vacancy.find('a')
        link = lay_1['href']

        salary = vacancy.find('span', class_='bloko-header-section-3')
        if salary is not None:
            salary_tr = salary.text
            pattern = re.compile(r'\u202f')
            line = ' '
            salary = re.sub(pattern, line, salary_tr)
        if salary is None:
            salary = 'Не указано'

        lay_2 = vacancy.find(class_='vacancy-serp-item-company')
        company_link = lay_2.find('a').text
        name_company = re.sub(r'\s+', ' ', company_link).strip()

        city = re.findall(r'(?:Москва|Санкт-Петербург)', lay_2.text)

        vacancy_dir = {
            'link': link,
            'salary': salary,
            'company': name_company,
            'city': city[0]
        }

        vacancy_page = requests.get(link, headers=headers_data).text
        vacancy_page_soup = bs4.BeautifulSoup(vacancy_page, 'lxml')
        keys_tags = vacancy_page_soup.find('div', class_='bloko-tag-list')
        if keys_tags is not None:
            not_nullable_kt = keys_tags.text
            match = re.search(r'(Django|Flask)', not_nullable_kt)
            if match:
                all_vacancys.append(vacancy_dir)

        filename = 'vacancys_data'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_vacancys, f, indent=4, ensure_ascii=False)