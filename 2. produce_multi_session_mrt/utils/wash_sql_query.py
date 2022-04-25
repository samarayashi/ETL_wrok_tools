import re

single_comment_pattern = r"--.*"
multi_comment_pattern = r"/\*(.|\r|\n)+?\*/"
blank_line_pattern = r"^\s+"


def wash_sql_query(sql_query: str) -> str:
    sql_query = sql_query.strip()
    sql_query = re.sub(single_comment_pattern, "", sql_query)
    sql_query = re.sub(multi_comment_pattern, "", sql_query)
    sql_query = re.sub(blank_line_pattern, "", sql_query)
    sql_query = re.sub(r"#資料(日|期別|交換日期)#", "$$w_Exch_Date", sql_query)
    sql_query = re.sub(r"#?參數(1|2)#?", "$$w_Param\g<1>", sql_query)
    return sql_query
