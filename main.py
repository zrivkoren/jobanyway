import os
from dotenv import load_dotenv
import re
from datetime import date

import aggregators
import asyncio
import subprocess

from settings import WORDS_FOR_REPLACE, DIR_SETTINGS, BASE_SETTINGS
from aggregators import *
from templates import get_letter_from_base_template
from main_g4f import run_async_all

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
    return [value for item in asyncio.run(run_async_all(text)) for key, value in item.items() if value]
    # return main_g4f.get_inf(text)


class Vacancy:
    def __init__(self, url=""):
        self.url = url
        self._skills = []
        content = self.check_vacancy_for_provider()
        self.position = content["position"]
        self.company_name = content["company_name"]
        self.company_text = content["company_text"]
        self.salary = content["salary"]
        for s in content["skills"]:
            self.skills = s
        self.compared_skills = self.compare_skills(my_resume)
        self.cover_letter = CoverLetter(self)

    def check_vacancy_for_provider(self):
        if "hh.ru" in self.url:
            provider = aggregators.HHru()
            return provider.parse_vacancy(self.url)
        elif "habr.com" in self.url:
            provider = aggregators.Habr()
            return provider.parse_vacancy(self.url)
        else:
            provider = aggregators.OfflineAggregator()
            result = provider.parse_vacancy(DIR_SETTINGS["OFFLINE_VACATION_PATH"])
            self.url = result["offline_vacation_url"]
            return result

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


class MyResume:
    def __init__(self):
        self.name = os.getenv("RESUME_NAME")
        self.skills = os.getenv("RESUME_SKILLS").split(",")
        self.my_github = os.getenv("RESUME_MY_GITHUB")
        self.resume_file_url = os.getenv("RESUME_FILE_URL")


class CoverLetter:
    def __init__(self, vacancy: Vacancy):
        self.vacancy = vacancy
        self.text = ""
        self.file_path = f"{DIR_SETTINGS['SAVE_LOCATION_DIR']}{date.today()}_{self.vacancy.company_name}.txt"
        self.create_cover_letter()

    def create_cover_letter(self):
        created_ai_text = '\n\nЕще вариант: '.join(create_ai_text(self.vacancy.company_text))
        dict_to_send_to_letter_template = {
            "matching_skills": ', '.join(self.vacancy.compared_skills["matching_skills"]),
            "my_remaining_skills": ', '.join(self.vacancy.compared_skills["my_remaining_skills"]),
            "ready_to_study_skills": ', '.join(self.vacancy.compared_skills["ready_to_study"]),
            "created_ai_text": created_ai_text,
            "this_vacancy": self.vacancy,
        }
        self.text = get_letter_from_base_template(dict_to_send_to_letter_template)
        print("Конец обработки сопроводительного письма")

    def save_to_file(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(self.text)
            file.write(f"\n\n{self.vacancy.company_name}\n")
            file.write(f"{self.vacancy.position}\n{self.vacancy.url}\n{self.vacancy.salary} ")
            print(f"Сопроводительное письмо сохранено в {self.file_path}")

    def run_local_cover_letter(self):
        text_editor_path = DIR_SETTINGS["TEXT_EDITOR_PATH"]
        try:
            print(f"Открываю... {self.file_path}")
            subprocess.run([text_editor_path, self.file_path], shell=True, timeout=1)
        except Exception:
            pass


if __name__ == '__main__':
    my_resume = MyResume()
    vacancy = Vacancy(os.getenv("MAIN_VACATION_URL"))
    vacancy.cover_letter.save_to_file()
    if BASE_SETTINGS["OPEN_LOCAL_COVER_LETTER"]:
        try:
            vacancy.cover_letter.run_local_cover_letter()
        except Exception as e:
            print(e)
