import json
import hashlib
import os
import sys

class UserManager:
    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.users_file = os.path.join(sys._MEIPASS, 'users.json')
        else:
            self.users_file = 'users.json'
        self.load_users()
    
    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # 创建默认管理员账户
            self.users = {
                'admin': self._hash_password('admin123')
            }
            self.save_users()
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)
    
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username, password):
        if username in self.users:
            return self.users[username] == self._hash_password(password)
        return False
    
    def add_user(self, username, password):
        if username not in self.users:
            self.users[username] = self._hash_password(password)
            self.save_users()
            return True
        return False 