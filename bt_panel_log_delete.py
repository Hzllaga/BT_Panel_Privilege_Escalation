import sqlite3

conn = sqlite3.connect('C:/BtSoft/panel/data/default.db')
c = conn.cursor()
sql = "select id from logs"
cursor = c.execute(sql)
for log in cursor.fetchall():
    log_id = log[0]
    sql = f"delete from logs where id = {log_id}"
    c.execute(sql)
    conn.commit()
conn.close()
