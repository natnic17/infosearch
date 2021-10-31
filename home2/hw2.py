import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import json
import re

link = 'https://hh.ru/search/vacancy'
search_vacancy = input("Ведите вакансию: ")

params = {'fromSearchLine': 'true',
          'text': search_vacancy,
          'area': '1'
}

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

vacancy_num = 1
page = 0

while True:
    response = requests.get(link, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancy_info = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

    next_page = soup.find('a', text='дальше')

    job = []

    for vac in vacancy_info:
        vacancy_data = {}

        vacancy_name_info = vac.find('a', attrs={'class': 'bloko-link'})
        vacancy_name = vacancy_name_info.text
        vacancy_link = vacancy_name_info['href']
        vacancy_employer = vac.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
        if not vacancy_employer:
            vacancy_employer = None
        else:
            vacancy_employer = vacancy_employer.text

        salary = vac.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})

        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText() \
                .replace(u'\xa0', u'')
            salary = re.split(r'\s|-', salary)

            if salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
            elif salary[0] == 'от':
                salary_min = int(salary[1])
                salary_max = None
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[1])

            salary_currency = salary[2]

        vacancy_data['vacancy_number'] = vacancy_num
        vacancy_data['name'] = vacancy_name
        vacancy_data['link'] = vacancy_link
        vacancy_data['employer'] = vacancy_employer
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency
        vacancy_data['site'] = link

        vacancy_num += 1
        job.append(vacancy_data)

    if not next_page or not response.ok:
        break

    page +=1
    params = {'fromSearchLine': 'true',
              'text': search_vacancy,
              'area': '1',
              'page': page
              }

with open('jobs.json', 'w') as json_file:
    json.dump(job, json_file)

