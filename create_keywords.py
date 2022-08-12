import pandas as pd
import csv

def get_list_of_urls():
    with open('temp.txt', 'a') as f:
        f.write('Hello \n')

def create_list_of_keywords():
    keywords = []
    list_of_us_cities = []
    with open('hotel keywords.txt', 'r') as f:
        d = f.readlines()
        for line in d:
            keywords.append(line.strip())

    output = []

    with open('US Cities (top 4000).xlsx - Sheet1.csv', 'r') as f:
        data = csv.reader(f)
        for d in data:
            for k in keywords:
                output.append({
                    'City': d[1],
                    'Code': d[2],
                    'Keyword': k,
                    'Flag': 0
                })

    pd.DataFrame(output).to_csv('keywords.csv', index=None)
    print(len(output))

# create_list_of_keywords()
get_list_of_urls()