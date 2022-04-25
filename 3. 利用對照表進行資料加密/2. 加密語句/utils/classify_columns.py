import csv

CHECKED_IDN_FILE = "../source/checked_idn.csv"
CHECKED_NAME_FILE = "../source/checked_name.csv"

def get_table_and_columns(file: str) -> dict:
    '''Collect all table and columns, return dict with table(key), columns(values)'''
    all_tables = {}
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            table = row['table'].strip()
            column = row['column'].strip()
            if table in all_tables:
                all_tables[table].append(column)
            else:
                all_tables[table] = [column]
    return all_tables


def classifiy_columns(all_columns: list) -> dict:
    '''Input the list of all columns, classfity into names, idns and others. Return the dict with list'''

    all_idn_columns = []
    all_name_columns = []
    with open(CHECKED_IDN_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_idn_columns.append(row['en_column_name'])

    with open(CHECKED_NAME_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_name_columns.append(row['en_column_name'])

    name_columns = []
    idn_columns = []
    other_columns = []
    for column in all_columns:
        if column in all_name_columns:
            name_columns.append(column)
        elif column in all_idn_columns:
            idn_columns.append(column)
        else:
            other_columns.append(column)
    return {'names': name_columns, 'idns': idn_columns, 'others': other_columns}


if __name__ == "__main__":
    with open('../output/classified_columns.csv', 'w', encoding='utf-8') as file:
        fieldnames = ['table_name', 'column_name', 'confidential_content']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        all_tables = get_table_and_columns("../source/SDM0603_STG_69tables.csv")
        print(len(all_tables))

        for table, columns in all_tables.items():
            all_columns = classifiy_columns(columns)
            for column in all_columns["names"]:
                writer.writerow({'table_name': table, 'column_name': column, 'confidential_content': 'name'})
            for column in all_columns["idns"]:
                writer.writerow({'table_name': table, 'column_name': column, 'confidential_content': 'idn'})
            for column in all_columns["others"]:
                writer.writerow({'table_name': table, 'column_name': column, 'confidential_content': 'X'})