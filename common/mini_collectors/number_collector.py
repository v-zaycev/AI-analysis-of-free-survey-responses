class NumberCollector:
    def __init__(self, default_value):
        self.default_value = default_value
        self.sum = 0
        self.counter = 0
    
    def add_info(self, value):
        if value is not None and value != self.default_value:
            self.sum += value
            self.counter += 1

    @staticmethod
    def get_columns_names(field_name :  str) -> list:
        return [ field_name + "_avg", field_name + "_count"]
    
    def get_columns_values(self) -> list:
        return [None if self.counter == 0 else self.sum / self.counter, self.counter]

    def __iadd__(self, other):
        self.sum += other.sum
        self.counter += other.counter