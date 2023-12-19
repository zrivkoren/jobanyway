import os


def get_letter_from_base_template(content: dict) -> str:
    result = f"""Привет!\nМеня зовут {os.getenv('RESUME_NAME')}, 
Ваша вакансия {content['this_vacancy'].position} мне подходит.\n    
Я бывалый разраб в {content['matching_skills']}.
Дуб дубом в {content['ready_to_study_skills']}.\n
Но зато умеют вот это {content['my_remaining_skills']}\n\n
Моя почта: {os.getenv('MY_EMAIL')}\n Всего доброго, хорошего настроения и здоровья!\n  
    """
    return result


def get_text_from_template(text: str) -> str:
    return f"""Напиши ка мне нейросеточка текст на основе вот этого {text}
Да покречпче! Чтобы прям ууух!
    """
