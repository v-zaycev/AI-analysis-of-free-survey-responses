import pandas as pd
import re

class names_dict:
    def __init__(self, filename : str):
        data = pd.read_excel(filename)
        self.__data = dict()
        for _, row in data.iterrows():
            self.__data[self.__standartize_str(row["name"])] = row["name"]        
    
    def get_names(self, name : str) -> list :
        candidates = set()
        for i in self.__data.keys():
            if i.issuperset(self.__standartize_str(name)):
                candidates.add(self.__data[i])
        return list(candidates)
    
    def __standartize_str (self, name : str) ->  frozenset:
        name = name.strip()
        name = re.split('[ \t,;\:\-\.\!\?]+', name)
        name = [i.lower() for i in name]
        return frozenset(name)

class number_collector:
    def __init__(self, default_value):
        self.default_value = default_value
        self.sum = 0
        self.counter = 0
    
    def add_info(self, value):
        if value != self.default_value:
            self.sum += value
            self.counter += 1

class free_collector:
    def __init__(self, default_value):
        self.default_value = default_value
        self.feedback = []

    def add_info(self, value):
        if value != self.default_value:
            self.feedback.append(value)

class select_collector:
    def __init__(self, default_value, question_info : dict):
        self.default_value = default_value
        self.question_info = question_info
        self.answers = dict()
        if type(question_info[2]) == list:
            for value in question_info[2]:
                self.answers[value] = 0
        elif type(question_info[2]) == dict:
            for _, value in question_info[2].items():
                self.answers[value] = 0
        self.counter = 0

    def add_info(self, answer : str):
        if type(self.question_info[2]) == list:
            if answer in self.answers:
                self.answers[answer] += 1
        elif type(self.question_info[2]) == dict:
            if answer in self.question_info[2]:
                self.answers[self.question_info[2][answer]] += 1
        self.counter += 1