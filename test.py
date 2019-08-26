from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def homepage():
    return "<h1>RIIYASAT <3 NAZIA</h1>"

