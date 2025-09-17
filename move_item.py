import json
import random
from datetime import datetime, timedelta
import requests
import csv 
import unicodedata
import random
import locale

source_path = "data.jsonl"
target_path = "index.json"
today_path = "today.json"


######################################################################

# Read all items from source.jsonl
with open(source_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

if not lines:
    print("No items left in source.jsonl")
    exit(0)

# ---- Modify this selection logic as needed ----
# For example: pick the first, random, or based on some field
idx = random.randint(0, len(lines) - 1)

item = json.loads(lines[idx])
print(item)
# ------------------------------------------------

# Append the selected item to target.jsonl
with open(target_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(item))

print(f"Moved item: {item}")


######################################################################
# write the current date to file + past words
######################################################################

def write_csv(data, file):
    for item in data:

        if item is not None:
            for key in item:
                if isinstance(item[key], str):
                    item[key] = "".join(ch for ch in item[key] if unicodedata.category(ch)[0]!="C")
                if item[key] == None:
                    item[key] = "NULL"

    fieldnames = data[0].keys()
    with open(file, mode='w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";", quotechar='"')
        writer.writeheader()
        for item in data:
            if item is not None:
                writer.writerow(item)
                

def  read_csv(path, deli=";"):
	data = []
	headers = None
	with open(path, encoding='utf-8-sig') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=deli, quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i,row in enumerate(spamreader):
			if i== 0 and headers is None:
				
				headers = row
			if i>0:
				record = {}
				for i, value in enumerate(row):
					try:
						value = value.replace("\xa0", " ")
						record[headers[i]] = value
					except:
							print(value)
				data.append(record)
				
	return data

def ordinal(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def dtStylish(dt,  local="en", include_year=True):
	if local == "en":
		f = '%B {th}, %Y'
		if not include_year:
			f = '%B {th}'
		return dt.strftime(f).replace("{th}", ordinal(dt.day))
	
	elif local == "fr":
		f = "{th} %B %Y"
		if not include_year:
			f = "{th} %B"
		return dt.strftime(f).replace("{th}", str(dt.day))

def get_wod():
	url = "https://definition-api.reverso.net/v1/api/todiscover/en"
	response = requests.get(url)
	return response.json()

def get_wod_image():
	url = "https://definition-api.reverso.net/v1/api/todiscoverimage/en"
	response = requests.get(url)
	return response.json()

def get_masked_expression(expression):
	expression_masked = expression
	wc = len(expression.split(" "))
	if wc>1:
		one_or_two = 1 if wc == 2 or wc == 3 else 2
		expression_masked = " ".join(expression.split(" ")[0:-one_or_two]+["_"*len(i) for i in expression.split(" ")[-one_or_two:]])

	return expression_masked

today = datetime.now().date()
today_str = str(today)

past = read_csv("past.csv",";")

wod = get_wod()
word = wod["word"]["entry"]
expression = wod["expression"]["entry"]

expression_masked = get_masked_expression(expression)

past.append({"date":today_str, "word":word, "expression":expression})
write_csv(past, "past.csv")


for i in past:
	tmp = datetime.strptime(i["date"], "%Y-%m-%d").date()
	i["date"]=tmp

past_terms_candidates = [i for i in past if i["date"]>datetime.now().date()-timedelta(days=14)]

past_terms = []

selected_dates = []

while len(selected_dates)!=4:
	rand = random.randint(0, len(past_terms_candidates)-1)
	if rand not in selected_dates:
		selected_dates.append(rand)

selected_dates.sort()

for i in zip(selected_dates,["word","word", "expression", "expression"]):
	index,term = i
	past_terms.append(
		{
			"date":dtStylish(past_terms_candidates[index]["date"], include_year=False), 
			"date_fr":dtStylish(past_terms_candidates[index]["date"], include_year=False, local="fr"), 
			"term":past_terms_candidates[index][term]
		})


today = {
	"today":dtStylish(datetime.now().date()),
	"date_fr":dtStylish(datetime.now().date(), local="fr"),
	"past_terms_1":past_terms[0],
	"past_terms_2":past_terms[1],
	"past_terms_3":past_terms[2],
	"past_terms_4":past_terms[3]
}

json.dump(today, open(today_path, "w"))	
