import csv
import os
from datetime import datetime

today = datetime.now()
DATA_EXCH_DATE = today.strftime("%Y-%m-%d")
SDM_VERSION = "v20210820"
EMAIL = "XXX@email.com.tw"

SOURCE_FILE = "source/test_sample_bas.csv"
DEVELOP_PERIOD = "sample_test_bas"



def get_table_and_columns(file: str) -> dict:
    """Collect all table and columns, return dict with source_table(key), target_table & columns(values)"""

    all_tables_dict: dict[str: dict[str, str, str, list[str]]]
    all_tables_dict = {}

    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_table_name = row['source_table_name'].strip()
            target_table_name = row['target_table_name'].strip()
            column_name = row['column_name'].strip()
            if source_table_name not in all_tables_dict:
                all_tables_dict[source_table_name] = {"target_table_name": target_table_name, "columns": [column_name]}
            else:
                all_tables_dict[source_table_name]["columns"].append(column_name)
    return all_tables_dict


def get_count_sql(source_table_name: str, target_table_name: str):

    count_target_sql = f"select count(*) as target_cnt\n" \
                       f"\tfrom IA.{target_table_name}\n" \
                       f"\twhere DATA_EXCH_DATE=TO_DATE('{DATA_EXCH_DATE}','YYYY-MM-DD')"

    count_source_sql = f"select count(*) as source_cnt\n" \
                       f"\tfrom IA.{source_table_name}" \

    count_sql = f"select '{target_table_name}' as stg_name, " \
                f"t.target_cnt, s.source_cnt, t.target_cnt - s.source_cnt as diff_cnt\n" \
                f"from\n" \
                f"\t--Target Count\n" \
                f"\t({count_target_sql}) t\n\n" \
                f"\tinner join\n" \
                f"\t--Source Count\n" \
                f"\t({count_source_sql}) s\n\n" \
                f"\ton 1=1;"
    return count_sql


def get_detail_sql(source_table_name: str, target_table_name: str, columns: list):
    target_record_sql = f"select *\n" \
                        f"\tfrom {target_table_name}\n" \
                        f"\twhere DATA_EXCH_DATE=TO_DATE('{DATA_EXCH_DATE}','YYYY-MM-DD')"
    source_record_sql = f"select {','.join(columns)},DATA_EXCH_DATE\n" \
                        f"\tfrom {source_table_name}"
    detail_sql = f"select *\n" \
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

for source_table_name, contents in tables.items():
    target_table_name = contents["target_table_name"]
    columns = contents["columns"]
    count_sql = get_count_sql(source_table_name, target_table_name)
    detail_sql = get_detail_sql(source_table_name, target_table_name, columns)

    out_put_file = f"sql_outputs({DEVELOP_PERIOD})"

    if not os.path.exists(f"./output/{out_put_file}"):
        os.mkdir(f"./output/{out_put_file}")
    if not os.path.exists(f"./output/{out_put_file}/{target_table_name}"):
        os.mkdir(f"./output/{out_put_file}/{target_table_name}")

    with open(f"./output/{out_put_file}/{target_table_name}/{target_table_name}_count.sql", "w") as file:
        file.write(meta_data + "\n\n")
        file.write(count_sql)

    with open(f"./output/{out_put_file}/{target_table_name}/{target_table_name}_detail.sql", "w") as file:
        file.write(meta_data + "\n\n")
        file.write(detail_sql)
