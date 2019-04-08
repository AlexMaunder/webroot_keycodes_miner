import csv

inputm = []

with open('keycodes.csv', mode='r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter="\n")
    for row in reader:
        inputm.append(row[0])
print(inputm)