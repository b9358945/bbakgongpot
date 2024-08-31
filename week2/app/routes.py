from app import app
from flask import render_template, request

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/main", methods=['POST', 'GET'])
def main():
    id = request.form['id']
    pw = request.form['pw']
    return render_template('main.html',
                           id=id,
                           pw=pw)

