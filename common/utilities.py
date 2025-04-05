import pandas as pd
import re
import json
from generate_text import summarize, async_summarize

class names_dict:
    def __init__(self, filename : str):
        data = pd.read_excel(filename)
        self.__data = dict()
        for _, row in data.iterrows():
            self.__data[self.__standartize_str(row["name"])] = row["name"]
    
    def get_names(self, name : str) -> list :
        candidates = list()
        for i in self.__data.keys():
            if i.issuperset(self.__standartize_str(name)):
                candidates.append(self.__data[i])
        if len(candidates) == 0:
            self.__check_initials(name, candidates)
        return candidates
    
    def __standartize_str (self, name : str) ->  frozenset:
        name = name.strip().replace("ё","е")
        name = re.split('[ \t,;\:\-\.\!\?]+', name)
        name = [i.lower() for i in name if i != ""]
        return frozenset(name)
    
    def __check_initials(self, name: str, candidates : list):
        name = name.strip()
        chars_array = list(name)
        i = 0
        while i < len(chars_array) - 1:
            alpha = chars_array[i].isalpha() and chars_array[i+1].isalpha()
            upper = chars_array[i].isupper() and chars_array[i+1].isupper()
            if alpha and upper:
                chars_array.insert(i+1,'.')
            i += 1
        
        name = re.split('[ \t,;\:\-\.\!\?]+', "".join(chars_array))
        name = [i.lower() for i in name if i != ""]
        if len(name) != 2 and len(name) != 3:
            return 
        
        if len(name) == 3:
            if len(name[0]) == 1:
                first = name[0]
                middle = name[1]
                last = name[2]
            elif len(name[2]) == 1:
                first = name[1]
                middle = name[2]
                last = name[0]
            else:
                return 
        if len(name) == 2:
            if len(name[0]) == 1:
                first = name[0]
                middle = None
                last = name[2]
            elif len(name[1]) == 1:
                first = name[1]
                middle = None
                last = name[0]
            else:
                return 
        
        for _, candidate_str in self.__data.items():
            elements = re.split('[ \t,;\:\-\.\!\?]+', candidate_str)
            elements = [i.lower() for i in elements]
            if last != elements[0]: continue
            if len(elements) > 1 and not elements[1].startswith(first): continue
            if len(elements) > 2 and middle != None and not elements[2].startswith(middle): continue
            candidates.append(candidate_str)
        



class number_collector:
    def __init__(self, default_value):
        self.default_value = default_value
        self.sum = 0
        self.counter = 0
    
    def add_info(self, value):
        if value is not None and value != self.default_value:
            self.sum += value
            self.counter += 1

    def get_columns_names(self, field_name :  str) -> list:
        return [ field_name + "_avg", field_name + "_count"]
    
    def get_columns_values(self) -> list:
        return [0 if self.counter == 0 else self.sum / self.counter, self.counter]

    def __iadd__(self, other):
        self.sum += other.sum
        self.counter += other.counter

class free_collector:
    def __init__(self, default_value):
        self.default_value = default_value
        self.feedback = []

    def add_info(self, value):
        if value is not None and value != self.default_value and str(value).strip() != "":
            self.feedback.append(str(value))

    def get_columns_names(self, field_name :  str) -> list:
        return [field_name + "_feedback", field_name + "_count"]
    
    def get_columns_values(self) -> list:
        if len(self.feedback) != 0:
            return [async_summarize("\n\n".join(self.feedback)), len(self.feedback)]
        else:
            return [None, 0]
    
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

    def add_info(self, answer):
        if type(self.question_info[2]) == list:
            if answer in self.answers:
                self.answers[answer] += 1
        elif type(self.question_info[2]) == dict:
            if answer in self.question_info[2]:
                self.answers[self.question_info[2][answer]] += 1
        self.counter += 1
    
    def get_columns_names(self, field_name :  str) -> list:
        return [ field_name + "_positive_pct", field_name + "_count"]
    
    def get_columns_values(self) -> list:
        if 1 in self.answers:
            return [0 if self.counter == 0 else self.answers[1] / self.counter,  self.counter]
        else:
            return [0, 0]
        
def read_survey_structure(file_name : str) -> dict:
    with open(file_name, "r", encoding = "utf-8") as tmp_input:
        survey_structure = json.load(tmp_input)    
        new_fields = dict()
        for key, value in survey_structure["fields"].items():
            new_fields[int(key)] = value
        survey_structure["fields"] = new_fields
        new_output_headers = dict()
        for key, value in survey_structure["output headers"].items():
            new_output_headers[int(key)] = value
        survey_structure["output headers"] = new_output_headers
    return survey_structure