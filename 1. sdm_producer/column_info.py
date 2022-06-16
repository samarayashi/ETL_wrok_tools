import re
from datetime import date
import logging

from db import DataBase
from raw_sql import ColumnTextHandler

today = date.today().strftime("%Y%m%d")


class ColumnDetail:
    def __init__(self, new_table_name, new_column_name, source_table_name, source_column_name,
                 data_type, is_pk, not_null, description, notes, raw_text):
        self.new_table_name = new_table_name
        self.new_column_name = new_column_name
        self.source_table_name = source_table_name
        self.source_column_name = source_column_name
        self.data_type = data_type
        self.is_pk = is_pk
        self.not_null = not_null
        self.description = description
        self.notes = notes
        self.raw_text = raw_text


class DecodeColumnHandler(DataBase):
    def __init__(self, db_location, column_handler: ColumnTextHandler):
        super().__init__(db_location)
        self.column_handler = column_handler
        self.__update_handler_content()

    def __update_handler_content(self):
        self.__upper_column_table_name()
        self.__update_new_table_name()
        self.__update_unique_column()
        self.__update_new_column()

    def __upper_column_table_name(self):
        self.column_handler.new_table_name = self.column_handler.new_table_name.upper()
        for column_info in self.column_handler.columns_info_list:
            column_info.source_column_name = column_info.source_column_name.upper()
            column_info.source_table_name = column_info.source_table_name.upper()
            column_info.new_column_name = column_info.new_column_name.upper()

    def __update_new_table_name(self):
        if self.column_handler.new_table_name == 'CHECK YOURSELF':
            self.column_handler.new_table_name = input("input new table name: ")

    def __update_unique_column(self):
        tables = ','.join(f"'{table}'" for table in self.column_handler.all_tables)
        query = f"select table_name, column_name from " \
                f"( " \
                f"SELECT table_name, column_name, count() over(PARTITION by column_name) c_number from table_info " \
                f"where table_name in ({tables}) " \
                f")tmp " \
                f"where c_number=1"
        self.cur.execute(query)
        rows = self.cur.fetchall()
        unique_column_dict = {row[1]: row[0] for row in rows}
        for column_info in self.column_handler.columns_info_list:
            if column_info.source_column_name == 'UNIQUE_COLUMN_NAME':
                try:
                    column_info.source_column_name = next(unique_column
                                                          for unique_column in unique_column_dict.keys()
                                                          if
                                                          re.search(r'\b' + unique_column + r'\b',
                                                                    column_info.raw_column_text, flags=re.IGNORECASE))
                    column_info.source_table_name = unique_column_dict[column_info.source_column_name]

                except StopIteration as err:
                    logging.warning(f"column:{column_info.raw_column_text} doesn't match existed table")
                    column_info.source_column_name = 'no_source_column'
                    column_info.source_table_name = 'no_source_table'

    def __update_new_column(self):
        for column_info in self.column_handler.columns_info_list:
            if column_info.new_column_name == 'SAME_AS_SOURCE_COLUMN_NAME':
                if column_info.source_column_name == 'no_source_column':
                    column_info.new_column_name = 'check_your_self'
                else:
                    column_info.new_column_name = column_info.source_column_name

    def change_column_handler(self, new_column_handler: ColumnTextHandler):
        assert isinstance(new_column_handler, ColumnTextHandler), 'only accept ColumnTextHandler'
        setattr(self, 'column_handler', new_column_handler)
        self.__update_handler_content()

    def get_column_detail_list(self):
        detail_list = []
        for column_info in self.column_handler.columns_info_list:
            source_table_name = column_info.source_table_name.upper()
            source_column_name = column_info.source_column_name.upper()
            query = f"SELECT table_name, column_name, data_type, is_pk, not_null, description " \
                    f"FROM table_info WHERE table_name='{source_table_name}' " \
                    f"AND column_name='{source_column_name}';"
            self.cur.execute(query)
            row = self.cur.fetchone()
            notes_status = [column_info.use_function, column_info.use_decode, column_info.use_contact]
            notes_content = ['function', 'decode', 'contact']
            notes = ', '.join(content for (content, status) in zip(notes_content, notes_status) if status)

            if row:
                column_detail = ColumnDetail(self.column_handler.new_table_name, column_info.new_column_name, row[0],
                                             row[1], row[2], row[3], row[4], row[5],
                                             notes, column_info.raw_column_text)
            elif column_info.new_column_name == 'MX_SEQ':
                column_detail = ColumnDetail(self.column_handler.new_table_name, column_info.new_column_name,
                                             'no_source_table', 'no_source_column', 'NUMBER', '',
                                             '', '排序序號', notes,
                                             column_info.raw_column_text)
            elif column_info.new_column_name == 'DATA_EXCH_DATE':
                column_detail = ColumnDetail(self.column_handler.new_table_name, column_info.new_column_name,
                                             'no_source_table', 'no_source_column', 'DATE', '',
                                             'Y', 'ETL載入日期', notes,
                                             column_info.raw_column_text)
            elif column_info.source_table_name == 'no_source_table':
                column_detail = ColumnDetail(self.column_handler.new_table_name, column_info.new_column_name,
                                             'no_source_table', 'no_source_column', 'check_your_self', '',
                                             'check_your_self', 'check_your_self', notes,
                                             column_info.raw_column_text)
            else:
                column_detail = ColumnDetail(self.column_handler.new_table_name, column_info.new_column_name,
                                             'check_your_self', 'check_your_self', 'check_your_self', '',
                                             'check_your_self', 'check_your_self', notes,
                                             column_info.raw_column_text)
            detail_list.append(column_detail)
        return detail_list

    def write_back_sqlite(self, detail_list: list[ColumnDetail], disinherit_columns: list[str] = None) -> str:
        row_value_list = []
        for seq, column_detail in enumerate(detail_list, 1):

            if disinherit_columns:
                for disinherit_column in disinherit_columns:
                    column_detail.__setattr__(disinherit_column, '')

            values = (column_detail.new_table_name, column_detail.new_column_name, column_detail.data_type,
                      column_detail.is_pk, column_detail.not_null, seq, column_detail.description,
                      column_detail.source_table_name, column_detail.source_column_name,
                      column_detail.raw_text, column_detail.notes, today)
            row_value_list.append(values)

        in_params = ','.join('?' for _ in row_value_list[0])
        query = f'insert into table_info(table_name, column_name, data_type, is_pk, not_null, seq, description, ' \
                f'source_table, source_column, raw_text, notes, update_date) ' \
                f"values({in_params});"
        self.cur.executemany(query, row_value_list)
        self.con.commit()

        # make sure data_exch_date is not null
        query = "update table_info set not_null = 'Y' WHERE column_name = 'DATA_EXCH_DATE' and table_name = ? "
        self.cur.execute(query, (column_detail.new_table_name,))
        self.con.commit()
        return column_detail.new_table_name


if __name__ == '__main__':
    test_sql = input_raw_sql = """INSERT INTO TMP_TEST_PART1
select decode(a.sno,null,'0',a.sno) sno, c.ftyp, c.ciid, b.idn, b.brdte, b.name, trim(b.hmk) hmk, c.uno, c.unock, c.acno, c.range, start_date, end_date,
TO_DATE('$$w_Exch_Date','YYYYMMDD') AS DATA_EXCH_DATE
from MRT_TEST_EXT a, MRT_TEST_TABLEB b ,MRT_TEST_TABLEC c   """
    column_handler = ColumnTextHandler(test_sql)
    with DecodeColumnHandler('tables_information.db', column_handler) as column_decoder:
        detail_list = column_decoder.get_column_detail_list()
        for detail in detail_list:
            print(detail.__dict__)
        new_table_name = column_decoder.write_back_sqlite(detail_list, disinherit_columns=['not_null', 'is_pk'])
        print('new_table_name:' + new_table_name)
