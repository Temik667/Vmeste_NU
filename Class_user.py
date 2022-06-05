import string
import sqlite3
from parse import *

# conn = sqlite3.connect('vmeste.db')
# c = conn.cursor()
# c.execute("""CREATE TABLE vmeste (
#         id INTEGER,
#         name TEXT,
#         sex TEXT,
#         photo BIT,
#         first_fail INTEGER,
#         second_fail INTEGER
# )""")

# conn.commit()
# c.close()

class sql_class():
    
    conn = sqlite3.connect('vmeste.db', check_same_thread=False)
    c = conn.cursor()

    @classmethod 
    def add_user(cls, new_user_id, new_name, new_sex, new_photo) -> None:
        parameters = new_user_id, new_name, new_sex, new_photo, 0, 0
        cls.c.execute("""INSERT INTO vmeste VALUES (?, ?, ?, ?, ?, ?)""", parameters)
        cls.conn.commit()

    @classmethod
    def delete_user(cls, user_id) -> None:
        cls.c.execute("""DELETE FROM vmeste WHERE id = {}""".format(user_id))
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
    def find_rides(cls, user_id) -> int:
        cls.c.execute("""SELECT rides FROM vmeste WHERE id = {}""".format(str(user_id)))
        rides = str(cls.c.fetchone())
        r = parse("({},)", rides)
        return int(r[0])
    
    @classmethod
    def find_first_fail(cls, user_id) -> int:
        cls.c.execute("""SELECT first_fail FROM vmeste
        WHERE id = {}""".format(user_id))
        result = str(cls.c.fetchone())
        r = parse("({},)", result)
        return int(r[0])
    
    @classmethod
    def find_second_fail(cls, user_id) -> int:
        cls.c.execute("""SELECT second_fail FROM vmeste
        WHERE id = {}""".format(user_id))
        result = str(cls.c.fetchone())
        r = parse("({},)", result)
        return int(r[0])

    @classmethod
    def is_new(cls, user_id) -> bool:
        cls.c.execute("""SELECT id FROM vmeste WHERE id = {}""".format(str(user_id)))
        result = str(cls.c.fetchone())
        if result == 'None':
            return True
        else:
            return False
    
    @classmethod
    def update_name(cls, user_id, new_name) -> None:
        cls.c.execute("""UPDATE vmeste 
        SET name = (?)
        WHERE id = (?)""", (new_name, user_id))
        cls.conn.commit()
    
    @classmethod
    def update_sex(cls, user_id, new_sex) -> None:
        cls.c.execute("""UPDATE vmeste 
        SET sex = (?)
        WHERE id = (?)""", (new_sex, user_id))
        cls.conn.commit()

    @classmethod
    def update_photo(cls, user_id, new_photo) -> None:
        cls.c.execute("""UPDATE vmeste 
        SET photo = (?)
        WHERE id = (?)""", (new_photo, user_id))
        cls.conn.commit()
        
    @classmethod
    def add_fail(cls, user_id) -> None:
        if cls.find_first_fail(user_id) == 1:
            cls.c.execute("""UPDATE vmeste
            SET second_fail = (?)
            WHERE id = (?)""", (1, user_id))
            cls.conn.commit()
            return
        cls.c.execute("""UPDATE vmeste
            SET first_fail = (?)
            WHERE id = (?)""", (1, user_id))
        cls.conn.commit()
    
    @classmethod
    def remove_fail(cls, user_id) -> None:
        if cls.find_second_fail(user_id) == 1:
            cls.c.execute("""UPDATE vmeste
            SET second_fail = (?)
            WHERE id = (?)""", (0, user_id))
            cls.conn.commit()
            return
        cls.c.execute("""UPDATE vmeste
            SET first_fail = (?)
            WHERE id = (?)""", (0, user_id))
        cls.conn.commit()