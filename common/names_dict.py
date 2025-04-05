import pandas as pd
import re

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
