import copy
import pandas as pd
from typing import Optional, Union
from common.names_dict import NamesDict
from common.survey_structure import SurveyStructure
from common.mini_collectors.number_collector import NumberCollector 

class DataCollector:
    def __init__(self, data_path : str, structure_path : str, names_path : str):
        """Конструктор класса
        Parameters:
            data_path: .xlsx файл с результатами опроса
            structure_path: .json файл с описанием опроса
            names_path: .xlsx файл со списком рассматриваемых имён руководителей
        """
        self.__survey_data = pd.read_excel(data_path)
        self.__names = NamesDict(names_path)
        self.survey_structure = SurveyStructure(structure_path)
        self.__person_template = self.survey_structure.create_person_template()
        self.__collector = dict()

    def collect(self) -> tuple:
        """Метод выполняющий сбор статистики для различных руководителей\n
        Returns:
            tuple: (число неидентифицированных имён, число всех непустых имён)
        """
        names_counter = 0
        unaccepted_names_counter = 0
        questions = self.survey_structure["fields"]
        for row_index, row in self.__survey_data.iterrows():
            for _, columns in self.survey_structure["groups"].items():
                group_structure = self.survey_structure.create_group_structure(columns)

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
                
                if (raw_name != self.survey_structure["empty_value"]):
                    names_counter += 1
                else:
                    continue

                names = self.__names.get_names(raw_name)
                
                if len(names) != 1:
                    print(f"row {row_index}: \"{name_column_question}\"\n  {raw_name}: {names}")
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

    def contains(self, name : str) -> Optional[str]:
        """Метод проверяет, есть ли переданное имя среди собранных данных
        Parameters:
            name (str): проверяемое имя
        Returns:
            Optional (str): если имени соответствует единственная запись, то возвращается имя в той форме,
            в которой оно записано в сборщике, в противном случае возращается None"""
        name = self.__names.get_names(name)
        if len(name) != 1:
            return None
        name = name[0]
        if name not in self.__collector:
            return None
        return name

    def create_report_df(self, group_name : Optional[str] = None) -> pd.DataFrame:
        """Метод возвращающий pandas DataFrame, с набором статистик для каждого вопроса для каждого руководителя
        Args:
            group_name (Optional[str]): тип руководства
        Returns:
            Pandas.DataFrame: Заголовками являются формулировки вопросов/выходные интерпретации + постфикс для соответствующей статистики.
            Набор статистик зависит от типа вопроса.
        """
        if group_name is None:
            columns_numbers = sorted(self.survey_structure["fields"].keys())
        elif group_name in self.survey_structure["groups"]:
            columns_numbers = sorted(self.survey_structure["groups"][group_name])
        else:
            return None
        
        columns_names = ["Имя"]
        for index in columns_numbers:
            if index in self.__person_template:
                columns_names.extend(self.__person_template[index][1].get_columns_names(self.__person_template[index][0]))

        if group_name is None:
            for columns_name in self.survey_structure["merge"].keys():
                columns_names.extend(NumberCollector.get_columns_names(columns_name))
        df = pd.DataFrame()

        for name, person_data in self.__collector.items():
            cur_row = [name]
            for index, info in person_data.items():
                if index not in columns_numbers:
                    continue
                cur_row.extend(info[1].get_columns_values())
            if group_name is None:
                for _, merge_columns in self.survey_structure["merge"].items():
                    merge_result = NumberCollector(self.survey_structure["empty_value"])
                    for index in merge_columns:
                        merge_result.__iadd__(self.__collector[name][index][1])
                    cur_row.extend(merge_result.get_columns_values())
            
            if df.empty:
                df = pd.DataFrame(data=[cur_row], columns = columns_names)
            else:
                df = pd.concat([df, pd.DataFrame(data=[cur_row], columns = columns_names)], ignore_index = True)

        return df

    def get_person_report(self, name : str, group_name : Optional[str] =  None) -> Optional[pd.Series]:
        """Метод возвращающий pandas Series, с набором статистик для каждого вопроса\n
        Args:
            name: имя руководителя
            group_name: тип руководства
        Returns:
            Optional[Pandas.Series]: заголовками являются формулировки вопроса/выходные интерпретации + постфикс для соответствующей статистики.
            Набор статистик зависит от типа вопроса.
        """
        name = self.contains(name)
        if name is None:
            return None
            
        if group_name is None:
            columns_numbers = sorted(self.survey_structure["fields"].keys())
        elif group_name in self.survey_structure["groups"]:
            columns_numbers = sorted(self.survey_structure["groups"][group_name])
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
        if group_name is None and not self.survey_structure["merge"]:
            for merge_name, merge_columns in self.survey_structure["merge"].items():
                merge_result = NumberCollector(self.survey_structure["empty_value"])
                for index in merge_columns:
                    merge_result += self.__collector[name][1]
            columns_names.extend(merge_result.get_columns_names(merge_name))
            columns_data.extend(merge_result.get_columns_values())

        return pd.Series(columns_data, index = columns_names)         

    def get_persons_select(self, name : str, group_name : Optional[str] =  None) -> Optional[pd.Series]:
        name = self.contains(name)
        if name is None:
            return None
        
        if group_name is None:
            columns_numbers = sorted([i for i , data in self.survey_structure["fields"].items() if data[0] == "select" ])
        elif group_name in self.survey_structure["groups"]:
            columns_numbers = sorted([i for i in self.survey_structure["groups"][group_name] if (
                self.survey_structure["fields"][i][0] == "select" )])
        else:
            return None
        
        person_data = self.__collector[name]
        columns_names = list()
        columns_data = list()
        for i in columns_numbers:
            pass
        #!!!!!!!!
        return pd.Series(columns_data, index = columns_names)  

    def get_select_vals_for_plot(self, name : str, group_name : str) -> tuple[list, list]:
        """
        Args:
            name (str): имя руководителя
            group_name (str): тип руководства

        Returns:
            tuple: пара списков, где первый содержит интерпретации вопросов, а второй - список из доли положительных и отрицательных ответов"""
        candidates = self.__names.get_names(name)
        if len(candidates) == 1:
            name = candidates[0]
        else:
            return None
        
        if group_name not in self.survey_structure["groups"]:
            return None

        group_structure = self.survey_structure.create_group_structure(self.survey_structure["groups"][group_name])
        names = list()
        vals = list()
        for index in group_structure["select"]:
            names.append(self.__collector[name][index][0])
            positive_pct = round(self.__collector[name][index][1].get_columns_values()[0],2)
            vals.append([positive_pct, round(1 - positive_pct,2)])
        return (names, vals)

    def get_person_ratings(self, name : str) -> list:
        """
        Args:
            name (str): имя руководителя

        Returns:
            list: список пар (средняя оценка, число оценок) для каждого столбца типа number"""
        candidates = self.__names.get_names(name)
        if len(candidates) != 1:
            return None
        name = candidates[0]
        ratings = list()
        for question_nmb, data in self.__collector[name].items():
            if type(data[1]) == NumberCollector:
                ratings.append(data[1].get_columns_values())
        return ratings

    def get_average_rating(self, columns : Union[int, list[int]]):
        """Метод считает среднюю оценку среди всех респондентов по вопросам с указанными номерами
        Args:
            columns (int | list[int]): набор вопросов
        Returns:
            dict | float | None: значение или набор значений для соответствующих формулировок вопросов"""
        if type(columns) == int:
            mini_collector = NumberCollector(self.survey_structure["empty_value"])
            for _, stats in self.__collector.items():
                mini_collector.__iadd__(stats[columns][1])
            return None if mini_collector.counter == 0 else mini_collector.sum /mini_collector.counter
        else:
            overall_collector = NumberCollector(self.survey_structure["empty_value"])
            result = dict()
            for column in columns:
                mini_collector = NumberCollector(self.survey_structure["empty_value"])
                for _, stats in self.__collector.items():
                    mini_collector.__iadd__(stats[column][1])
                overall_collector.__iadd__(mini_collector)           
                result[self.__person_template[column][0]] = (None if mini_collector.counter ==0 else mini_collector.sum /mini_collector.counter)
            result["Overall"] = (None if overall_collector.counter ==0 else overall_collector.sum /overall_collector.counter)
            return result
    
    def get_top_one_level(self, threshold : int = 1, top : int = 5) -> pd.DataFrame:
        """Метод формирует рейтинг руководителей только с прямыми подчинёнными
        Args:
            threshold (int): минимальное число оценок для учёта в рейтинге
            top (int): число руководителей в топе
        Returns:
            Pandas.DataFrame: таблица со столбцами \"name\", \"rating\""""
        names = list()
        ratings = list()
        for name, data in self.__collector.items():
            if data[4][1].counter >= threshold and data[11][1].counter == 0 and data[20][1].counter == 0:
                names.append(name)
                ratings.append(data[4][1].sum / data[4][1].counter)
        return pd.DataFrame(data = {"name" : names, "rating" : ratings}).sort_values(by = ["rating"],ascending = False).reset_index(drop = True)[:top]        
    
    def get_top_several_levels(self, threshold : int = 1, top : int = 5) -> dict:
        """Метод формирует рейтинг руководителей только с несколькими уровнями подчинения
        Parameters:
            threshold (int): минимальное число оценок для учёта в рейтинге
            top (int): число руководителей в топе
        Returns:
            dict: словарь с ключами \"direct\", \"non direct\" и соответствующими pandas DataFrame
            со столбцами \"name\", \"rating direct\" или \"rating non direct\""""
        names = list()
        ratings_direct = list()
        ratings_non_direct = list()
        for name, data in self.__collector.items():
            if data[4][1].counter >= threshold and (data[11][1].counter >= threshold or data[20][1].counter >= threshold):
                names.append(name)
                ratings_direct.append(data[4][1].sum / data[4][1].counter)
                ratings_non_direct.append((data[11][1].sum + data[20][1].sum)  / (data[11][1].counter + data[20][1].counter))
        result =  pd.DataFrame(data = {"name" : names, "rating direct" : ratings_direct, "rating non direct" : ratings_non_direct})
        return {"direct" : result.drop(columns=["rating non direct"]).sort_values(by = ["rating direct"],ascending = False).reset_index(drop = True)[:top],
                "non direct" : result.drop(columns=["rating direct"]).sort_values(by = ["rating non direct"],ascending = False).reset_index(drop = True)[:top]}

    def get_areas_of_growth(self) -> dict:
        """Метод формирует списки зон роста по уровням подчинения
        Returns:
            dict: словарь с ключами по типам подчинения и соответствующими pandas DataFrame
            со столбцами \"question\", \"rating\", \"votes\""""
        overall_collector = copy.deepcopy(self.__person_template)
        fields  = self.survey_structure["fields"]
        for _, data in self.__collector.items():
            for i, collector in data.items():
                if fields[i][0] == "select":
                    overall_collector[i][1].__iadd__(collector[1])
        result = dict()
        for group_name, group_columns in self.survey_structure["groups"].items():
            group_structure = self.survey_structure.create_group_structure(group_columns)
            questions = list()
            ratings = list()
            votes = list()
            for i in group_structure["select"]:
                questions.append(overall_collector[i][0])
                tmp = overall_collector[i][1].get_columns_values()
                ratings.append(tmp[0])
                votes.append(tmp[1])
            
            df = pd.DataFrame(data = {"question": questions, "rating": ratings, "votes": votes})
            df = df.sort_values(by=["rating"]).reset_index(drop = True)
            result[group_name] = df
        return result
