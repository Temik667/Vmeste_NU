import string
import os


class User:
    photo = ""
    def __init__(self, user_id) -> None:
        self.user_id = user_id
        self.name = 'Temirlan' # SQL
        self.sex = 'Male' # SQL
        self.photo = user_id + '_photo.jpg' #change later
    
    def is_New(self) -> bool:
        if self.user_id == 1234567890: #SQL
           return False
        else:
            return True
    
    #SQL!!!
    """Registration process"""
    def reg_user_name(self, new_name) -> None:
        self.name = new_name
    
    def reg_user_sex(self, new_sex) -> None:
        self.sex = new_sex
    
    """EDIT PHOTO AND BIO"""
    def find_photo(self) -> string:
        return self.user_id() + '_photo.jpg'
    
    def delete_photo(self) -> None:
        os.remove(self.find_photo(self.user_id))
    
    def change(self, new_name, new_sex) -> None:
        self.name = new_name
        self.sex = new_sex
        