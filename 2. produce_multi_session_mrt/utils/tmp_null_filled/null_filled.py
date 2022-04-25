import csv
import re
from utils.tmp_null_filled.bracket_excluded_char_split import bracket_excluded_char_split



def read_source_file(source_file: str):
    ori_sql_list = []
    all_columns_list = []
    with open(source_file, 'r', encoding="utf-8") as ori_file:
        reader = csv.reader(ori_file)
        next(reader, None) # skip header
        for row in reader:
            ori_sql_list.append(row[0])
            all_columns_list.append(row[1])

    return ori_sql_list, all_columns_list


def get_new_select_columns(all_ori_column: str, target_ori_column: str, target_sql_column: str) -> str:
    ori_list = all_ori_column.split(",")
    clean_ori_list = [column.lower().strip() for column in ori_list]

    target_list = target_ori_column.split(",")
    clean_target_list = [column.lower().strip() for column in target_list]

    sql_list = bracket_excluded_char_split(target_sql_column, ",")
    clean_sql_list = [column.strip() for column in sql_list]

    target_dict = {clean_target_list[i]: clean_sql_list[i] for i in range(len(clean_target_list))}
    new_column_list = []
    for column in clean_ori_list:
        if column in clean_target_list:
            new_column_list.append(target_dict[column])
        else:
            new_column_list.append("null")

    new_column_str = ",".join(new_column_list)
    return new_column_str

def get_new_sql_queries(ori_sql_queries : list[str], all_ori_columns: list[str]) ->list[str]: 
    new_queries = []
    for i in range(len(ori_sql_queries)):
        select_index = ori_sql_queries[i].lower().find("select")
        end_index = ori_sql_queries[i].find(");")
        before_select = ori_sql_queries[i][:select_index]
        select_statement = ori_sql_queries[i][select_index:end_index]

        if ")" in before_select:
            target_ori_columns = re.search(r"(?<=\()(.|\s)+?(?=\))", before_select).group(0)
            target_sql_coluns = re.search(r"(?<=select )(.|\s)+?(?= from)", select_statement).group(0)
            new_target_columns_str = get_new_select_columns(all_ori_columns[i], target_ori_columns, target_sql_coluns)
            new_query = re.sub(r"(?<=select )(.|\s)+?(?= from)", new_target_columns_str, select_statement, count=1)
        else:
            new_query = select_statement

        new_queries.append(new_query)

    return new_queries

def write_new_file(new_file: str, ori_sql_list: list[str], all_columns_list: list[str]):
    with open(new_file, 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # write header
        writer.writerow(["ori_sql",	"all_columns" ,	"new_sql"])

        # write content
        for i in range(len(ori_sql_list)):
            new_sql_list = get_new_sql_queries(ori_sql_list, all_columns_list)
            writer.writerow([ori_sql_list[i], all_columns_list[i], new_sql_list[i]])


if __name__ == "__main__":
    ori_sql_list, all_columns_list= read_source_file("utils/tmp_null_filled/TMP_TSET_TABLEA_ori.csv")
    write_new_file("utils/tmp_null_filled/TMP_TSET_TABLEA_new.csv", ori_sql_list, all_columns_list)

