import os


def get_letter_from_base_template(content: dict) -> str:
    resume_name = os.getenv('RESUME_NAME')
    resume_email = os.getenv('MY_EMAIL')
    vacancy_position = content['this_vacancy'].position
    matching_skills = content['matching_skills']
    ready_to_study_skills = content['ready_to_study_skills']
    remaining_skills = content['my_remaining_skills']
    created_ai_text = content['created_ai_text']
    result = f"""Привет!\nМеня зовут {resume_name}, 
Ваша вакансия {vacancy_position} мне подходит.\n    
Я бывалый разраб в {matching_skills}.
Дуб дубом в {ready_to_study_skills}.\n
Но зато умеют вот это {remaining_skills}\n\n
Вот такой чудесный текст сгенерировал ИИ:\n
{created_ai_text}\n\n
Моя почта: {resume_email}\n Всего доброго, хорошего настроения и здоровья!\n  
    """
    return result


def get_text_from_template(text: str) -> str:
    return f"""Напиши ка мне нейросеточка текст на основе вот этого {text}
Да покрепче! Чтобы прям ууух!
    """
