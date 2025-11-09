from flask import Flask, render_template, redirect, url_for, session
import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from pathlib import Path

from datetime import timedelta




env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)






app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

app.permanent_session_lifetime = timedelta(minutes=5)


app.config.update(
    SESSION_COOKIE_NAME='flask_sso_session',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

@app.before_request
def make_session_permanent():
    session.permanent = True





oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    server_metadata_url=os.environ.get("AUTH0_DOMAIN") + "/.well-known/openid-configuration",
    client_kwargs={
        'scope': 'openid profile email',
    },

)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri="http://127.0.0.1:5000/callback")
    #return auth0.authorize_redirect(redirect_uri=os.environ["AUTH0_CALLBACKURL"])


@app.route("/callback")
def callback():
    print("Session before callback:", dict(session))
    token = auth0.authorize_access_token()
    nonce = token.get("nonce") or session.get("nonce")  # fetch nonce
    userinfo = auth0.parse_id_token(token, nonce=nonce)  # pass nonce here
    session["user"] = userinfo
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("https://dev-sjvpzk870wg0apjg.us.auth0.com/v2/logout?returnTo=http://localhost:5000&client_id=WpWSdRJeg08vQFEk92MlWIbDjDnm0VQB")



if __name__ == "__main__":
    app.run(debug=True)