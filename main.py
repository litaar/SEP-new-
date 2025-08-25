from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
import databaseManager as dbHandler

# Session
from flask import Flask, render_template, request, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # needed for sessions



# Connect to database
DATABASE = 'your_database_name.db'  # Change this to your DB file

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for CSRF protection




@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

csrf = CSRFProtect(app)

from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging


# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)


# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")

# create method for user to play quiz

@app.route("/play", methods=["GET", "POST"])
def play():
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
            finished=False
        )

    # Handle new question (GET)
    row = dbHandler.getQExclude(session["asked_ids"])

    if not row:  # No more questions left
        final_score = session["score"]
        total_questions = len(session["asked_ids"])

        # Reset for next round
        session.pop("score", None)
        session.pop("asked_ids", None)

        return render_template(
            "play.html",
            quiz=f"🎉 You finished all {total_questions} questions!",
            answer="",
            alert_message=f"Your final score: {final_score}/{total_questions}",
            score=final_score,
            finished=True
        )

    # Otherwise, show next question
    qid, name, qtype, answer, category = row
    session["asked_ids"].append(qid)

    return render_template(
        "play.html",
        quiz=name,      # question text
        answer=answer,  # correct answer
        alert_message="",
        score=session["score"],
        finished=False
    )


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("/form.html")
    else:
        return render_template("/form.html")


# Adding route functions for cards
@app.route('/play-notes')
def play_notes():
    # You can customize what you pass to the template
    return render_template('play.html')

@app.route('/play-terms')
def play_terms():
    # You can customize what you pass to the template
    return render_template('terms.html')

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)