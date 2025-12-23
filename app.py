from flask import Flask, render_template, request
from logic.doctor import analyze

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        size = request.form["size"]
        battery = request.form["battery"]
        style = request.form["style"]

        result = analyze(size, battery, style)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()