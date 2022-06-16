from raw_sql import ColumnTextHandler
from column_info import DecodeColumnHandler
from sdm import SdmProducer


test_sql = input_raw_sql = """ 
INSERT INTO TMP_TEST_PART1
select decode(a.sno,null,'0',a.sno) sno, c.ftyp, c.ciid, b.idn, b.brdte, b.name, trim(b.hmk) hmk, c.uno, c.unock, c.acno, c.range, start_date, end_date,
TO_DATE('$$w_Exch_Date','YYYYMMDD') AS DATA_EXCH_DATE
from MRT_TEST_EXT a, MRT_TEST_TABLEB b ,MRT_TEST_TABLEC c  
"""

column_handler = ColumnTextHandler(test_sql)
with DecodeColumnHandler('tables_information.db', column_handler) as column_decoder:
    detail_list = column_decoder.get_column_detail_list()
    new_table_name = column_decoder.write_back_sqlite(detail_list, disinherit_columns=['not_null', 'is_pk'])
    print("raw_sql\n", column_handler.raw_sql)
    print('new_table_name:' + new_table_name)
    input(f"Make sure the column info of {new_table_name} is correct in sqlite\n"
          f"Press Enter to produce SDM and SQL: ")

with SdmProducer('tables_information.db') as sdm_producer:
    ddl_text = sdm_producer.get_create_dll(new_table_name)
    sdm_content = sdm_producer.get_sdm_content(f'wf_{new_table_name}', new_table_name)
    sensitive_dict = sdm_producer.get_sensitive_column(new_table_name)
    sdm_producer.write_ddl_txt(f'{new_table_name}_ddl.sql', ddl_text)
    sdm_producer.write_sdm_csv(f'{new_table_name}_sdm.csv', sdm_content)
    sdm_producer.write_sensitive_check(f'{new_table_name}_sensitive.csv', sensitive_dict)
