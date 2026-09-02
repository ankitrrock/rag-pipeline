import pytest

from app.llm.service import LLMService


@pytest.mark.asyncio
async def test_llm_service_maps_rate_limit(monkeypatch):
    service = object.__new__(LLMService)
    service.model = "test-model"

    class FakeCompletions:
        async def create(self, **kwargs):
            from openai import RateLimitError
            from httpx import Request, Response

            request = Request("POST", "https://api.openai.com/v1/chat/completions")
            response = Response(429, request=request)
            raise RateLimitError("quota exhausted", response=response, body=None)

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    service.client = FakeClient()

    with pytest.raises(RuntimeError, match="quota has been exhausted"):
        await service.generate_answer("question", "context")
