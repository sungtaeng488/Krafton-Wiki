from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/mypage")
def mypage():
    return render_template("mypage.html")


@app.route("/keyword/<keyword>")
def detail(keyword):
    return render_template("detail.html", keyword=keyword)


@app.route("/quiz/<keyword>")
def quiz(keyword):
    return render_template("quiz.html", keyword=keyword)


if __name__ == "__main__":
    app.run(debug=True)