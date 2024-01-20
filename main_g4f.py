import g4f
import asyncio
from main import logger

from templates import get_text_from_template

g4f.debug.logging = False
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
        if response:
            results.append({provider.__name__: response})
            logger.debug(f"Результат провайдера <{provider.__name__}> добавлен в список")
    except Exception as e:
        logger.trace(f"Провайдер <{provider.__name__}> отказал: {str(e)}")


async def run_async_all(text_input):
    logger.info("Началась асинхронная генерация текста ИИ..")
    calls = [
        run_provider(provider, text_input) for provider in _providers
    ]
    await asyncio.gather(*calls)
    logger.info("Конец генерации текста ИИ")
    return results
