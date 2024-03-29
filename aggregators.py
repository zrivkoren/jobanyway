from abc import ABC, abstractmethod
# import lxml
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from main import logger

from settings import WORDS_FOR_REPLACE
from main import make_clean_text, check_text_on_skills


def get_text_from_soup(source_soup: BeautifulSoup, tag: str, attributes: dict):
    result = source_soup.find(tag, attrs=attributes)
    return result.text if result else None


class Aggregator(ABC):
    @abstractmethod
    def __init__(self):
        self.headers = {"user-agent": UserAgent().random}
        logger.debug(f"Назначен агрегатор {self.__class__.__name__}")

    @abstractmethod
    def parse_vacancy(self, url):
        pass

    def get_soup(self, url):
        try:
            data = requests.get(url=url, headers=self.headers, timeout=5)
            data.raise_for_status()
            return BeautifulSoup(data.text, "lxml")
        except requests.exceptions.Timeout:
            logger.error("Запрос превысил таймаут")
        except requests.exceptions.ConnectionError as error:
            logger.error(f"Ошибка соединения: {error}")
        except requests.exceptions.HTTPError as error:
            logger.error(f"Ошибка HTTP: {error}")


class HHru(Aggregator):
    def __init__(self):
        super().__init__()

    def parse_vacancy(self, url):
        soup = self.get_soup(url=url)
        content = dict()
        content["skills"] = []
        try:
            content["position"] = get_text_from_soup(soup, 'h1', {'class': 'bloko-header-section-1'})
            content["company_name"] = soup.find("span", class_='vacancy-company-name').find(
                'span', class_='bloko-header-section-2 bloko-header-section-2_lite'
            ).contents[-1]

            [content["skills"].append(
                x.text if (x.text.lower() not in WORDS_FOR_REPLACE) else WORDS_FOR_REPLACE[x.text.lower()]
            ) for x in soup.findAll('div', class_='bloko-tag bloko-tag_inline')]

            raw_company_text = get_text_from_soup(
                soup, 'div', {'class': 'g-user-content', 'data-qa': 'vacancy-description-print'}
            )
            if not raw_company_text:
                raw_company_text = get_text_from_soup(
                    soup, 'div', {'class': 'g-user-content', 'data-qa': 'vacancy-description'}
                )
            if not raw_company_text:
                raw_company_text = get_text_from_soup(soup, 'div', {'class': 'tmpl_hh_wrapper'})

            company_text = make_clean_text(raw_company_text)
            try:
                salary = soup.find(attrs={'data-qa': 'vacancy-salary'}).text
                salary = salary.replace(' ', '')
            except:
                salary = "Зарплата не указана"
            content["salary"] = salary
            content["skills"].extend(check_text_on_skills(company_text))

            url_company_description = 'https://hh.ru' + soup.find(
                'span', class_='vacancy-company-name'
            ).find('a').get('href')
            company_description = self.parse_vacancy_company_description(url_company_description)
            content["company_text"] = company_text + company_description
        except Exception as e:
            logger.error("Ошибка при парсинге вакансии", e)
        return content

    def parse_vacancy_company_description(self, url):
        soup = self.get_soup(url=url)
        try:
            company_descr = soup.find('div', class_="bloko-gap bloko-gap_top").text
            # company_descr = soup.find('div', attrs={'data-qa': 'company-description-text'}).find().text
            return "\n-Информация о самой компании-: " + make_clean_text(company_descr)
        except:
            try:
                company_descr = soup.find('div', class_='employer-constructor-widgets-container').text
                return "\n-Информация о самой компании-: " + make_clean_text(company_descr)
            except Exception as e:
                logger.error(f" -!-  Парсинг информации о компании {url} завершился с ошибкой -!-", e)
                return ''


class Habr(Aggregator):
    def __init__(self):
        super().__init__()

    def parse_vacancy(self, url):
        soup = self.get_soup(url=url)
        content = dict()
        content["skills"] = []
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
            company_name_div = soup.find("div", class_='company_info').find("div", class_='company_name')
            content["company_name"] = company_name_div.text if company_name_div else "NoName"
            url_company_description = 'https://career.habr.com' + company_name_div.find('a').get('href')
            raw_company_text = soup.find(
                'div', class_='basic-section basic-section--appearance-vacancy-description'
            ).get_text(' ')
            company_text = make_clean_text(raw_company_text)
            content["skills"].extend(check_text_on_skills(company_text))

            company_description = self.parse_vacancy_company_description(url_company_description)
            content["company_text"] = company_text + company_description
        except Exception as e:
            logger.critical(e)
        return content

    def parse_vacancy_company_description(self, url):
        soup = self.get_soup(url=url)
        try:
            company_descr = soup.find('div', class_='about_company').text
            return "\n-Информация о самой компании-: " + make_clean_text(company_descr)
        except Exception as e:
            logger.error(f" -!-  Парсинг информации о компании {url} завершился с ошибкой -!-", e)
            return ''


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
            content["company_text"] = " ".join([x.strip() for x in file.readlines()])
            logger.debug(f"Файл оффлайн вакансии <{content['offline_vacation_url']}> прочитан")
        company_text = make_clean_text(content["company_text"])
        content["skills"] = check_text_on_skills(company_text)
        content["company_text"] = company_text
        return content
