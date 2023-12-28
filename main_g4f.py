import g4f
import asyncio

from templates import get_text_from_template

g4f.debug.logging = True
_providers = [
    g4f.Provider.Aichat,
    g4f.Provider.ChatBase,
    g4f.Provider.Vercel,
    g4f.Provider.You,
    g4f.Provider.ChatgptAi,
    # g4f.Provider.Bing,
    # g4f.Provider.GptGo,
    # g4f.Provider.Bard,
    # g4f.Provider.Yqcloud,
    # g4f.Provider.OpenaiChat,
]

results = []


async def run_provider(provider: g4f.Provider.BaseProvider, text: str):
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": text}],
            provider=provider,
        )
        results.append({provider.__name__: response})
    except Exception as e:
        print(provider.__name__, str(e))


async def run_async_all(text_input):
    text_value = get_text_from_template(text_input)
    print(f"{text_value}")
    print("Начало асинхронной генерации текста ИИ...")
    calls = [
        run_provider(provider, text_value) for provider in _providers
    ]
    await asyncio.gather(*calls)
    print("Конец генерации текста ИИ")
    return results


def get_inf(text_input):
    print("Начало генерации текста ИИ...")
    text_value = get_text_from_template(text_input)
    response = None
    print(f"{text_value}")
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text_value}],
        )
        print("Конец генерации текста ИИ")
        if not response:
            response = text_value
    except Exception as e:
        print("--Возникла ошибка во время генерации текста-- Текст для ручной генерации сформирован.\n")
        print(e)
        response = text_value
    return response
