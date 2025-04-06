import json
from common.mini_collectors import number_collector
from common.mini_collectors import select_collector
from common.mini_collectors import free_collector

class survey_structure:
    def __init__(self, file_name : str) -> dict:
        with open(file_name, "r", encoding = "utf-8") as tmp_input:
            self.__survey_structure = json.load(tmp_input)    
            new_fields = dict()
            for key, value in self.__survey_structure["fields"].items():
                new_fields[int(key)] = value
            self.__survey_structure["fields"] = new_fields
            new_output_headers = dict()
            for key, value in self.__survey_structure["output headers"].items():
                new_output_headers[int(key)] = value
            self.__survey_structure["output headers"] = new_output_headers
        
    def __getitem__(self, key):
        return self.__survey_structure[key]

    def create_group_structure(self, columns : list) -> dict:
        group_structure = dict()
        for index in columns:
            if self.__survey_structure["fields"][index][0] not in group_structure:
                group_structure[self.__survey_structure["fields"][index][0]] = [index]
            else:
                group_structure[self.__survey_structure["fields"][index][0]].append(index)
        return group_structure
    
    def create_person_template(self):
        person_template = dict()
        for index, info in self.__survey_structure["fields"].items():
            if index in self.__survey_structure["output headers"]:
                field_name = self.__survey_structure["output headers"][index]
            else:
                field_name = info[1]

            if info[0] == "number":
                person_template[index] = [field_name, number_collector(self.__survey_structure["empty_value"])] 
            elif info[0] == "select":
                person_template[index] = [field_name, select_collector(self.__survey_structure["empty_value"], info)] 
            elif info[0] == "free":
                person_template[index] = [field_name, free_collector(self.__survey_structure["empty_value"])]
        return person_template