# !/usr/bin/env python3

from __future__ import annotations
from yandex_cloud_ml_sdk import AsyncYCloudML
from authentication import FOLDER_ID, AUTH


async def summarize(reviews) -> str:
    sdk = AsyncYCloudML(folder_id=FOLDER_ID, auth=AUTH)
    sdk.setup_default_logging()

    model = sdk.models.completions('yandexgpt-lite')

    messages = [
        {
            "role": "system",
            "text": "Проанализируй отзывы о руководителе, пронумерованные с 1, и составь краткую обратную связь по пунктам. Первый пункт должен быть самым актуальным и важным. Вывод должен быть кратким.",
        },
        {
            "role": "user",
            "text": reviews,
        },
    ]

    result = await model.configure(
        temperature=0.7
    ).run(messages)

    return result[0].text

# if __name__ == '__main__':
#     print(asyncio.run(summarize("how to calculate the Hirsch index in O(N)")))
