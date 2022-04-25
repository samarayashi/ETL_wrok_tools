import sqlite3


class DataBase:
    def __init__(self, db_location):
        self.con = sqlite3.connect(db_location)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()
