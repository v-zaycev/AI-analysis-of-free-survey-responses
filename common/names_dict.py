import pandas as pd
import re
import copy
from common.generate_text import async_get_name
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, NewsNERTagger, PER, NamesExtractor, Doc

class NamesDict:
    def __init__(self, filename : str):
        """Коструктор, читающий имена из файла
        Args:
            filename (str): .xlsx файл с именами, имена должны находиться в колонке с названием \"name\"
        """
        data = pd.read_excel(filename)
        self.__data = dict()
        for _, row in data.iterrows():
            self.__data[self.__standartize_str(row["name"])] = row["name"]
    
    def get_names(self, name : str) -> list :
        """Метод возвращает список ФИО, частью которых может быть исходная строка
        Args:
            name (str): рассматриваемая строка
        Returns:
            list: список имён из словаря, частью которых может быть входная строка
        """
        candidates = list()
        for i in self.__data.keys():
            if i.issuperset(self.__standartize_str(name)):
                candidates.append(self.__data[i])
        if len(candidates) == 0:
            self.__check_initials(name, candidates)
        if len(candidates) == 0:
            self.__normalize_name(name, candidates)
        return candidates
    
    def __standartize_str (self, name : str) ->  frozenset:
        name = name.strip().replace("ё","е").replace("Ё", "Е")
        name = re.split('[ \t,;:+.!?]+', name)
        name = [i.lower() for i in name if i != ""]
        return frozenset(name)
    
    def __check_initials(self, name: str, candidates : list):
        """Метод проверяет наличие инициалов в строке и ищет соответствия в словаре
        Args:
            name (str): рассматриваемая строка
            candidates (list): список потенциальных имён, куда добавляются новые
        """
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
                last = name[1]
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

    def __normalize_name(self, name : str, candidates: list):
        """Метод приводит разговорную форму имени к полному и ищет соответствия в словаре
        Args:
            name (str): рассматриваемая строка
            candidates (list): список потенциальных имён, куда добавляются новые
        """
        segmenter = Segmenter()
        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)
        ner_tagger = NewsNERTagger(emb)
        morph_vocab = MorphVocab()
        names_extractor = NamesExtractor(morph_vocab)
        
        name = name.strip().replace("ё","е")
        
        doc = Doc(name)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        for token in doc.tokens:
            token.lemmatize(morph_vocab)
        doc.tag_ner(ner_tagger)
        for span in doc.spans:
            span.normalize(morph_vocab)
        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)
        names = [_.fact.as_dict for _ in doc.spans if _.type == PER]
        if len(names) != 1 or "first" not in names[0]:
            return
        
        normalized_names = re.findall("[а-яА-ЯёЁ]+", async_get_name(names[0]["first"]).replace("ё","е").replace("Ё", "Е"))
        name = re.split('[ \t,;:.!?+]+', name)
        for normalized_name in normalized_names:
            name_cp = copy.deepcopy(name)
            for i in range(len(name_cp)):
                if names[0]["first"] == name_cp[i]:
                    name_cp[i] = normalized_name
                    break
            name_cp = frozenset([i.lower() for i in name_cp if i != ""])
            for i in self.__data.keys():
                if i.issuperset(name_cp):
                    candidates.append(self.__data[i])
        