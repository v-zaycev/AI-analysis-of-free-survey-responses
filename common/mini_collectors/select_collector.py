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