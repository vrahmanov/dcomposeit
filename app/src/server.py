import os
import flask
import json
from flask import request
import mysql.connector
import random
# for debugging from Visual Studio Code -- turn off flask debugger first
# import ptvsd
# ptvsd.enable_attach(address=('0.0.0.0', 3000))

class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user,
            password=pf.read(),
            host=host,
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()

    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS unboundtech')
        self.cursor.execute('CREATE TABLE unboundtech (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))')
        self.cursor.executemany('INSERT INTO unboundtech (id, title) VALUES (%s, %s);', [(i, 'Customer #%d'% i) for i in range (1,5)])
        self.connection.commit()

    def query_titles(self):
        self.cursor.execute('SELECT title FROM unboundtech')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    def insert_titles(self,number):
        self.cursor.executemany('INSERT INTO unboundtech (id, title) VALUES (%s, %s);', [(number, 'Customer #%d'% number)])
        self.connection.commit()
    # def post(self):
    #     """
    #     Add a quote to the db
    #     Expect a JSON payload with the following format
    #     {
    #         "quote": "The quote",
    #         "quote_by": "The person who said the quote",
    #         "added_by": The person who is posting the quote"
    #     }
    #     """
    #     data = request.get_json()
    #     query = "INSERT INTO `unboundtech` (`quote`, `quote_by`, `added_by`) VALUES (:quote, :quote_by, :added_by)"
    #     try:
    #         self.db.connection.execute(sql_text(query), data)
    #         return True
    #     except:
    #         return False


server = flask.Flask(__name__)
conn = None

@server.route('/customers' , methods=['GET','POST'])
def mainer():
    if request.method == 'GET':
        global conn
        if not conn:
            conn = DBManager(password_file='/run/secrets/db-password')
            conn.populate_db()
        rec = conn.query_titles()

        result = []
        for c in rec:
            result.append(c)

        return flask.jsonify({"response": result})
    elif request.method == 'POST':
        if not conn:
            conn = DBManager(password_file='/run/secrets/db-password')
            conn.populate_db()
        try:
            rec = conn.insert_titles(random.randrange(100000000))
            return flask.jsonify({"response": "New line inserted randomly"})
        except:
            return flask.jsonify({"ERROR": "duplicate entry"})

    else:
        return flask.jsonify({"response": "API error - check method"})



@server.route('/insert',methods = ['POST'])
def insertcustomer():
    print(request.is_json)
    content = request.get_json()
    print(content)
    # return 'JSON posted'
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_db()
    try:
        rec = conn.insert_titles(content)
        return flask.jsonify({"response": "New line inserted Explicitly %s" % content})
    except:
        return flask.jsonify({"ERROR": "Already Exist %s" % content})



@server.route('/')
def hello():
    return flask.jsonify({"status": "200"})


if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=5000)
