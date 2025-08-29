import sqlite3 as sql

def retrieveUsers(username, password):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    con.close()

    if row is None:
        return False

    stored_password = row[0]
    return stored_password == password   # 🔐 (later: use bcrypt)
