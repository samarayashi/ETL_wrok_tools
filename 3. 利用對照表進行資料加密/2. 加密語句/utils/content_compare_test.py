import csv
idn1 = set()
idn2 = set()
with open("../source/checked_name.csv", 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        idn1.add(row['en_column_name'])
with open("checked_name2.csv", 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        idn2.add(row['en_column_name'])

diff = idn1.symmetric_difference(idn2)
print(diff)


    