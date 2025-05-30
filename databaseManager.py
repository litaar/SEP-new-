import sqlite3 as sql

def getQ():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM QuizQ ORDER BY RANDOM() LIMIT 1")
    ans = cur.fetchone()
    con.close()
    print(ans)
    return ans