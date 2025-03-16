import pandas as pd
import re
import sys
from generate_text import summarize
from resources import questions, results, level_to_name, level_to_questions
import copy
import asyncio


class Preprocessing:
    def __init__(self, path):
        self.survey_data = pd.read_excel(path)

    def collect(self):
        collector = {}
        for index, row in self.survey_data.iterrows():
            for level in level_to_name.keys():
                name = row[questions[level_to_name[level]]["column_name"]].strip()
                if self.check_input(name) is False:
                    continue
                if name not in collector:
                    collector[name] = copy.deepcopy(results)
                for question_id in level_to_questions[level]:
                    if questions[question_id]["type"] == "select":
                        if row[questions[question_id]["column_name"]] in questions[question_id]["estimate"]:
                            collector[name][question_id]["value"] += questions[question_id]["estimate"][
                                row[questions[question_id]["column_name"]]]
                            collector[name][question_id]["quantity"] += 1
                    elif questions[question_id]["type"] == "free":
                        if self.check_input(row[questions[question_id]["column_name"]]):
                            collector[name][question_id].append(row[questions[question_id]["column_name"]])
                    elif questions[question_id]["type"] == "number":
                        if str(row[questions[question_id]["column_name"]]).isdigit():
                            collector[name][question_id]["value"] += int(
                                row[questions[question_id]["column_name"]])
                            collector[name][question_id]["quantity"] += 1
        return collector

    def check_input(self, text):
        try:
            is_name = re.match("[a-zA-ZА-Яа-яЁё]+", text)
        except TypeError:
            return False
        else:
            if is_name is None:
                return False
            else:
                return True

    def free_responses(self, collector):
        def to_summarize(name, question):
            if len(collector[name][question]) > 0:
                reviews = ""
                for i in range(len(collector[name][question])):
                    reviews += f"{i + 1}: {collector[name][question][i]}\n"
                return asyncio.run(summarize(reviews))

        for name in collector.keys():
            collector[name][8] = to_summarize(name, 8)
            collector[name][14] = to_summarize(name, 14)
            collector[name][22] = to_summarize(name, 22)

        return collector

    def numeric_responses(self, collector):
        for name in collector.keys():
            for question in collector[name].keys():
                if type(collector[name][question]) is dict:
                    if collector[name][question]["quantity"] < 1:
                        collector[name][question] = None
                    else:
                        collector[name][question] = round(collector[name][question]["value"] / collector[name][question]["quantity"], 1)

        return collector

    def to_csv(self, collector):
        return pd.DataFrame.from_dict(collector, orient='index')


if __name__ == '__main__':
    path = input("Please, enter path to xlsx file:")
    Prep = Preprocessing(path)
    collector = Prep.collect()
    collector = Prep.free_responses(collector)
    collector = Prep.numeric_responses(collector)
    Prep.to_csv(collector).to_csv("ready_quiz.csv")
