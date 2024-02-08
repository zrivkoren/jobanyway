import asyncio


class AIProvider:
    def __init__(self, text_to_generate: str):
        self._text_to_generate = text_to_generate
        self._results_texts = []
        self._ai_provider_list = [G4FProvider, ]

    def check_all_providers(self):
        for provider in self._ai_provider_list:
            result = provider.get_ai_text(self)
            self.results = result

    @property
    def results(self):
        return self._results_texts

    @results.setter
    def results(self, value):
        self._results_texts.append(value)

    async def get_ai_text(self):
        input_text = self._text_to_generate
        return "Здесь какой то текст"


class G4FProvider(AIProvider):
    async def get_ai_text(self):
        input_text = self._text_to_generate
        # result = await
        return "Здесь какой то текст"
