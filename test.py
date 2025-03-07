import requests
import json
import sys

class request_gpt:        
    def __init__(self, account_info_file : str):
        with open("auth.json", "r") as tmp_input:
            auth_info = json.load(tmp_input)
        self.__api_key = auth_info["api-key"]
        self.__direcrory_id = auth_info["directory-id"]
        self.__prompt = {
            "modelUri": "gpt://"+ self.__direcrory_id +"/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.1,
                "maxTokens": "50"
            },
            "messages": [
                {
                    "role": "system",
                    "text": ""
                },
                {
                    "role": "user",
                    "text": ""
                }
            ]
        }
    
    def __call__(self, reques_settings : str, reques_text : str) -> str:
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Api-Key " + self.__api_key
        }
        self.__prompt["messages"][0]["text"] = reques_settings
        self.__prompt["messages"][1]["text"] = reques_text
        response = requests.post(url, headers=headers, json=self.__prompt)
        result = response.text
        f = open("output.txt", "w")
        f.write(result)
        f.close()
        result_json = json.loads(result)
        sys.stdout.reconfigure(encoding='utf-8')
        print(result_json['result']['alternatives'][0]['message']['text'])
        return result


auth_info = "auth.json"
reques_settings = "Ты ассистент дроид, способный помочь в галактических приключениях."
reques_text = "Привет, Дроид! Мне нужна твоя помощь, чтобы узнать больше о Силе. Как я могу научиться ее использовать?"

request = request_gpt(auth_info)
request(reques_settings, reques_text)