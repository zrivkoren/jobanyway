import requests
from bs4 import BeautifulSoup
# import lxml
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
import re
from datetime import date
import main_g4f
import subprocess

load_dotenv()

WORDS_FOR_REPLACE = {
    "django framework": "Django",
    "django rest framework": "Django Rest Framework",
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
    "drf": "Django Rest Framework",
    "postgres": "PostgreSQL",
    "github": "Git",
    "docer compose": "Docker compose",
    "nginx": "nginx",

}
RESERVED_WORDS = {
    "ООП": "Знание ООП",
}


class Vacancy:
    def __init__(self, url):
        self.url = url
        self._skills = []
        self.headers = {"user-agent": UserAgent().random}
        content = self.parse_vacancy()
        self.position = content["position"]
        self.company_name = content["company_name"]
        self.company_text = content["company_text"]

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        if value.lower() in WORDS_FOR_REPLACE:
            value = WORDS_FOR_REPLACE[value.lower()]
        if value.lower() not in [x.lower() for x in self._skills]:
            self._skills.append(value)

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
            ).contents[-1]

            [self.skills.append(
                x.text if (x.text.lower() not in WORDS_FOR_REPLACE) else WORDS_FOR_REPLACE[x.text.lower()]
            ) for x in soup.findAll('div', class_='bloko-tag bloko-tag_inline')]
            company_text = soup.find('div', class_='vacancy-section').text
            content["company_text"] = company_text
            self.check_text_on_skills(company_text)
        except Exception as e:
            print(e)
        return content

    def check_text_on_skills(self, text):
        for w in WORDS_FOR_REPLACE:
            if w in text.lower():
                if w in WORDS_FOR_REPLACE:
                    self.skills = WORDS_FOR_REPLACE[w]
                else:
                    self.skills = w
                text = re.sub(w, "", text, flags=re.IGNORECASE)

        for word in RESERVED_WORDS:
            if word in text.lower():
                self.skills = RESERVED_WORDS[word]
        for item in re.findall("[a-zA-Z]{3,}", text):
            self.skills = item

    def compare_skills(self, resume):
        compare = {
            "matching_skills": [x for x in resume.skills if x in self.skills],
            "my_remaining_skills": [x for x in resume.skills if x not in self.skills],
            "ready_to_study": [x for x in self.skills if x not in resume.skills],
        }
        return compare

    def create_ai_text(self):
        return main_g4f.get_inf(self.company_text)

    def create_cover_letter(self, resume):
        compare = self.compare_skills(my_resume)
        matching_skills = ', '.join(compare["matching_skills"])
        my_remaining_skills = ', '.join(compare["my_remaining_skills"])
        ready_to_study = ', '.join(compare["ready_to_study"])
        with open(f"output_files/{date.today()}_{self.company_name}.txt", "w") as file:
            file.write("Добрый день!\n")
            file.write(f"Меня зовут {resume.name}, пишу по вакансии {self.position}.\n")
            file.write(f"У меня есть опыт разработки на {matching_skills}.\n")
            file.write(
                f"Мои проекты можно посмотреть на гитхабе {resume.my_github}\n")
            file.write(f"Готов изучить {ready_to_study}.\n")
            file.write(
                f"Также знаком с {my_remaining_skills} и другими технологиями. Подробнее в резюме {resume.resume_file_url} \n\n")
            file.write(self.create_ai_text())
            file.write(f"Готов выполнить тестовое задание.\nБуду благодарен за любую обратную связь.\n\n")
            file.write(f"Мои контакты: тг. @{os.getenv('MY_TELEGRAM')}")
            print("Конец обработки вакансии и резюме")
        file_path = f"output_files/{date.today()}_{self.company_name}.txt"
        notepad_path = r'C:\Program Files\Notepad++\notepad++.exe'
        subprocess.run([notepad_path, file_path], shell=True)


class MyResume:
    def __init__(self):
        self.name = os.getenv("RESUME_NAME")
        self.skills = os.getenv("RESUME_SKILLS").split(",")
        self.my_github = os.getenv("RESUME_MY_GITHUB")
        self.resume_file_url = os.getenv("RESUME_FILE_URL")


if __name__ == '__main__':
    my_resume = MyResume()
    vacancy = Vacancy(os.getenv("VACATION_URL"))
    vacancy.create_cover_letter(my_resume)
