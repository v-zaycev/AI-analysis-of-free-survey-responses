from common.generate_text import summarize, async_summarize

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