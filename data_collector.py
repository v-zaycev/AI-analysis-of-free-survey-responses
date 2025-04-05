import json
import copy
import pandas as pd
from typing import Optional
from typing import Union
from utilities import names_dict, select_collector, number_collector, free_collector, read_survey_structure
import sys

class Preprocessing:
    def __init__(self, data_path : str, structure_path : str, names_path : str):
        self.__survey_data = pd.read_excel(data_path)
        self.__names = names_dict(names_path)
        self.__survey_structure = read_survey_structure(structure_path)
        self.__questions_to_indexes = dict()
        
        for key, value in self.__survey_structure["fields"].items():
                self.__questions_to_indexes[key] = value
        self.__create_person_template()
        self.__collector = dict()

    def collect(self) -> tuple:
        names_counter = 0
        unaccepted_names_counter = 0
        questions = self.__survey_structure["fields"]
        for row_index, row in self.__survey_data.iterrows():
            for _, columns in self.__survey_structure["groups"].items():
                group_structure = self.__create_group_structure(columns)

                valid_flag = True
                if "check" in group_structure:
                    for index in group_structure["check"]:
                        question = questions[index][1]
                        answer =  row[question]
                        if answer not in questions[index][2] or questions[index][2][answer] != 1:
                            valid_flag = False
                if not valid_flag:
                    continue

                name_column_number = group_structure["name"][0]
                name_column_question = questions[name_column_number][1]
                raw_name = row[name_column_question].strip()
                names = self.__names.get_names(raw_name)
                
                if (raw_name != self.__survey_structure["empty_value"]):
                    names_counter += 1
                else:
                    continue
                
                if len(names) != 1:
                    print(f"row {row_index}: {name_column_question}\n  {raw_name}: {names}")
                    unaccepted_names_counter += 1
                    continue
                else:
                    name = names[0]

                if name not in self.__collector:
                    self.__collector[name] = copy.deepcopy(self.__person_template)
                group_structure.pop("name", None)
                group_structure.pop("check", None)
                for type in group_structure:
                    for index in group_structure[type]:
                        self.__collector[name][index][1].add_info(row[questions[index][1]])
            
        return (unaccepted_names_counter, names_counter)

    def create_report_df(self, group_name : Optional[str] = None) -> pd.DataFrame:
        if group_name is None:
            columns_numbers = sorted(self.__survey_structure["fields"].keys())
        elif group_name in self.__survey_structure["groups"]:
            columns_numbers = sorted(self.__survey_structure["groups"][group_name])
        else:
            return None
        
        columns_names = ["Имя"]
        for index in columns_numbers:
            if index in self.__person_template:
                columns_names.append(self.__person_template[index][0])
        if group_name is None and not self.__survey_structure["merge"]:
            for columns_name in self.__survey_structure["merge"].keys():
                columns_names.append(columns_name)
        df = pd.DataFrame(columns = columns_names)

        for name, person_data in self.__collector.items():
            cur_row = [name]
            for index, info in person_data.items():
                if index not in columns_numbers:
                    continue
                if type(info[1]) == select_collector:
                    cur_row.append(None if info[1].counter == 0 else info[1].answers[1] / info[1].counter)
                elif type(info[1]) == number_collector:
                    cur_row.append(None if info[1].counter == 0 else info[1].sum / info[1].counter)
                elif type(info[1]) == free_collector:
                    cur_row.extend(info[1].get_columns_values())
            if group_name is None and not self.__survey_structure["merge"]:
                for _, merge_columns in self.__survey_structure["merge"].items():
                    merge_result = number_collector(self.__survey_structure["empty_value"])
                    for index in merge_columns:
                        merge_result += self.__collector[name][1]
                    cur_row.append(None if merge_result.counter == 0 else merge_result.sum / merge_result.counter)
            
            if df.empty:
                df = pd.DataFrame(data=[cur_row], columns = columns_names)
            else:
                df = pd.concat([df, pd.DataFrame(data=[cur_row], columns = columns_names)], ignore_index = True)

        return df

    def get_person_info(self, name : str, group_name : Optional[str] =  None) -> pd.Series:

        candidates = self.__names.get_names(name)
        if len(candidates) == 1:
            name = candidates[0]
        else:
            return None
            
        if group_name is None:
            columns_numbers = sorted(self.__survey_structure["fields"].keys())
        elif group_name in self.__survey_structure["groups"]:
            columns_numbers = sorted(self.__survey_structure["groups"][group_name])
        else:
            return None
        
        person_data = self.__collector[name]
        columns_names = list()
        columns_data = list()
        for index, info in person_data.items():
            if index not in columns_numbers:
                continue
            columns_names.extend(info[1].get_columns_names(info[0]))
            columns_data.extend(info[1].get_columns_values())
        if group_name is None and not self.__survey_structure["merge"]:
            for merge_name, merge_columns in self.__survey_structure["merge"].items():
                merge_result = number_collector(self.__survey_structure["empty_value"])
                for index in merge_columns:
                    merge_result += self.__collector[name][1]
            columns_names.extend(merge_result.get_columns_names(merge_name))
            columns_data.extend(merge_result.get_columns_values())

        return pd.Series(columns_data, index = columns_names)         

    def get_select_vals_for_plot(self, name : str, group_name : str) -> tuple:
        candidates = self.__names.get_names(name)
        if len(candidates) == 1:
            name = candidates[0]
        else:
            return None
        
        if group_name not in self.__survey_structure["groups"]:
            return None

        group_structure = self.__create_group_structure(self.__survey_structure["groups"][group_name])
        names = list()
        vals = list()
        for index in group_structure["select"]:
            names.append(self.__collector[name][index][0])
            positive_pct = round(self.__collector[name][index][1].get_columns_values()[0],2)
            vals.append([positive_pct, round(1 - positive_pct,2)])
        return (names, vals)

    def get_person_ratings(self, name : str) -> list:
        candidates = self.__names.get_names(name)
        if len(candidates) != 1:
            return None
        name = candidates[0]
        ratings = list()
        for question_nmb, data in self.__collector[name].items():
            if type(data[1]) == number_collector:
                ratings.append(data[1].get_columns_values())
        return ratings

    def get_average_rating(self, columns : Union[int, list[int]]):
        if type(columns) == int:
            mini_collector = number_collector(self.__survey_structure["empty_value"])
            for _, stats in self.__collector.items():
                mini_collector.__iadd__(stats[columns][1])
            return None if mini_collector.counter ==0 else mini_collector.sum /mini_collector.counter
        else:
            overall_collector = number_collector(self.__survey_structure["empty_value"])
            mini_collector = number_collector(self.__survey_structure["empty_value"])
            result = dict()
            for column in columns:
                mini_collector = number_collector(self.__survey_structure["empty_value"])
                for _, stats in self.__collector.items():
                    mini_collector.__iadd__(stats[column][1])
                overall_collector.__iadd__(mini_collector)           
                result[self.__person_template[column][0]] = (None if mini_collector.counter ==0 else mini_collector.sum /mini_collector.counter)
            result["Overall"] = (None if overall_collector.counter ==0 else overall_collector.sum /overall_collector.counter)
            return result
    
    def get_top5(self, criterias : Union[int, list[int]]):
        pass
    
    def __create_person_template(self):
        self.__person_template = dict()
        for index, info in self.__survey_structure["fields"].items():
            if index in self.__survey_structure["output headers"]:
                field_name = self.__survey_structure["output headers"][index]
            else:
                field_name = info[1]

            if info[0] == "number":
                self.__person_template[index] = [field_name, number_collector(self.__survey_structure["empty_value"])] 
            elif info[0] == "select":
                self.__person_template[index] = [field_name, select_collector(self.__survey_structure["empty_value"], info)] 
            elif info[0] == "free":
                self.__person_template[index] = [field_name, free_collector(self.__survey_structure["empty_value"])]
    
    def __create_group_structure(self, columns : list) -> dict:
        group_structure = dict()
        for index in columns:
            if self.__survey_structure["fields"][index][0] not in group_structure:
                group_structure[self.__survey_structure["fields"][index][0]] = [index]
            else:
                group_structure[self.__survey_structure["fields"][index][0]].append(index)
        return group_structure
