from flask import Flask, request, session, url_for, render_template, flash

app = Flask(__name__)


@app.route('/pypitches/')
def status():
    return render_template("status.html")

@app.route('/pypitches/controls')
def controls():
    return render_template("controls.html")


if __name__ == "__main__":
    app.run()
