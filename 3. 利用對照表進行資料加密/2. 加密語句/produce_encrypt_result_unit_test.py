import csv

ALL_TABLE_COLUMNS_FILE = "./source/58table(by_official0719).csv"
CONDITION_FILE = './source/select_condition(by_official0719).csv'
CHECKED_IDNS_FILE = "./source/checked_idns(by_official0719).csv"
CHECKED_NAMES_FILE = "./source/checked_names(by_official0719-1).csv"
OUT_PUT_FILE = f"output/unmatch_count_test_sql(by_official0719-1).sql"


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


def produce_ut_sql(tibero_ori_table: str, tibero_encrypt_table: str, idn_columns_list: list, ) -> str:
    single_select_list = []
    for idn_column in idn_columns_list:
        minus_sql = f"select {idn_column} from mx.{tibero_ori_table} minus select idn from md.token_idn"
        single_select_list.append(f"select * from mx.{tibero_ori_table} where {idn_column} in ({minus_sql})")
    union_select = "\n\tunion\n\t".join(single_select_list)
    count_ori_unmatch_select = f"select count(*) as ori_unmatch_count from" \
                               f"\n\t({union_select})"

    encrypt_where_statement = " or ".join([f"{idn_column}='no_match'" for idn_column in idn_columns_list])
    count_encrypt_unmatch_select = f"select count(*) as encrypt_unmatch_count from mx.{tibero_encrypt_table} where {encrypt_where_statement}"
    ut_sql = f"-----{tibero_ori_table} unmatch count UT-----\n" \
             f"select ori_unmatch_count, encrypt_unmatch_count, ori_unmatch_count - encrypt_unmatch_count as diff\n" \
             f"from\n" \
             f"-----count ori------\n" \
             f"({count_ori_unmatch_select}) ori\n" \
             f"inner join\n" \
             f"-----count encrypt------\n" \
             f"({count_encrypt_unmatch_select}) enc\n" \
             f"on 1=1;"

    return ut_sql


def main():
    all_tables = get_table_and_columns(ALL_TABLE_COLUMNS_FILE)
    print(f"read how many table:{len(all_tables)}")

    with open(OUT_PUT_FILE, 'w', encoding='utf-8') as file:
        for table_content in all_tables.values():
            tibero_ori_table = table_content["tibero_ori_table"]
            tibero_encrypt_table = table_content["tibero_encrypt_table"]
            columns = table_content["columns"]
            all_columns = classifiy_columns(columns)

            ut_sql = produce_ut_sql(tibero_ori_table, tibero_encrypt_table, all_columns['idns'])
            file.write(ut_sql+"\n\n\n")
            file.write("----------------------------\n")


if __name__ == "__main__":
    main()
