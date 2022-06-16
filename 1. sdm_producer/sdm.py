from datetime import date
from db import DataBase
import csv
from os import path
# test
from column_info import DecodeColumnHandler
from raw_sql import ColumnTextHandler

today = date.today().strftime("%Y%m%d")


class SdmContent:
    def __init__(self, wf_name, new_table_name, new_column_name, new_column_type,
                 is_pk, partition, not_null, index, seq, description, group_num, source_table_name, source_column_name,
                 source_data_type):
        self.wf_name = wf_name
        self.new_table_name = new_table_name
        self.new_column_name = new_column_name
        self.new_column_type = new_column_type
        self.is_pk = is_pk
        self.partition = partition
        self.not_null = not_null
        self.index = index
        self.seq = seq
        self.description = description
        self.group_num = group_num
        self.source_table_name = source_table_name
        self.source_column_name = source_column_name
        self.source_data_type = source_data_type


class SdmProducer(DataBase):
    def __init__(self, db_location):
        super().__init__(db_location)

    def get_create_dll(self, table_name):
        query = 'select column_name, data_type, not_null, description from table_info where table_name=? order by seq;'
        self.cur.execute(query, (table_name,))
        rows = self.cur.fetchall()
        ddl_contents = []
        comment_sentences = []

        for row in rows:
            row = [value if value else "" for value in row]
            column_name = row[0]
            data_type = row[1]
            not_null = row[2]
            if not_null == 'Y':
                not_null = 'not null'
            description = row[3]

            ddl_content = ' '.join((column_name, data_type, not_null))
            ddl_contents.append(ddl_content)
            comment_sentence = f"comment on column mx.{table_name}.{column_name} is '{description}';"
            comment_sentences.append(comment_sentence)

        table_contents_str = ",\n\t".join(ddl_contents)
        create_table_str = f'create table MX.{table_name}(\n\t' \
                           f'{table_contents_str});'
        comment_sentence_str = '\n'.join(comment_sentences)

        return create_table_str + '\n' + comment_sentence_str

    def get_sdm_content(self, wf_name, target_table_name):
        query = f"select '{wf_name}', n.table_name, n.column_name, n.data_type, null, null, n.not_null, " \
                f"null, n.seq, n.description, null, o.table_name, o.column_name, o.data_type from table_info n " \
                f"left join table_info o on n.source_table=o.table_name and n.source_column=o.column_name " \
                f"where n.table_name='{target_table_name}' " \
                f"order by n.seq;"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        sdm_rows = []
        for row in rows:
            sdm_row = SdmContent(row[0], row[1], row[2], row[3], row[4], row[5],
                                 row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            sdm_rows.append(sdm_row)
        return sdm_rows

    def get_sensitive_column(self, table_name):
        query = "SELECT sensitive_info, GROUP_CONCAT(column_name, ', ')  from sensitive_columns " \
                "where column_name in (select column_name from table_info where table_name = ?) " \
                "group by sensitive_info;"
        self.cur.execute(query, (table_name,))
        rows = self.cur.fetchall()
        csv_dict = {'TABLE_NAME': table_name}
        if rows:
            for row in rows:
                sensitive_info = row[0]
                columns = row[1]
                csv_dict[sensitive_info] = columns

        return csv_dict

    @staticmethod
    def write_sdm_csv(csv_file: str, sdm_rows: list[SdmContent]):
        sdm_header = list(sdm_rows[0].__dict__.keys())
        rows = [sdm_row.__dict__ for sdm_row in sdm_rows]
        if not path.isfile(csv_file):
            with open(csv_file, mode='w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=sdm_header)
                writer.writeheader()
                writer.writerows(rows)
                csv_file.write('\n')
        else:
            with open(csv_file, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=sdm_header)
                writer.writerows(rows)
                csv_file.write('\n')

    @staticmethod
    def write_ddl_txt(file_name: str, file_content: str):
        with open(file_name, mode='a', newline='') as ddl_file:
            ddl_file.write(file_content)
            ddl_file.write('\n---------\n')

    @staticmethod
    def write_sensitive_check(csv_name: str, content_dict: dict[str, str]):
        header = ['TABLE_NAME', 'IDN', 'NAME', 'BIRTH', 'PHONE', 'ADDRESS', 'MAIL', 'BANK_ACCOUNT']
        if not path.isfile(csv_name):
            with open(csv_name, mode='w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=header)
                writer.writeheader()
                writer.writerow(content_dict)
        else:
            with open(csv_name, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=header)
                writer.writerow(content_dict)

if __name__ == '__main__':
    test_sql = input_raw_sql = """INSERT INTO TMP_TEST_PART1
select decode(a.sno,null,'0',a.sno) sno, c.ftyp, c.ciid, b.idn, b.brdte, b.name, trim(b.hmk) hmk, c.uno, c.unock, c.acno, c.range, start_date, end_date,
TO_DATE('$$w_Exch_Date','YYYYMMDD') AS DATA_EXCH_DATE
from MRT_TEST_EXT a, MRT_TEST_TABLEB b ,MRT_TEST_TABLEC c     """
    column_handler = ColumnTextHandler(test_sql)
    with DecodeColumnHandler('tables_information.db', column_handler) as column_decoder:
        detail_list = column_decoder.get_column_detail_list()
        new_table_name = column_decoder.write_back_sqlite(detail_list, disinherit_columns=['not_null', 'is_pk'])
        print('new_table_name:' + new_table_name)

    with SdmProducer('tables_information.db') as sdm_producer:
        ddl_text = sdm_producer.get_create_dll(new_table_name)
        sdm_content = sdm_producer.get_sdm_content('wf_test', new_table_name)
        sdm_producer.write_ddl_txt('test_ddl.sql', ddl_text)
        sdm_producer.write_sdm_csv('test_sdm.csv', sdm_content)


