import json
import copy
import asyncio
import pandas as pd
#from generate_text import summarize
from resources import questions_data, empty_collector, levels, full_names, report_data
#from docx import Document
#from docx import Inches
#import plotly.graph_objects as go
from utilities import names_dict, select_collector, number_collector, free_collector

class Preprocessing:
    def __init__(self, data_path : str, structure_path : str, names_path : str):
        self.__survey_data = pd.read_excel(data_path)
        self.__names = names_dict(names_path)
        with open(structure_path, "r", encoding = "utf-8") as tmp_input:
            self.__survey_structure = json.load(tmp_input)    
            new_fields = dict()
            for key, value in self.__survey_structure["fields"].items():
                new_fields[int(key)] = value
            self.__survey_structure["fields"] = new_fields
            new_output_headers = dict()
            for key, value in self.__survey_structure["output headers"].items():
                new_output_headers[int(key)] = value
            self.__survey_structure["output headers"] = new_output_headers

        self.__questions_to_indexes = dict()
        for key, value in self.__survey_structure["fields"].items():
                self.__questions_to_indexes[key] = value
        self.__create_person_template()
        self.__collector = dict()

    def collect(self):
        questions = self.__survey_structure["fields"]
        for _, row in self.__survey_data.iterrows():
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
                if len(names) != 1:
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

    def create_report_df(self, group_name : str):
        if group_name is None:
            pass
        elif group_name in self.__survey_structure["groups"]:
            columns_numbers = sorted(self.__survey_structure["groups"][group_name])
            columns_names = ["Имя"]
            for index in columns_numbers:
                if index in self.__survey_structure["output headers"]:
                    columns_names.append(self.__survey_structure["output headers"][index])
                elif index in self.__person_template:
                    columns_names.append(self.__person_template[index][0])
            df = pd.DataFrame(columns=columns_names)

            for name, person_data in self.__collector.items():
                cur_row = [name]
                for index, info in person_data.items():
                    if index not in columns_numbers:
                        continue
                    if type(info[1]) == select_collector:
                        cur_row.append("" if info[1].counter == 0 else info[1].answers[1] / info[1].counter)
                    elif type(info[1]) == number_collector:
                        cur_row.append("" if info[1].counter == 0 else info[1].sum / info[1].counter)
                    elif type(info[1]) == free_collector:
                        cur_row.append("\n".join(info[1].feedback))
                df = pd.concat([df, pd.DataFrame(data=[cur_row], columns=columns_names)], ignore_index=True)
            return df
        else:
            pass
            
        
    

    # def free_responses(self, collector):
    #     def to_summarize(name, question):
    #         if len(collector[name][question]) > 0:
    #             reviews = ""
    #             for i in range(len(collector[name][question])):
    #                 reviews += f"{i + 1}: {collector[name][question][i]}\n"
    #             return asyncio.run(summarize(reviews))

    #     for name in collector.keys():
    #         collector[name][8] = to_summarize(name, 8)
    #         collector[name][14] = to_summarize(name, 14)
    #         collector[name][22] = to_summarize(name, 22)

    #     return collector

    # def numeric_responses(self, collector):
    #     for name in collector.keys():
    #         for question in collector[name].keys():
    #             if type(collector[name][question]) is dict:
    #                 if collector[name][question]["quantity"] < 1:
    #                     collector[name][question] = None
    #                 else:
    #                     collector[name][question] = round(collector[name][question]["value"] / collector[name][question]["quantity"], 1)

    #     return collector

    # def to_csv(self, filename):
    #     pd.DataFrame.from_dict(self.__collector, orient='index').to_csv(filename)

    # def get_mean(self, collector):
    #     counter = 0
    #     s = 0
    #     for name in collector.keys():
    #         if collector[name][4] is not None:
    #             s += collector[name][4]
    #             counter += 1
    #         if collector[name][11] is not None:
    #             s += collector[name][11]
    #             counter += 1
    #         if collector[name][20] is not None:
    #             s += collector[name][20]
    #             counter += 1
    #     return round(s / counter, 1)

    # def to_report(self, collector):
    #     for name in collector.keys():
    #         document = Document()

    #         if name in full_names:
    #             fn = full_names[name]
    #         else:
    #             fn = ' '.join(map(lambda x: x.capitalize(), list(name)))

    #         document.add_heading(fn, 0)

    #         document.add_paragraph(f"Cредний урочень оценок: {self.get_mean(collector)}")
    #         for level in levels:
    #             graph = {"x": [], "y": []}
    #             document.add_paragraph(f"Уровень подчинения: {level}", style='Intense Quote')
    #             for question in sorted(list(levels[level]["relevant_questions"])):
    #                 if questions_data[question]["type"] == "number":
    #                     if collector[name][question] is not None:
    #                         document.add_paragraph(f"Средняя оценка по уровню: {collector[name][question]}")
    #                     else:
    #                         document.add_paragraph("Недостаточно оценок")
    #                 elif questions_data[question]["type"] == "select":
    #                     if collector[name][question] is not None:
    #                         graph["x"].append(collector[name][question])
    #                         graph["y"].append(report_data[question])
    #                 else:
    #                     if collector[name][question] is not None:
    #                         document.add_paragraph(f"Cуммаризированные отзывы с свободным ответом: {collector[name][question]}")
    #                     else:
    #                         document.add_paragraph("Недостаточно отзывов с свободным ответом")

    #             fig = go.Figure(go.Bar(
    #                 x=graph["x"],
    #                 y=graph["y"],
    #                 orientation='h'))
    #             fig.write_image("fig.png")
    #             document.add_picture("fig.png", width=Inches(8))

    #             document.add_page_break()
    #         document.save(f'{fn}.docx')

    def __create_person_template(self):
        self.__person_template = dict()
        for number, info in self.__survey_structure["fields"].items():
            if info[0] == "number":
                self.__person_template[number] = [info[1], number_collector("-")] 
            elif info[0] == "select":
                self.__person_template[number] = [info[1], select_collector("-", info)] 
            elif info[0] == "free":
                self.__person_template[number] = [info[1], free_collector("-")]
    
    def __create_group_structure(self, columns : list) -> dict:
        group_structure = dict()
        for index in columns:
            if self.__survey_structure["fields"][index][0] not in group_structure:
                group_structure[self.__survey_structure["fields"][index][0]] = [index]
            else:
                group_structure[self.__survey_structure["fields"][index][0]].append(index)
        return group_structure

if __name__ == '__main__':
    data_path = "data.xlsx"
    structure_path = "resources\\survey_structure.json"
    names_path = "resources\\names.xlsx"
    #path = input("Please, enter path to xlsx file:")
    Prep = Preprocessing(data_path, structure_path, names_path)
    Prep.collect()
    Prep.create_report_df("Непосредственный руководитель").to_excel("output.xlsx", index=False)
#    collector = prep.collect()
#    prep.to_report(collector)
#    print(collector)


