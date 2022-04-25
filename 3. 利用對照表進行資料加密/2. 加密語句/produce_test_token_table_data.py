import csv

ALL_TABLE_COLUMNS_FILE = "./source/58table(by_official0719).csv"
CONDITION_FILE = './source/select_condition(by_official0719).csv'
CHECKED_IDNS_FILE = "./source/checked_idns(by_official0719).csv"
CHECKED_NAMES_FILE = "./source/checked_names(by_official0719-1).csv"
OUT_PUT_FILE = f"output/produce_idn_test_data_sql(by_official0719).sql"


def get_table_and_columns(file: str) -> dict:
    """Collect all table and columns, use the key to filter duplicated table name, return dict with table content"""
    all_tables = {}
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tibero_ori_table = row['tibero_ori_table'].strip()
            tibero_encrypt_table = row['tibero_encrypt_table'].strip()
            column = row['column'].strip()
            if tibero_ori_table not in all_tables.keys():
                all_tables[tibero_ori_table] = {'columns': [column],
                                                "tibero_ori_table": tibero_ori_table,
                                                'tibero_encrypt_table': tibero_encrypt_table}
            else:
                all_tables[tibero_ori_table]['columns'].append(column)

    return all_tables


def classifiy_columns(all_columns: list) -> dict:
    """Input the list of all columns, classfity into names, idns and others. Return the dict with list"""
    with open(CHECKED_IDNS_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        all_idn_columns = [row['idn_column'] for row in reader]

    with open(CHECKED_NAMES_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        all_name_columns = [row['name_column'] for row in reader]

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


def get_select_condition(condition_csv: str) -> dict:
    with open(condition_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        tables_condition = {row['tibero_ori_table'].strip(): row["condition"].strip() for row in reader}
        return tables_condition


def produce_select_list(tibero_ori_table: str, idn_columns_list: list) -> list[str]:
    select_idn_list = [f"select {idn_column} as idn from mx.{tibero_ori_table}" for idn_column in idn_columns_list]

    return select_idn_list


def main():
    all_tables = get_table_and_columns(ALL_TABLE_COLUMNS_FILE)
    print(f"read how many table:{len(all_tables)}")

    select_list = []
    for table_content in all_tables.values():
        tibero_ori_table = table_content["tibero_ori_table"]
        columns = table_content["columns"]
        all_columns = classifiy_columns(columns)
        select_list += produce_select_list(tibero_ori_table, all_columns['idns'])
    select_union_sql = "\nUNION\n".join(select_list)

    with open(OUT_PUT_FILE, 'w', encoding='utf-8') as file:
        file.write("truncate table md.token_idn;\n\n")
        file.write(
            "insert into MD.token_idn(idn, idn_token)\n" 
            "select idn, 'enc'||substr(idn,4,99)\n"
            "from\n" 
            f"({select_union_sql})\n" 
            "where length(idn)<=10;")


if __name__ == "__main__":
    main()
