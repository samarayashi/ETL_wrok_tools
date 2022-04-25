from utils.collect import get_table_and_columns

SOURCE_FILE = './source/test_sample.csv'
PACKAGE_NAME = "sync_oracle"
all_tables = get_table_and_columns(SOURCE_FILE)
for oracle_table_name, others in all_tables.items():
    tibero_table_name = others["tibero_table_name"]
    procedure_name = tibero_table_name.replace("STG_", "") + "_SYNC"
    all_tables[oracle_table_name]["procedure_name"] = procedure_name


# specification
def write_package_spec():
    all_procedure_define = ""
    for oracle_table_name, others in all_tables.items():
        tibero_table_name = others["tibero_table_name"]
        procedure_name = others["procedure_name"]
        procedure_define = f"\tPROCEDURE {procedure_name}(" \
                           f"fetch_date IN {tibero_table_name}.data_exch_date%TYPE DEFAULT SYSDATE," \
                           f"fetch_limit_in IN number DEFAULT 100000);\n"
        all_procedure_define += procedure_define

    all_procedure_define = all_procedure_define.rstrip()
    package_spec = f"CREATE OR REPLACE PACKAGE MX.{PACKAGE_NAME} AS\n" \
                   f"{all_procedure_define}\n" \
                   f"END {PACKAGE_NAME};"

    with open("./out_put/package_spec.sql", "w") as file:
        file.write(package_spec)


def write_package_body():
    all_procedure_bodys = ""
    for oracle_table_name, others in all_tables.items():
        tibero_table_name = others["tibero_table_name"]
        all_columns_str = ",".join(others["columns"])
        array_columns_str = ",".join(["recs(i)." + column for column in others["columns"]])
        procedure_name = others['procedure_name']

        procedure_body = f"PROCEDURE {procedure_name} (\n" \
                         f"\tfetch_date IN {tibero_table_name}.data_exch_date%TYPE DEFAULT SYSDATE,\n" \
                         f"\tfetch_limit_in       IN number DEFAULT 100000)\n" \
                         f"IS\n" \
                         f"\tchk_data number:=0;\n" \
                         f"\tCURSOR  cur_oracle IS\n" \
                         f"\t\tSELECT /*+ parallel (8) */ {all_columns_str}\n" \
                         f"\t\tFROM {oracle_table_name}@T2TO_MX;\n" \
                         f"\tTYPE rec_array IS TABLE OF cur_oracle%ROWTYPE INDEX BY BINARY_INTEGER;\n" \
                         f"\trecs rec_array;\n" \
                         f"\tnow_count number := 0;\n" \
                         f"\tstart_time number := DBMS_UTILITY.get_time;\n" \
                         f"BEGIN\n" \
                         f"\tselect count(*) into chk_data from MX.{tibero_table_name};\n" \
                         f"\tDBMS_OUTPUT.PUT_LINE('Fetch Oracle: {oracle_table_name} to Tibero: MX.{tibero_table_name}');\n" \
                         f"\tDBMS_OUTPUT.PUT_LINE('DATA_EXCH_DATE: '||fetch_date);\n" \
                         f"\tIF (chk_data >0) THEN\n" \
                         f"\t\texecute immediate 'TRUNCATE TABLE MX.{tibero_table_name}';\n" \
                         f"\t\tDBMS_OUTPUT.PUT_LINE('Truncate table ('||chk_data||' row dropped)');\n" \
                         f"\tEND IF;\n" \
                         f"\tstart_time := DBMS_UTILITY.get_time;\n" \
                         f"\tOPEN cur_oracle;\n" \
                         f"\tLOOP\n" \
                         f"\t\tFETCH cur_oracle BULK COLLECT into recs LIMIT fetch_limit_in;\n" \
                         f"\t\tEXIT WHEN recs.COUNT = 0;\n" \
                         f"\t\tnow_count := now_count+recs.COUNT;\n" \
                         f"\t\tFORALL i IN 1 .. recs.COUNT\n" \
                         f"\t\t\tINSERT INTO /*+ parallel (8) */ MX.{tibero_table_name}({all_columns_str},DATA_EXCH_DATE)\n" \
                         f"\t\t\tVALUES({array_columns_str},fetch_date);\n" \
                         f"\t\tDBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');\n" \
                         f"\t\tDBMS_APPLICATION_INFO.SET_CLIENT_INFO('Insert data into {tibero_table_name}');\n" \
                         f"\t\tCOMMIT;\n" \
                         f"\tEND LOOP;\n" \
                         f"\tCOMMIT;\n" \
                         f"\tCLOSE cur_oracle;\n" \
                         f"\tDBMS_OUTPUT.PUT_LINE('Insert '||to_char(now_count)||' row, spend '||to_char((DBMS_UTILITY.GET_TIME - start_time)/100)||'sec');\n" \
                         f"\tDBMS_APPLICATION_INFO.SET_MODULE('Records Processed: ' ||now_count, 'Elapsed: ' || (DBMS_UTILITY.GET_TIME - start_time)/100 || ' sec');\n" \
                         f"\tDBMS_APPLICATION_INFO.SET_CLIENT_INFO('Finished {tibero_table_name}');\n" \
                         f"\tCOMMIT;\n" \
                         f"EXCEPTION\n" \
                         f"\tWHEN OTHERS THEN\n" \
                         f"\t\tDBMS_OUTPUT.PUT_LINE('!!!!! {procedure_name} ERROR !!!');\n" \
                         f"\t\tDBMS_OUTPUT.PUT_LINE( 'error message: ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE || DBMS_UTILITY.FORMAT_ERROR_STACK );\n" \
                         f"END {procedure_name};\n\n"
        all_procedure_bodys += procedure_body

    package_body = f"CREATE OR REPLACE PACKAGE BODY MX.{PACKAGE_NAME} AS\n\n\n" \
                   f"{all_procedure_bodys}\n\n" \
                   f"END {PACKAGE_NAME};"

    with open("./out_put/package_body.sql", "w") as file:
        file.write(package_body)


def write_execute_procedure():
    execcute_sql = ""
    for oracle_table_name, others in all_tables.items():
        procedure_name = others["procedure_name"]
        execcute_sql += f"CALL MX.{PACKAGE_NAME}.{procedure_name};\n"

    with open("./out_put/execute_procedure.sql", "w") as file:
        file.write(execcute_sql)


if __name__ == "__main__":
    write_package_spec()
    write_package_body()
    write_execute_procedure()