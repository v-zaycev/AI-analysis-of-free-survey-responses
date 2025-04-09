from yandex_cloud_ml_sdk import YCloudML, AsyncYCloudML
import json
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
            "text": """Тебе даётся список отзывов о руководителе. Убери из них эмоциональный окрас и составь краткую обратную связь содержащую предложения по улучшению рабочего процесса.
                       В результате представь нумерованный список, где пункты отражают различные ключевые моменты. Ответ должен содержать не более трёх пунктов.
                       Не больше 35 слов."""
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
            "text": """Тебе даётся список отзывов о руководителе. Убери из них эмоциональный окрас и составь краткую обратную связь содержащую предложения по улучшению рабочего процесса.
                       В результате представь нумерованный список, где пункты отражают различные ключевые моменты. Ответ должен содержать не более трёх пунктов."""
        },
        {
            "role": "user",
            "text": reviews,
        },
    ]
    async def get_msg():
          return await model.run(messages)
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(get_msg())
    return result[0].text

def get_name(name : str) -> str:
    with open("resources\\auth.json", "r") as tmp_input:
            auth_info = json.load(tmp_input)
    sdk = YCloudML(folder_id=auth_info["directory-id"], auth=auth_info["api-key"])
    sdk.setup_default_logging()

    model = sdk.models.completions('yandexgpt-lite')

    messages = [
            {
                "role": "system",
                "text": "Тебе даётся разговорный вариант имени. Верни полное имя. Если имя может быть как женским так и мужским, верни оба. Верни только само полное имя. Одним словом."
            },
            {
                "role": "user",
                "text": name,
            },
        ]

    result = (model.configure(temperature=0.0).run(messages))

    return result[0].text

def async_get_name(name : str) -> str:
    with open("resources\\auth.json", "r") as tmp_input:
            auth_info = json.load(tmp_input)
    sdk = AsyncYCloudML(folder_id=auth_info["directory-id"], auth=auth_info["api-key"])
    sdk.setup_default_logging()

    model = sdk.models.completions('yandexgpt-lite').configure(temperature=0.0)

    messages = [
        {
            "role": "system",
            "text": "Тебе даётся разговорный вариант имени. Верни полное имя. Если имя может быть как женским так и мужским, верни оба и раздели их '/'. Верни только само полное имя. Одним словом."
        },
        {
            "role": "user",
            "text": name,
        },
    ]
    async def get_msg():
          return await model.run(messages)
    event_loop = asyncio.get_event_loop()
    result = event_loop.run_until_complete(get_msg())
    return result[0].text
