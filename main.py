# ----------------------
# imports
# ----------------------
from flask import Flask, redirect, render_template, request, session, g
from flask_wtf.csrf import CSRFProtect
from flask_csp.csp import csp_header
import sqlite3
import logging
import databaseManager as dbHandler
import userManagement as um

# ----------------------
# App setup
# ----------------------
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"  # keep ONE consistent key
csrf = CSRFProtect(app)

# Database setup
DATABASE = "databaseFiles/database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ----------------------
# Logging setup
# ----------------------
app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# ----------------------
# Routes
# ----------------------

# Root route → send to login if not logged in
@app.route("/")
def root():
    if "user_id" in session:
        print("User logged in:", session["user_id"])
        return redirect("/index")  # user already logged in → dashboard
    return redirect("/login")      # not logged in → login page

# Dashboard (protected)
@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html", username=session["user_id"])

# --- Register ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("databaseFiles/database.db")
        cur = conn.cursor()

        # check if username already exists
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            conn.close()
            return "❌ Username already taken"

        # insert new user
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/login")
    return render_template("register.html")

# -- Login -- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        logout()
        username = request.form["username"]
        password = request.form["password"]

        isLoggedIn = um.retrieveUsers(username, password)
        if isLoggedIn:
            session["user_id"] = username
            return redirect("/index")   # go to dashboard
        else:
            return "❌ Invalid username or password"
    
    return render_template("login.html")

# --- Menu ---
@app.route("/menu")
def menu():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("menu.html", username=session["user_id"])

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- Play page ---
@app.route("/play", methods=["GET", "POST"])
def play():
    # Protect route: force login
    if "user_id" not in session:
        return redirect("/login")

    # Initialize session vars if not set
    if "score" not in session:
        session["score"] = 0
    if "asked_ids" not in session:
        session["asked_ids"] = []

    # Handle form submission (POST)
    if request.method == "POST":
        user_answer = request.form.get("user_answer", "").strip().lower()
        actual_answer = request.form.get("actual_answer", "").strip().lower()
        quiz = request.form.get("quiz")

        if user_answer == actual_answer:
            session["score"] += 1
            alert_message = "✅ Correct!"
        else:
            alert_message = f"❌ Incorrect! The answer was {actual_answer}"

        return render_template(
            "play.html",
            quiz=quiz,
            answer=actual_answer,
            alert_message=alert_message,
            score=session["score"],
            finished=False,
        )

    # GET: fetch new question
    row = dbHandler.getQExclude(session["asked_ids"])

    if not row:  # no more questions
        final_score = session["score"]
        total_questions = len(session["asked_ids"])
        session.pop("score", None)
        session.pop("asked_ids", None)

        return render_template(
            "play.html",
            quiz=f"🎉 You finished all {total_questions} questions!",
            answer="",
            alert_message=f"Your final score: {final_score}/{total_questions}",
            score=final_score,
            finished=True,
        )

    qid, name, qtype, answer, category = row
    session["asked_ids"].append(qid)

    return render_template(
        "play.html",
        quiz=name,
        answer=answer,
        alert_message="",
        score=session["score"],
        finished=False,
    )

# Example CSRF-protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("form.html")
    return render_template("form.html")

# Extra pages
@app.route("/play-notes")
def play_notes():
    return render_template("play.html")


#Music terms quizzer
@app.route("/play-terms", methods=["GET", "POST"])
def play_terms():
    if "user_id" not in session:
        return redirect("/login")

    if "score_terms" not in session:
        session["score_terms"] = 0
    if "asked_terms" not in session:
        session["asked_terms"] = []

    alert_message = ""
    # Handle form submission
    if request.method == "POST":
        selected = request.form.get("option")
        correct = request.form.get("correct_option")
        if selected == correct:
            session["score_terms"] += 1
            alert_message = "✅ Correct!"
        else:
            alert_message = f"❌ Incorrect! The answer was {correct}"

    # GET: fetch new question
    q = dbHandler.getTermsQMC(session["asked_terms"])
    if not q:
        final_score = session["score_terms"]
        session.pop("score_terms", None)
        session.pop("asked_terms", None)
        return render_template(
            "terms.html",
            quiz="🎉 All questions finished!",
            alert_message=f"Your final score: {final_score}",
            score=final_score,
            finished=True,
        )

    qid, question, correct, choices = q
    session["asked_terms"].append(qid)

    return render_template(
        "terms.html",
        quiz=question,
        choices=choices,
        answer=correct,
        alert_message=alert_message,
        score=session["score_terms"],
        finished=False,
    )



# CSP report endpoint
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"

# ----------------------
# Run app
# ----------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
