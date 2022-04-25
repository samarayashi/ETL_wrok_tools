import csv

ALL_TABLE_COLUMNS_FILE = "./source/sample_table.csv"
CONDITION_FILE = './source/sample_table_condition.csv'
CHECKED_IDNS_FILE = "./source/checked_idns.csv"
CHECKED_NAMES_FILE = "./source/checked_names.csv"
OUT_PUT_FILE = f"output/sample_table_insert_sql.sql"


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

            
def produce_encrypt_sql(tibero_ori_table: str, tibero_encrypt_table: str, table_condition: str,
                        name_columns_list: list, idn_columns_list: list, other_columns_list: list) -> str:

    new_name_list = [f"'測試'||substr(ori.{name},3) as {name}" for name in name_columns_list]
    
    new_idn_list = []
    token_index = 1
    # decode(NVL(t1.idn_token, ori.EVTIDNNO),t1.idn_token, t1.idn_token,null, null,ori.EVTIDNNO, 'no_match') as EVTIDNNO
    for idn_column in idn_columns_list:
        new_idn_list.append(f"decode(nvl(t{token_index}.idn_token, ori.{idn_column}), "
                            f"t{token_index}.idn_token,t{token_index}.idn_token,"
                            f"null,null,"
                            f"ori.{idn_column}, 'no_match') as {idn_column}")
        token_index += 1
    new_other_columns_list = [f"ori.{other_column}" for other_column in other_columns_list]

    old_columns_list = name_columns_list + idn_columns_list + other_columns_list
    old_column_str = ",".join(old_columns_list)
    new_columns_list = new_name_list+new_idn_list+new_other_columns_list
    new_columns_str = ",".join(new_columns_list)

    from_statement = f"from mx.{tibero_ori_table} ori"
    
    token_index = 1
    join_statement = ""
    for idn_column in idn_columns_list:
        join_statement += f"\tleft join MD.TOKEN_IDN t{token_index} on ori.{idn_column} = t{token_index}.idn\n"
        token_index += 1
    join_statement = join_statement.lstrip()

    where_statement = ""
    if table_condition:
        where_statement = f"where {table_condition}"

    insert_encrypt_sql = f"insert into mx.{tibero_encrypt_table}({old_column_str})\n" \
                         f"select {new_columns_str}\n" \
                         f"\t{from_statement}\n" \
                         f"\t{join_statement}" \
                         f"\t{where_statement}"
    insert_encrypt_sql = insert_encrypt_sql.rstrip()+";"

    return insert_encrypt_sql


def main():
    all_tables = get_table_and_columns(ALL_TABLE_COLUMNS_FILE)
    tables_condition = get_select_condition(CONDITION_FILE)
    print(f"read how many table:{len(all_tables)}")

    with open(OUT_PUT_FILE, 'w', encoding='utf-8') as file:
        for table_content in all_tables.values():
            tibero_ori_table = table_content["tibero_ori_table"]
            tibero_encrypt_table = table_content["tibero_encrypt_table"]
            columns = table_content["columns"]
            table_condition = tables_condition[tibero_ori_table]
            all_columns = classifiy_columns(columns)

            sql = produce_encrypt_sql(tibero_ori_table, tibero_encrypt_table, table_condition,
                                      all_columns['names'], all_columns['idns'], all_columns['others'])
            file.write(f'-----{tibero_encrypt_table}------\n')
            file.write(sql+"\n")
            file.write("commit;\n\n\n")


if __name__ == "__main__":
    main()
