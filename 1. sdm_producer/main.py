from raw_sql import ColumnTextHandler
from column_info import DecodeColumnHandler
from sdm import SdmProducer, write_sdm_csv, write_ddl_txt, write_sensitive_check

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
    print('new_table_name:' + new_table_name)

with SdmProducer('tables_information.db') as sdm_producer:
    ddl_text = sdm_producer.get_create_dll(new_table_name)
    sdm_content = sdm_producer.get_sdm_content('wf_test', new_table_name)
    sensitive_dict = sdm_producer.get_sensitive_column(new_table_name)
    write_ddl_txt('test_ddl.sql', ddl_text)
    write_sdm_csv('test_sdm.csv', sdm_content)
    write_sensitive_check('test_sensitive.csv', sensitive_dict)
