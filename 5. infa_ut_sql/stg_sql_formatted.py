import csv
import os
from datetime import datetime

today = datetime.now()
DATA_EXCH_DATE = today.strftime("%Y-%m-%d")
SDM_VERSION = "v20210820"
EMAIL = "XXX@email.com.tw"

SOURCE_FILE = "source/test_sample_stg.csv"
DEVELOP_PERIOD = "test_sample_stg"


def get_table_and_columns(file: str) -> dict:
    """Collect all table and columns, return dict with table(key), columns(values)"""
    all_tables_dict: dict[str: dict[str, str, str, list[str]]]
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


def get_count_sql(oracle_table_name: str, tibero_table_name: str, exch_date: str = DATA_EXCH_DATE):
    count_target_sql = f"select count(*) as target_cnt\n" \
                       f"\tfrom IA.{tibero_table_name}\n" \
                       f"\twhere DATA_EXCH_DATE=TO_DATE('{exch_date}','YYYY-MM-DD')"
    count_source_sql = f"select count(*) as source_cnt\n" \
                       f"\tfrom {oracle_table_name}@T2O_IA"

    count_sql = f"select '{tibero_table_name}' as stg_name, " \
                f"t.target_cnt, s.source_cnt, t.target_cnt - s.source_cnt as diff_cnt\n" \
                f"from\n" \
                f"\t--Target Count\n" \
                f"\t({count_target_sql}) t\n\n" \
                f"\tinner join\n" \
                f"\t--Source Count\n" \
                f"\t({count_source_sql}) s\n\n" \
                f"\ton 1=1;"
    return count_sql


def get_detail_sql(oracle_table_name: str, tibero_table_name: str, columns: list, exch_date: str = DATA_EXCH_DATE):
    target_record_sql = f"select *\n" \
                        f"\tfrom IA.{tibero_table_name}\n" \
                        f"\twhere DATA_EXCH_DATE=TO_DATE('{exch_date}','YYYY-MM-DD')"
    source_record_sql = f"select {','.join(columns)},TO_DATE('{exch_date}', 'YYYY-MM-DD') as DATA_EXCH_DATE\n" \
                        f"\tfrom {oracle_table_name}@T2O_IA"
    detail_sql = f"select count(*), merge_tmp.*\n" \
                 f"from\n" \
                 f"\t(\n" \
                 f"\t--Target Records\n" \
                 f"\t{target_record_sql}\n\n" \
                 f"\tunion all\n" \
                 f"\t--Source Records\n" \
                 f"\t{source_record_sql}\n\n" \
                 f"\t) merge_tmp\n\n" \
                 f"--All Columns\n" \
                 f"group by {','.join(columns)},DATA_EXCH_DATE\n\n" \
                 f"--Normal = 2\n" \
                 f"having count(*) <> 2;"
    return detail_sql


def get_meta_str(email=EMAIL, sdm_v=SDM_VERSION, date=today.strftime('%Y/%m/%d')):
    meta_str = f"--{email}\n" \
               f"--SDM {sdm_v}\n" \
               f"--Date: {date}"

    return meta_str


tables = get_table_and_columns(SOURCE_FILE)
meta_data = get_meta_str()

for oracle_table_name, contents in tables.items():
    tibero_table_name = contents["tibero_table_name"]
    columns = contents["columns"]
    count_sql = get_count_sql(oracle_table_name, tibero_table_name)
    detail_sql = get_detail_sql(oracle_table_name, tibero_table_name, columns)

    out_put_file = f"sql_outputs({DEVELOP_PERIOD})"
    if not os.path.exists(f"./output/{out_put_file}"):
        os.mkdir(f"./output/{out_put_file}")
    if not os.path.exists(f"./output/{out_put_file}/{tibero_table_name}"):
        os.mkdir(f"./output/{out_put_file}/{tibero_table_name}")

    with open(f"./output/{out_put_file}/{tibero_table_name}/{tibero_table_name}_count.sql", "w") as file:
        file.write(meta_data + "\n\n")
        file.write(count_sql)

    with open(f"./output/{out_put_file}/{tibero_table_name}/{tibero_table_name}_detail.sql", "w") as file:
        file.write(meta_data + "\n\n")
        file.write(detail_sql)
