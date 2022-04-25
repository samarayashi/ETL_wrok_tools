import re
import sqlite3

single_comment_pattern = r"--.*"
multi_comment_pattern = r"/\*(.|\r|\n)+?\*/"
blank_line_pattern = r"^\s+"


def wash_sql_query(sql_query: str) -> str:
    sql_query = sql_query.strip()
    sql_query = re.sub(single_comment_pattern, "", sql_query)
    sql_query = re.sub(multi_comment_pattern, "", sql_query)
    sql_query = re.sub(blank_line_pattern, "", sql_query)
    sql_query = re.sub(r"#資料(日|期別|交換日期)#", r"$$w_Exch_Date", sql_query)
    sql_query = re.sub(r"#?參數(1|2)#?", r"$$w_Param\g<1>", sql_query)
    return sql_query


def get_user_etl_dict(db_location) -> dict:
    try:
        con = sqlite3.connect(db_location)
        cur = con.cursor()
        query = 'select user_system_table, etl_table from user_system_table;'
        cur.execute(query)
        rows = cur.fetchall()
        conversion_dict = {}
        for row in rows:
            conversion_dict[row[0]] = row[1]
    finally:
        cur.close()
        con.close()

    return conversion_dict


def replace_user_table(sql_query: str, conversion_dict: dict):
    for user, etl in conversion_dict.items():
        sql_query = re.sub(re.escape(user), re.escape(etl), sql_query, flags=re.IGNORECASE)
    return sql_query


def convert_half_width(sql_query: str):
    full2half = dict((i + 0xFEE0, i) for i in range(0x21, 0x7F))
    full2half[0x3000] = 0x20
    return sql_query.translate(full2half)

if __name__ == '__main__':

    test_sql = """
INSERT INTO TMP_TEST_PART1
select decode(a.sno,null,'0',a.sno) sno, c.ftyp, c.ciid, b.idn, b.brdte, b.name, trim(b.hmk) hmk, c.uno, c.unock, c.acno, c.range, start_date, end_date,
TO_DATE('$$w_Exch_Date','YYYYMMDD') AS DATA_EXCH_DATE
from MRT_TEST_EXT a, MRT_TEST_TABLEB b ,MRT_TEST_TABLEC c   
    """
    sql = wash_sql_query(test_sql)
    user_etl_dict = get_user_etl_dict("tables_information.db")
    sql = replace_user_table(sql, user_etl_dict)
    sql = convert_half_width(sql)
    print(sql)

