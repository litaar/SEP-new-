import sqlite3 as sql

def getAnswer():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM QuizQ ORDER BY RANDOM() LIMIT 1")
    ans = cur.fetchone()
    con.close()
    print(QuizQ)
    return QuizQ