from openai import (
    APIConnectionError,
    APIError,
    AsyncOpenAI,
    RateLimitError,
)

from app.config import settings


class LLMService:

    def __init__(self):

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.llm_model

    async def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:

        prompt = f"""
Answer the user's question using only the provided context.

If the answer cannot be found in the context,
say that you do not have enough information.

Context:
{context}

Question:
{question}
"""

        try:

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful document "
                            "question-answering assistant."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
            )

            return response.choices[0].message.content or ""

        except RateLimitError as exc:

            raise RuntimeError(
                "LLM service quota has been exhausted. "
                "Please check the OpenAI API billing or quota."
            ) from exc

        except APIConnectionError as exc:

            raise RuntimeError(
                "Unable to connect to the LLM service."
            ) from exc

        except APIError as exc:

            raise RuntimeError(
                "The LLM service returned an API error."
            ) from exc


llm_service = LLMService()