import g4f
from templates import get_text_from_template

g4f.debug.logging = True


def get_inf(text_input):
    print("Начало генерации текста ИИ...")
    text_value = get_text_from_template(text_input)
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text_value}],
        )
        print("Конец генерации текста ИИ")
        if not response:
            response = text_value
    except Exception as e:
        print("-Возникла ошибка во время генерации текста-. Текст для ручной генерации сформирован.\n")
        print(e)
        response = text_value
    return response


if __name__ == '__main__':
    text = """  """
    print("Текст запуска генерации текста ИИ из файла main_g4f.py")
    print(get_inf(text))
