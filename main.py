from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
import databaseManager as dbHandler


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
    # Check answer
    if request.method == 'POST':
        
        # Answer submitted by user
        user_answer = request.form.get('user_answer', '').strip().lower()
        
        # Answer stored in database
        actual_answer = request.form.get('actual_answer', '').strip().lower()
        alert_message = 'incorrect' if user_answer != actual_answer else 'correct'
        print(actual_answer,user_answer)

        return render_template('play.html', quiz=request.form.get('quiz'), answer=request.form.get('actual_answer'), alert_message=alert_message)
# grabbing specific rows from database
    questionRow = dbHandler.getQ() 
    question = questionRow[1]
    answer = questionRow[3]

    print(question[1]) 
    return render_template('play.html', quiz=question, answer=answer)


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

