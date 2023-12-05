import g4f


def get_inf(text):
    print("Начало генерации текста ИИ")
    text_value = f"""
        Есть вакансия, в которой следующий текст описывает компанию, напиши якобы ОТ МОЕГО ИМЕНИ почему я хочу быть разработчиком именно в данной компании. Результат должен быть в 2 - 3 предложения, без пафоса, как будто писал реальный человек. Начни с 'Мне интересна ваша компания потому что ....'. В тексте должно быть что то близкое к 'что подразумевает рост меня как разработчика в ходе работы над реально полезным продуктом.' Предложи два(2) варианта
Текст: {text}
        """
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text_value}],
        )
        print("Конец генерации текста ИИ")
    except Exception as e:
        print("Возникла ошибка во время генерации текста, вот текст для ручной генерации:\n")
        print(e)
        response = text_value
    return response


if __name__ == '__main__':
    text = """  """

    print(get_inf(text=text))
