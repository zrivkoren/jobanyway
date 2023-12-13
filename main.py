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
    "ООП": "с использованием ООП",
}


class Vacancy:
    def __init__(self, url):
        self.url = url
        self._skills = []
        self.headers = {"user-agent": UserAgent().random}
        content = self.parse_vacancy()
        self.position = content["position"]
        self.company_name = content["company_name"]
        self.company_text = self.get_clean_text(content["company_text"])
        self.salary = content["salary"]

    @staticmethod
    def get_clean_text(text):
        return re.sub(r"[^а-яА-Яa-zA-Z.,;:!?]", " ", text)

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
            try:
                salary = soup.find(attrs={'data-qa': 'vacancy-salary'}).text
                salary = salary.replace(' ', '')
            except:
                salary = "Зарплата не указана"
            content["salary"] = salary

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

        for item in re.findall("[a-zA-Z]{3,}", text):
            self.skills = item

    def compare_skills(self, resume):
        compare = {
            "matching_skills": [x for x in resume.skills if re.search(
                r'\b' + x + r'\b', ' '.join(self.skills), re.IGNORECASE
            )],
            "my_remaining_skills": [x for x in resume.skills if not re.search(
                r'\b' + x + r'\b', ' '.join(self.skills), re.IGNORECASE
            )],
            "ready_to_study": [x for x in self.skills if not re.search(
                r'\b' + x + r'\b', ' '.join(resume.skills), re.IGNORECASE
            )],
        }
        for key, value in compare.items():
            if 'HTML' in value and 'CSS' in value:
                compare[key].remove('HTML')
                compare[key].remove('CSS')
                if 'Bootstrap' in value:
                    compare[key].insert(value.index('Bootstrap') + 1, 'HTML/CSS')
                else:
                    compare[key].append('HTML/CSS')
        return compare

    def create_ai_text(self):
        return main_g4f.get_inf(self.company_text)

    def create_cover_letter(self, resume):
        compare = self.compare_skills(my_resume)
        matching_skills = ', '.join(compare["matching_skills"])
        my_remaining_skills = ', '.join(compare["my_remaining_skills"])
        ready_to_study = ', '.join(compare["ready_to_study"])
        created_ai_text = self.create_ai_text()
        with open(f"output_files/{date.today()}_{self.company_name}.txt", "w", encoding="utf-8") as file:
            file.write("Добрый день!\n")
            file.write(f"Меня зовут {resume.name}, пишу по вакансии {self.position}.\n")
            file.write(f"У меня есть опыт разработки на {matching_skills}.\n")
            file.write(
                f"Некоторые мои проекты можно посмотреть на гитхабе {resume.my_github}\n")
            file.write(f"Готов изучить {ready_to_study}.\n")
            file.write(
                f"Также работал с {my_remaining_skills} и другими технологиями. Подробнее в резюме {resume.resume_file_url}\n\n")
            file.write(created_ai_text)
            file.write(f"\n\nГотов выполнить тестовое задание.\nБуду благодарен за любую обратную связь.\n\n")
            file.write(f"Мои контакты: тг: @{os.getenv('MY_TELEGRAM')}\ne-mail: {os.getenv('MY_EMAIL')}")
            file.write(f"\n\n{self.company_name}\n{self.position}\n{self.url}\n{self.salary}")
        print("Конец обработки вакансии и резюме")
        file_path = f"output_files/{date.today()}_{self.company_name}.txt"
        notepad_path = r'C:\Program Files\Notepad++\notepad++.exe'
        subprocess.run([notepad_path, file_path], shell=True)


class SimpleVacancy(Vacancy):
    def __init__(self, url=None):
        self._skills = []
        with open("simple_vacancy.txt", "r", encoding="utf-8") as file:
            self.url = file.readline()
            self.company_name = file.readline().strip()
            self.position = file.readline().strip()
            self.salary = file.readline().strip()
            self.company_text = " ".join([x.strip() for x in file.readlines()])
        self.check_text_on_skills(self.company_text)


class MyResume:
    def __init__(self):
        self.name = os.getenv("RESUME_NAME")
        self.skills = os.getenv("RESUME_SKILLS").split(",")
        self.my_github = os.getenv("RESUME_MY_GITHUB")
        self.resume_file_url = os.getenv("RESUME_FILE_URL")


IS_HH_VACATION = True

if __name__ == '__main__':
    my_resume = MyResume()
    if IS_HH_VACATION:
        vacancy = Vacancy(os.getenv("VACATION_URL"))
    else:
        vacancy = SimpleVacancy()
    vacancy.create_cover_letter(my_resume)
