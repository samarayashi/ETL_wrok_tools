import csv

FILE_NAME = "../source/SDM0624_STG_all_columns.csv"

idn_columns = []
name_columns = []
idn_list = []
name_list = []
with open(FILE_NAME, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        ch_name = row['ch_column_name'].strip()
        en_name = row['en_column_name'].strip()
        if 'IDN' in en_name and en_name not in idn_list:
            idn_columns.append({'ch_column_name': ch_name, 'en_column_name': en_name})
            idn_list.append(en_name)

        if 'NAME' in en_name and en_name not in name_list:
            name_columns.append({'ch_column_name': ch_name, 'en_column_name': en_name})
            name_list.append(en_name)


with open('../source/unchecked_idn.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ch_column_name', 'en_column_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(idn_columns)

with open('../source/unchecked_name.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ch_column_name', 'en_column_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(name_columns)
