from abc import ABC, abstractmethod
# import lxml
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from settings import WORDS_FOR_REPLACE
from main import make_clean_text, check_text_on_skills


class Aggregator(ABC):
    @abstractmethod
    def __init__(self):
        self.headers = {"user-agent": UserAgent().random}
        print(f"Назначен агрегатор {self.__class__.__name__}")

    @abstractmethod
    def parse_vacancy(self, url):
        pass


class HHru(Aggregator):
    def __init__(self):
        super().__init__()

    def parse_vacancy(self, url):
        data = requests.get(url=url, headers=self.headers)
        if data.status_code != 200:
            return
        content = dict()
        content["skills"] = []
        soup = BeautifulSoup(data.text, "lxml")
        try:
            content["position"] = soup.find(attrs={'class': 'bloko-header-section-1'}).text
            content["company_name"] = soup.find("span", class_='vacancy-company-name').find(
                'span', class_='bloko-header-section-2 bloko-header-section-2_lite'
            ).contents[-1]

            [content["skills"].append(
                x.text if (x.text.lower() not in WORDS_FOR_REPLACE) else WORDS_FOR_REPLACE[x.text.lower()]
            ) for x in soup.findAll('div', class_='bloko-tag bloko-tag_inline')]
            raw_company_text = soup.find(
                'div', attrs={'class': 'g-user-content', 'data-qa': 'vacancy-description'}
            ).text
            company_text = make_clean_text(raw_company_text)
            try:
                salary = soup.find(attrs={'data-qa': 'vacancy-salary'}).text
                salary = salary.replace(' ', '')
            except:
                salary = "Зарплата не указана"
            content["salary"] = salary

            content["skills"].extend(check_text_on_skills(company_text))

            url_company_description = 'https://hh.ru' + soup.find('span', class_='vacancy-company-name').find('a').get(
                'href')
            company_description = self.parse_vacancy_company_description(url_company_description)
            content["company_text"] = company_text + company_description
        except Exception as e:
            print(e)
        return content

    def parse_vacancy_company_description(self, url):
        data = requests.get(url=url, headers=self.headers)
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.text, "lxml")
        try:
            company_descr = soup.find('div', attrs={'data-qa': 'company-description-text'}).find().text
            return "\n-Информация о самой компании-: " + make_clean_text(company_descr)
        except:
            try:
                company_descr = soup.find('div', class_='employer-constructor-widgets-container').text
                return "\n-Информация о самой компании-: " + make_clean_text(company_descr)
            except Exception as e:
                print(f" -!-  Парсинг информации о компании {url} завершился с ошибкой -!-", e)
                return ''


class Habr(Aggregator):
    def __init__(self):
        super().__init__()

    def parse_vacancy(self, url):
        data = requests.get(url=url, headers=self.headers)
        if data.status_code != 200:
            return
        content = dict()
        content["skills"] = []
        soup = BeautifulSoup(data.text, "lxml")
        try:
            up_section = soup.find('div', class_='basic-section')
            content["position"] = up_section.find("div", class_='page-title').text

            requirements = None
            salary = "Зарплата не указана"
            for section in up_section.find_all('div', {'class': 'content-section'}):
                if "Зарплата" in section.text:
                    salary = section.find('div', class_='basic-salary').text
                if "Требования" in section.text:
                    requirements = [x.text for x in section.find_all('a', class_='link-comp')]
            content["salary"] = salary
            [content["skills"].append(
                x if (x.lower() not in WORDS_FOR_REPLACE) else WORDS_FOR_REPLACE[x.lower()]
            ) for x in requirements]
            content["company_name"] = soup.find("div", class_='company_name company_name--with-icon').text

            raw_company_text = soup.find('div',
                                         class_='basic-section basic-section--appearance-vacancy-description').text
            company_text = make_clean_text(raw_company_text)
            content["skills"].extend(check_text_on_skills(company_text))

            url_company_description = 'https://career.habr.com' + soup.find(
                'div', class_='company_name').find('a').get('href')

            pass

        #     company_description = self.parse_vacancy_company_description(url_company_description)
        #     content["company_text"] = company_text + company_description
        except Exception as e:
            print(e)
        return content

    def parse_vacancy_company_description(self, url):
        pass


class OfflineAggregator(Aggregator):
    def __init__(self):
        super().__init__()

    def parse_vacancy(self, path):
        content = dict()
        with open(path, "r", encoding="utf-8") as file:
            content["offline_vacation_url"] = file.readline().strip()
            content["company_name"] = file.readline().strip()
            content["position"] = file.readline().strip()
            content["salary"] = file.readline().strip()
            content["company_text"] = file.readlines()
            print("Файл оффлайн вакансии прочитан")
        company_text = make_clean_text(content["company_text"])
        content["skills"] = check_text_on_skills(company_text)
        content["company_text"] = company_text
        return content
