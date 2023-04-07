from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_file, g, jsonify
import os
import pandas as pd
import numpy as np
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(basedir, 'sqlite-ajay-db.db')
 
conn = sqlite3.connect(dbpath)
cursor = conn.execute("Select * from sqlite_schema limit 100;")
for i in cursor:
    print(i)
conn.close()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html' , verdict='Success')


@app.route('/secondpage', methods=['GET'])
def secondpage():
    return render_template('second_page.html' , verdict='Success')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)