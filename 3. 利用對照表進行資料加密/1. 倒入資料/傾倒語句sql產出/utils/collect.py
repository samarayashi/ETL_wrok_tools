import csv
def get_table_and_columns(file: str) -> dict:
    """Collect all table and columns, return dict with table(key), columns(values)"""

    all_tables_dict: dict[str, dict[str, str, str, list[str]]]
    all_tables_dict = {}

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            oracle_table_name = row['oracle_table_name'].strip()
            tibero_table_name = row['tibero_table_name'].strip()
            column_name = row['column_name'].strip()
            if oracle_table_name not in all_tables_dict.keys():
                all_tables_dict[oracle_table_name] = {"tibero_table_name": tibero_table_name, "columns": [column_name]}
            else:
                all_tables_dict[oracle_table_name]["columns"].append(column_name)
    return all_tables_dict