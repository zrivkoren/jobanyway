import g4f


def get_inf(text):
    print("Начало генерации текста ИИ")
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"""
        Есть вакансия, в которой следующий текст описывает компанию, напиши якобы ОТ МОЕГО ИМЕНИ почему я хочу быть разработчиком именно в данной компании. Результат должен быть в 2 - 3 предложения, без пафоса, как будто писал реальный человек. Начни с 'Мне интересна ваша компания потому что ....'. В тексте должно быть что то близкое к 'что подразумевает рост меня как разработчика в ходе работы над реально полезным продуктом.' Предложи два(2) варианта
Текст: {text}
        """}],
    )
    print("Конец генерации текста ИИ")
    return response


if __name__ == '__main__':
    text = """
Мы строим большую продуктовую компанию, в которой уже развиваются множество продуктов. Все это для того, чтобы ежедневно 300 000 наших клиентов по всему миру радовались, получая вовремя и в нужном качестве свои важные и ценные посылки.
Мы сейчас расширяем нашу команду Low-code продуктов и ищем 2х специалистов, кто поможет нам развивать продукт WMS (система управление складом). Он уже запущен и успешно работает. Сейчас стадия активной разработки. Основной стек - Low-code(Python) и FastAPI.
Предстоит: Участвовать в разработке продуктов, построенных с применением low-code-технологий (а именно WMS системы, но также и других) Поддерживать и оптимизировать текущие решения Интегрировать продукт с внешними и внутренними сервисами
Проводить оптимизацию кода, также запросов к БД Писать тесты, участвовать код-ревью Взаимодействовать с разработчиками, QA, PM , UI/UX дизайнерами, аналитиками и т.д.
"""

    print(get_inf(text=text))