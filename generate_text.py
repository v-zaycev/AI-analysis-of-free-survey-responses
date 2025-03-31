# !/usr/bin/env python3

from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML, AsyncYCloudML
import json
import sys
import asyncio

def summarize(reviews) -> str:
    with open("resources\\auth.json", "r") as tmp_input:
            auth_info = json.load(tmp_input)
    sdk = YCloudML(folder_id=auth_info["directory-id"], auth=auth_info["api-key"])
    sdk.setup_default_logging()

    model = sdk.models.completions('yandexgpt-lite')

    messages = [
        {
            "role": "system",
            "text": "Тебе даётся список отзывов о руководителе. Убери из них эмоциональный окрас и составь краткую обратную связь содержащую предложения по улучшению рабочего процесса. В результате представь нумерованный список, где пункты отражают различные ключевые моменты. "
        },
        {
            "role": "user",
            "text": reviews,
        },
    ]

    result = (model.configure(temperature=0.2).run(messages))

    return result[0].text

def async_summarize(reviews) -> str:
    with open("resources\\auth.json", "r") as tmp_input:
            auth_info = json.load(tmp_input)
    sdk = AsyncYCloudML(folder_id=auth_info["directory-id"], auth=auth_info["api-key"])
    sdk.setup_default_logging()

    model = sdk.models.completions('yandexgpt-lite').configure(temperature=0.2)

    messages = [
        {
            "role": "system",
            "text": "Тебе даётся список отзывов о руководителе. Убери из них эмоциональный окрас и составь краткую обратную связь содержащую предложения по улучшению рабочего процесса. В результате представь нумерованный список, где пункты отражают различные ключевые моменты. "
        },
        {
            "role": "user",
            "text": reviews,
        },
    ]
    async def get_msg(msg):
          return await model.run(messages)
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(get_msg(messages))
    return result[0].text

# sys.stdout.reconfigure(encoding='utf-8')
# text  = "1. Хаос в управлении, нужно менять подход.\n"+"2. Всё идеально, улучшать нечего.\n"+"3. Учитывать ,при разработке новых процессов,что системы не доработаны,много ручного труда,усложнение процессов Сначала налаживать технические процессы перед введением в работу\n"

# print(async_summarize(text))
