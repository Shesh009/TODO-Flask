from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime,date,time
from send_email import send_email
import os
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

app = Flask(__name__)
app.secret_key = os.urandom(24)

def connect_to_mysql():
    mysql_config = {
        'host': os.getenv("HOST"),
        'user': os.getenv("USER"),
        'password': os.getenv("PASSWORD_SQL"),
        'database': os.getenv("DATABASE")
    }
    connection = mysql.connector.connect(**mysql_config)
    return connection

def execute_query(query, fetch=False, fetchall=False):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            result = None
            if fetchall:
                result = cursor.fetchall()
            elif fetch:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()  # Fetch all by default for SELECT queries
        else:  # For INSERT, UPDATE, DELETE
            connection.commit()  # Commit changes for non-SELECT queries
            result = None
    except Exception as e:
        connection.rollback()  # Rollback changes if an exception occurs
        print(f"Error executing query: {str(e)}")
        result = None
    finally:
        cursor.close()
        connection.close()
    return result


@app.route('/', methods=["GET", "POST"])
def home():
    query = "SELECT DATE_FORMAT(CREATED, '%d %b %Y'),TASK,DATE_FORMAT(DEADLINE,'%Y-%m-%d'),COMPLETED,EMAIL,EMAIL_SENT FROM TODO ORDER BY DEADLINE"
    data = execute_query(query, fetchall=True)
    # d=defaultdict(list)
    for i in data:
        if not is_valid_date(i[2]):
            query = f"DELETE FROM TODO WHERE DEADLINE = '{i[2]}'"
            execute_query(query)
    data=execute_query(query,fetchall=True)
    # time=datetime.now().strftime("%H:%M")
    # for i in data:
    #     l=""
    #     if (datetime.strptime(i[2], '%Y-%m-%d')-datetime.today()).days==4 and i[3]==0 and i[5]==0:
    #         query=f"UPDATE TODO SET EMAIL_SENT=1 where (TASK='{i[1]}' and ((DATEDIFF('{i[2]}',SYSDATE())-1)=4 or (DATEDIFF('{i[2]}',SYSDATE())-2)=4))";
    #         execute_query(query,fetchall=True)
    #         l+=i[1]+"->"+i[2]+"\n"
    #         d[i[4]].append(l)
    #         print(l)
    # print(d)
    # c=0
    # try:
    #     for i,j in d.items():
    #         j=",".join(j)
    #         if j!='':
    #             send_email("Tasks to be completed in 4 days",i,j)
    #             c+=1
    # except:
    #     print("Error in sending mail")
    # print(f"Emails sent : {c}")
    
    query = "SELECT DATE_FORMAT(CREATED, '%d %b %Y'),TASK,DATE_FORMAT(DEADLINE,'%d %b %Y'),COMPLETED FROM TODO ORDER BY DEADLINE"
    data = execute_query(query, fetchall=True)
    return render_template("index.html" ,data=data)

@app.route('/add', methods=["POST"])
def add():
    task = request.form.get('task')
    deadline = request.form.get('deadline')
    mail=request.form.get('mail')
    current_date_time = datetime.now()
    current_date = current_date_time.date()
    if is_valid_date(deadline):
        query = f"INSERT INTO TODO (CREATED, TASK, DEADLINE,EMAIL) VALUES ('{current_date}', '{task}', '{deadline}','{mail}')"
        execute_query(query)
    return redirect(url_for('home'))

@app.route('/update/<task>', methods=["POST"])
def update(task):
    # Use the received value in your SQL query to update the database
    query = f"UPDATE TODO SET COMPLETED = CASE WHEN COMPLETED = 0 THEN 1 ELSE 0 END WHERE TASK = '{task}'"
    execute_query(query)
    return redirect(url_for('home'))

@app.route('/delete/<task>', methods=["GET","POST"])
def delete(task):
    query=f"DELETE FROM TODO WHERE TASK='{task}'"
    execute_query(query)
    return redirect(url_for('home'))


def is_valid_date(date_str, format='%Y-%m-%d'):
    try:
        current_date = datetime.now().date()
        if date_str >= str(current_date):
            datetime.strptime(date_str, format)
            return True 
    except ValueError:
        return False
    
def send_mail():
    query = "SELECT DATE_FORMAT(CREATED, '%d %b %Y'),TASK,DATE_FORMAT(DEADLINE,'%Y-%m-%d'),COMPLETED,EMAIL,EMAIL_SENT FROM TODO ORDER BY DEADLINE"
    d=defaultdict(list)
    data=execute_query(query,fetchall=True)
    time=datetime.now().strftime("%H:%M")
    for i in data:
        l=""
        if (datetime.strptime(i[2], '%Y-%m-%d')-datetime.today()).days==4 and i[3]==0 and i[5]==0:
            query=f"UPDATE TODO SET EMAIL_SENT=1 where (TASK='{i[1]}' and ((DATEDIFF('{i[2]}',SYSDATE())-1)=4 or (DATEDIFF('{i[2]}',SYSDATE())-2)=4))";
            # query = f"UPDATE TODO SET EMAIL_SENT=1 WHERE TASK='{i[1]}' AND DATE({i[2]}) = DATE(NOW() + INTERVAL 4 DAY)"
            execute_query(query,fetchall=True)
            l+=i[1]+"->"+i[2]+"\n"
            d[i[4]].append(l)
            print(l)
    print(d)
    c=0
    try:
        for i,j in d.items():
            j=",".join(j)
            if j!='':
                send_email("Tasks to be completed in 4 days",i,j)
                c+=1
                print("Mail sent")
    except Exception as e:
        print(f"Error in sending mail\n{e}")
    print(f"Emails sent : {c}")

scheduler.add_job(send_mail, 'interval', seconds=5)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)