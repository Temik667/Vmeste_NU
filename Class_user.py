import string
import os
import sqlite3
from parse import *

#         TABLE:
#         id INTEGER,
#         name TEXT,
#         sex TEXT,
#         photo BIT

class sql_class():
    
    conn = sqlite3.connect('vmeste.db', check_same_thread=False)
    c = conn.cursor()

    @classmethod
    def close_db():
    
    @classmethod # int, str, str, int
    def add_user(cls, new_user_id, new_name, new_sex, new_photo) -> None:
        parameters = new_user_id, new_name, new_sex, new_photo
        cls.c.execute("""INSERT INTO vmeste VALUES (?, ?, ?, ?)""", parameters)
        cls.conn.commit()

    @classmethod
    def find_name(cls, user_id) -> string:
        cls.c.execute("""SELECT name FROM vmeste WHERE id = {}""".format(str(user_id)))
        name = str(cls.c.fetchone())
        r = parse("('{}',)", name)
        return r[0]
    
    @classmethod 
    def find_sex(cls, user_id) -> string:
        cls.c.execute("""SELECT sex FROM vmeste WHERE id = {}""".format(str(user_id)))
        sex = str(cls.c.fetchone())
        r = parse("('{}',)", sex)
        return r[0]
    
    @classmethod
    def has_photo(cls, user_id) -> string:
        cls.c.execute("""SELECT photo FROM vmeste WHERE id = {}""".format(str(user_id)))
        photo = str(cls.c.fetchone())
        r = parse("({},)", photo)
        if r[0] == '0':
            return False
        return True

    @classmethod
    def is_new(cls, user_id) -> bool:
        cls.c.execute("""SELECT id FROM vmeste WHERE id = {}""".format(str(user_id)))
        result = str(cls.c.fetchone())
        if result == 'None':
            return True
        return True
    
    @classmethod
    def update_info(cls, user_id, new_name, new_sex, new_photo) -> None:
        cls.c.execute("""UPDATE vmeste 
        SET name = ?, sex = ?, photo = ? 
        where id = {}""".format(user_id), (new_name, new_sex, new_photo))
        cls.conn.commit()
