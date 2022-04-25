import re
from pprint import pprint
from typing import Optional
from utils.wash_sql_query import wash_sql_query, convert_half_width
from utils.bracket_excluded_char_split import bracket_excluded_char_split


class RawSqlHandler:
    def __init__(self, raw_sql: str):
        self.raw_sql = convert_half_width(wash_sql_query(raw_sql))
        self.confirm_basic_pattern()
        self.new_table_name: Optional[str] = None
        self.new_column_name_list: Optional[list[str]] = None
        self.columns_text_list: Optional[list[str]] = None
        self.tables_text_list: Optional[list[str]] = None
        self.get_new_table_name()
        self.get_new_column_name_list()
        self.get_columns_text_list()
        self.get_tables_text_list()

    def confirm_basic_pattern(self):
        basic_pattern = r"^(insert\s+into\s+.+?)?\(?select.+?from.+\)?"
        assert re.fullmatch(basic_pattern, self.raw_sql, re.IGNORECASE | re.DOTALL), \
            f'raw_sql need to match basic pattern:{basic_pattern}'

    def get_new_table_name(self):
        new_table_match = re.search(r"insert\s+into\s+(\w+)", self.raw_sql, re.IGNORECASE | re.DOTALL)
        if new_table_match:
            self.new_table_name = new_table_match.group(1)
        else:
            self.new_table_name = 'check yourself'

    def get_new_column_name_list(self):
        new_columns_match = re.search(r"insert\s+into\s+\w+\s*\((.+)\)", self.raw_sql, re.I)
        if new_columns_match:
            self.new_column_name_list = new_columns_match.group(1).split(',')
            self.new_column_name_list = list(map(str.strip, self.new_column_name_list))
        else:
            self.new_column_name_list = None

    def get_columns_text_list(self):
        column_sentence = re.search(r"(?<=select)(.|\s)+?(?=from)", self.raw_sql, re.I).group(0)
        self.columns_text_list = [column_text.strip()
                                  for column_text in bracket_excluded_char_split(column_sentence, ",")]

    def get_tables_text_list(self):
        table_sentence = re.search(r"(?<=from)(.+)?\)?", self.raw_sql, re.I).group(1)
        self.tables_text_list = [table_text.strip() for table_text in table_sentence.split(',')]


class TableTextHandler(RawSqlHandler):
    def __init__(self, raw_sql):
        super().__init__(raw_sql)
        self.all_tables: Optional[list[str]] = None
        self.all_alias_pairs: Optional[dict[str, str]] = None
        self.get_all_tables()
        self.get_alias_pairs()

    def get_all_tables(self):
        self.all_tables = [re.split(r'[ ]+', table_text)[0]
                           for table_text
                           in self.tables_text_list]

    def get_alias_pairs(self):
        self.all_alias_pairs = {}
        for table_text in self.tables_text_list:
            table_parts = re.split(r'[ ]+', table_text)
            if len(table_parts) == 2:
                self.all_alias_pairs[table_parts[1]] = table_parts[0]


class ColumnTextInfo:
    def __init__(self, raw_column_text, all_alias_pairs):
        self.raw_column_text: str = raw_column_text
        self.source_column_name: str = 'unique_column_name'
        self.source_table_name: str = 'default_table'
        self.new_column_name: str = 'same_as_source_column_name'
        self.use_alias: bool = False
        self.use_function: bool = False
        self.use_decode: bool = False
        self.use_contact: bool = False
        self.__update_column_status(all_alias_pairs)

    def __detect_function(self):
        if "(" in self.raw_column_text:
            self.use_function = True

    def __detect_decode(self):
        if re.search(r'decode\(.+?\)', self.raw_column_text):
            self.use_decode = True

    def __detect_alias(self, all_alias_pairs: dict[str, str]):
        for alias_name in all_alias_pairs.keys():
            columns_parts = re.search(r'\b(' + alias_name + r')\.(\w+)\b', self.raw_column_text, flags=re.IGNORECASE)
            if columns_parts:
                self.use_alias = True
                self.source_table_name = all_alias_pairs[alias_name]
                self.source_column_name = columns_parts.group(2)

    def __detect_new_column_name(self):
        column_text = re.sub(r'[ ]+', ' ', self.raw_column_text).strip()
        if match_parts := re.search(r".+? as (\w+)", column_text, re.I):
            self.new_column_name = match_parts.group(1)
        elif len(match_parts := bracket_excluded_char_split(column_text, ' ')) >= 2:
            self.new_column_name = match_parts[-1]

    def __detect_contact_operator(self):
        if '||' in self.raw_column_text:
            self.use_contact = True

    def __detect_self_defined_column(self):
        self_defined_columns = ['DATA_EXCH_DATE', 'MX_SEQ']
        for self_defined_name in self_defined_columns:
            if self_defined_name in self.raw_column_text:
                self.source_column_name = 'no_source_column'
                self.source_table_name = 'no_source_table'
                self.new_column_name = self_defined_name

    def __update_column_status(self, all_alias_pairs):
        self.__detect_function()
        self.__detect_decode()
        self.__detect_contact_operator()
        self.__detect_alias(all_alias_pairs)
        self.__detect_new_column_name()
        self.__detect_self_defined_column()


class ColumnTextHandler(TableTextHandler):
    def __init__(self, raw_sql):
        super().__init__(raw_sql)
        self.columns_info_list: list[ColumnTextInfo] = None
        self.get_columns_info_list()
        self.update_new_column_name()

    def get_columns_info_list(self):
        self.columns_info_list = [ColumnTextInfo(raw_column_text, self.all_alias_pairs)
                                  for raw_column_text in self.columns_text_list]

    def update_new_column_name(self):
        if self.new_column_name_list:

            assert len(self.new_column_name_list) == len(self.columns_info_list), \
                "the length of new column name and selected column doesn't match"

            for seq, new_column_name in enumerate(self.new_column_name_list):
                self.columns_info_list[seq].new_column_name = new_column_name


if __name__ == '__main__':
    test_sql = input_raw_sql = """ INSERT INTO TMP_TEST_PART1
select decode(a.sno,null,'0',a.sno) sno, c.ftyp, c.ciid, b.idn, b.brdte, b.name, trim(b.hmk) hmk, c.uno, c.unock, c.acno, c.range, start_date, end_date,
TO_DATE('$$w_Exch_Date','YYYYMMDD') AS DATA_EXCH_DATE
from MRT_TEST_EXT a, MRT_TEST_TABLEB b ,MRT_TEST_TABLEC c    """
    t_obj = ColumnTextHandler(test_sql)
    print(t_obj)
    pprint(vars(t_obj))
    for t in t_obj.columns_info_list:
        print(t.__dict__)
