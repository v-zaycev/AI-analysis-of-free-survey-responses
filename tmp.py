import pandas as pd
import re
import sys

def standartize_str (name : str) -> str:
    name = name.strip()
    name = re.split('[ \t,;\:\-\.\!\?]+', name)
    name = [i.lower().title() for i in name]
    name.sort()
    name = ' '.join(name)
    return name

sys.stdout.reconfigure(encoding='utf-8')

def update_names(names_set : set, name : frozenset):
    is_unique = True
    for i in names_set:
        if i.issuperset(name):
            is_unique = False
            break
        if name.issuperset(i):
            names_set.remove(i)
            names_set.add(name)
            return 
    if is_unique:
        names_set.add(name)



data = pd.read_excel("resources\\names_raw.xlsx", index_col = False)
data_base = data.copy()
data["name"] = data["name"].apply(standartize_str)
data = data.drop_duplicates(subset=["name"])
data = data.sort_values(by = "name")
names = set()
for i in data["name"]:
    name = frozenset(i.split())
    update_names(names, name)

names = [' '.join(i) for i in names]
names.sort()
data_out = pd.DataFrame(names, columns = ["name"] )
data_out.to_excel("resources\\tmp2.xlsx", index = False)
print(data["name"])

