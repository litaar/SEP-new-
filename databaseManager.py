import sqlite3 as sql
import random

def getTermsQMC(exclude_ids=[]):
    """Get a random musical terms multiple-choice question"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    if exclude_ids:
        placeholders = ",".join("?" * len(exclude_ids))
        query = f"SELECT * FROM QuizQ WHERE category='terms' AND id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1"
        cur.execute(query, exclude_ids)
    else:
        cur.execute("SELECT * FROM QuizQ WHERE category='terms' ORDER BY RANDOM() LIMIT 1")

    row = cur.fetchone()
    con.close()

    if row:
        # row structure: id, question, correct_answer, wrong1, wrong2, wrong3, category
        qid, question, correct, w1, w2, w3, category = row
        choices = [correct, w1, w2, w3]
        random.shuffle(choices)
        return qid, question, correct, choices
    return None

def getQ():
    """Get a random question from QuizQ table"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM QuizQ ORDER BY RANDOM() LIMIT 1")
    ans = cur.fetchone()
    con.close()
    print(ans)
    return ans




def getNotesQ():
    """Get a random note identification question from QuizQ table"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    # If you have a category/type column to filter note questions
    # cur.execute("SELECT * FROM QuizQ WHERE category='notes' ORDER BY RANDOM() LIMIT 1")
    # Otherwise, get any random question
    cur.execute("SELECT * FROM QuizQ ORDER BY RANDOM() LIMIT 1")
    ans = cur.fetchone()
    con.close()
    print("Notes question:", ans)
    return ans

def getTableStructure():
    """Debug function to see the structure of QuizQ table"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("PRAGMA table_info(QuizQ)")
    columns = cur.fetchall()
    con.close()
    return columns

def getAllQuestions():
    """Get all questions for debugging"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM QuizQ LIMIT 5")  # Get first 5 questions
    questions = cur.fetchall()
    con.close()
    return questions

def getQExclude(exclude_ids):
    """Get a random question not in exclude_ids"""
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()

    if exclude_ids:
        placeholders = ",".join("?" * len(exclude_ids))
        query = f"SELECT * FROM QuizQ WHERE id NOT IN ({placeholders}) ORDER BY RANDOM() LIMIT 1"
        cur.execute(query, exclude_ids)
    else:
        cur.execute("SELECT * FROM QuizQ ORDER BY RANDOM() LIMIT 1")

    ans = cur.fetchone()
    con.close()
    return ans
