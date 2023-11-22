from bs4 import BeautifulSoup
import requests
import lxml
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
import re

load_dotenv()

WORDS_FOR_REPLACE = {
    "django framework": "Django",
    "fastapi": "Fast API"
}


class Vacancy:
    def __init__(self, url):
        self.url = url
        self._skills = []
        self.headers = {"user-agent": UserAgent().random}
        content = self.parse_vacancy()
        self.position = content["position"]
        self.company_name = content["company_name"]
        pass

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        if value.lower() in WORDS_FOR_REPLACE:
            value = WORDS_FOR_REPLACE[value]
        if value.lower() not in [x.lower() for x in self._skills]:
            self._skills.append(value)

    def remove_skill(self, value):
        try:
            self._skills.remove(value)
        except:
            pass

    def parse_vacancy(self):
        data = requests.get(url=self.url, headers=self.headers)
        if data.status_code != 200:
            return
        content = dict()
        soup = BeautifulSoup(data.text, "lxml")
        try:
            content["position"] = soup.find(attrs={'class': 'bloko-header-section-1'}).text
            content["company_name"] = soup.find("span", class_='vacancy-company-name').find(
                'span', class_='bloko-header-section-2 bloko-header-section-2_lite'
            ).text
            [self.skills.append(x.text) for x in soup.findAll('div', class_='bloko-tag bloko-tag_inline')]
            company_text = soup.find('div', class_='vacancy-section').text
            self.check_text_on_skills(company_text)
        except Exception as e:
            print(e)
        return content

    def check_text_on_skills(self, text):
        if any(s in text.lower() for s in ["django rest framework", "drf"]):
            self.skills = "Django Rest Framework"
            text = text.replace("Django Rest Framework", "")
        clear_text = re.findall("[a-zA-Z]{3,}", text)
        for item in clear_text:
            self.skills = item
        pass


class MyResume:
    pass


def check_skills_match(vacation, resume):
    pass

if __name__ == '__main__':
    v1 = Vacancy(url='https://irkutsk.hh.ru/vacancy/89723032')
    # v1 = Vacancy(url='https://irkutsk.hh.ru/vacancy/89653950')
