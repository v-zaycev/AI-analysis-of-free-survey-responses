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
            "text": "Проанализируй отзывы о руководителе и составь краткую обратную связь. Результат должен быть оформлен по пунктам, каждый из которых отражает ключевой аспект из отзывов.",
        },
        {
            "role": "user",
            "text": reviews,
        },
    ]

    result = await model.configure(
        temperature=0.5
    ).run(messages)

    return result[0].text
