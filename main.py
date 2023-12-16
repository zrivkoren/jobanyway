import requests
from bs4 import BeautifulSoup
# import lxml
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
import re
from datetime import date

import aggregators
# import main_g4f
import subprocess

from settings import WORDS_FOR_REPLACE
from aggregators import *
from templates import get_letter_from_base_template

load_dotenv()


def make_clean_text(text):
    text = re.sub(r"[^а-яА-Яa-zA-Z.,;:!?]", " ", text)
    text = re.sub(r"[ ]", " ", text)
    return re.sub(' +', ' ', text)


def check_text_on_skills(text: str) -> list:
    skills = []
    for w in WORDS_FOR_REPLACE:
        if w in text.lower():
            if w in WORDS_FOR_REPLACE:
                skills.append(WORDS_FOR_REPLACE[w])
            else:
                skills.append(w)
            text = re.sub(w, "", text, flags=re.IGNORECASE)

    for item in re.findall("[a-zA-Z]{3,}", text):
        skills.append(item)
    return skills


def create_ai_text(text):
    return main_g4f.get_inf(text)


class Vacancy:
    def __init__(self, path=""):
        self._path = path
        self._skills = []
        content = self.check_vacancy_for_provider()
        self.position = content["position"]
        self.company_name = content["company_name"]
        self.company_text = content["company_text"]
        self.salary = content["salary"]
        for s in content["skills"]:
            self.skills = s
        self.compared_skills = self.compare_skills(my_resume)
        CoverLetter(self)

    def check_vacancy_for_provider(self):
        if "hh.ru" in self._path:
            provider = aggregators.HHru()
            return provider.parse_vacancy(self._path)
        elif "habr.com" in self._path:
            self.provider = aggregators.Habr()
        else:
            self.provider = aggregators.OfflineAggregator()

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        if value.lower() in WORDS_FOR_REPLACE:
            value = WORDS_FOR_REPLACE[value.lower()]
        if value.lower() not in [x.lower() for x in self._skills]:
            self._skills.append(value)

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


class OfflineVacancy(Vacancy):
    def __init__(self, path="simple_vacancy.txt"):
        self._skills = []
        with open(path, "r", encoding="utf-8") as file:
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


class CoverLetter:
    def __init__(self, vacancy):
        self._vacancy = vacancy
        self._text = ""
        self.file_path = f"output_files/{date.today()}_{self._vacancy.company_name}.txt"
        self.create_cover_letter()

    def create_cover_letter(self):
        created_ai_text = create_ai_text(self._vacancy.company_text)
        dict_to_send_to_letter_template = {
            "matching_skills": ', '.join(self._vacancy.compared_skills["matching_skills"]),
            "my_remaining_skills": ', '.join(self._vacancy.compared_skills["my_remaining_skills"]),
            "ready_to_study_skills": ', '.join(self._vacancy.compared_skills["ready_to_study"]),
            "created_ai_text": created_ai_text,
            "this_vacancy": self._vacancy,
        }
        self._text = get_letter_from_base_template(dict_to_send_to_letter_template)
        print("Конец обработки сопроводительного письма")

    def save_to_file(self):

        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(self._text)
            file.write(f"\n\n{self._vacancy.company_name}\n{self._vacancy.position}\n{self._vacancy._path}\n{self._vacancy.salary} ")
            print(f"Сопроводительное письмо сохранено в {self.file_path}")

    def run_local_cover_letter(self):
        file_path = f"output_files/{date.today()}_{self._vacancy.company_name}.txt"
        notepad_path = r'C:\Program Files\Notepad++\notepad++.exe'
        try:
            subprocess.run([notepad_path, file_path], shell=True, timeout=1)
            print(f"{self.file_path} открыт")
        except Exception as e:
            pass


if __name__ == '__main__':
    my_resume = MyResume()
    vacancy_for_me = Vacancy("")
    cover_letter = CoverLetter(vacancy_for_me)
    cover_letter.save_to_file()
    cover_letter.run_local_cover_letter()
