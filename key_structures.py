import pandas as pd
import sys
import re
import json
from typing import Optional

class answers_dict:
    def __init__(self, filename : str):
        data = pd.read_excel(filename)
        self.__data = dict()
        for _, row in data.iterrows():
            if row["question"] not in self.__data:
                self.__data[row["question"]] = dict()
            self.__data[row["question"]][row["answer"]] = row["key_value"]        
    
    def get_answer_key_value(self, question : str, answer: str):
        return self.__data[question][answer]
    
class names_dict:
    def __init__(self, filename : str):
        data = pd.read_excel(filename)
        self.__data = dict()
        for _, row in data.iterrows():
            self.__data[self.__standartize_str(row["name"])] = row["name"]        
    
    def get_name(self, name : str) -> Optional[str] :
        candidates = set()
        for i in self.__data.keys():
            if i.issuperset(self.__standartize_str(name)):
                candidates.add(self.__data[i])
        if len(candidates) != 1:
            return None
        else:
            return list(candidates)[0]
    
    def __standartize_str (self, name : str) ->  frozenset:
        name = name.strip()
        name = re.split('[ \t,;\:\-\.\!\?]+', name)
        name = [i.lower() for i in name]
        return frozenset(name)
        
class collector:
    class number_collector:
        def __init__(self):
            self.sum = 0
            self.counter = 0
        
        def add_info(self, value):
            self.sum += value
            self.counter += 1

    class free_collector:
        def __init__(self):
            self.feedback = []

        def add_info(self, value):
            self.feedback.append(value)

    class select_collector:
        def __init__(self, question : str, answers : answers_dict):
            self.answers = dict()
            for _, key_value in answers[question].items():
                self.answers[key_value] = 0
            self.counter = 0

        def add_info(self, value):
            self.answers[value] += 1
            self.counter += 1

    def __init__(self, survey_structure, group_name : str, names_dict : names_dict, answers_dict :answers_dict):
        self.__group_structure = survey_structure["groups"][group_name]
        
        self.__names = dict()
        word = "as"
        if word == "name":
            pass

    def process_row(self, row : pd.Series):
        pass   

    def print_groups(self):
        data = pd.read_excel("resources\\data.xlsx")
        for group, indexes in self.__survey_structure["groups"].items():
            print(data[data.columns[indexes]])

    #def (self):


with open("resources\\survey_structure.json", "r", encoding = "utf-8") as tmp_input:
        survey_structure = json.load(tmp_input)

sys.stdout.reconfigure(encoding = 'utf-8')
in_str = "ахматова екатерина"
x = answers_dict("resources\\keys.xlsx")
y = names_dict("resources\\names.xlsx")
z= collector(y,x)
z.print_groups()
print(x.get_answer_key_value("6. Способствует ли руководитель вашему развитию?","Скорее да, периодически ведется работа в этом направлении"))
print(x.get_answer_key_value("12. Как вы оцениваете эмоциональный вклад руководителя?","Общая демотивация"))
print(y.get_name(in_str))

