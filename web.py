from os import stat
from unittest import result
from flask import Flask, request,  render_template, redirect, session, url_for
import re, pymysql, json, requests
from datetime import timedelta
from flask_cors import CORS
app = Flask(__name__,static_folder='static/')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config.update(
TESTING=True,
SECRET_KEY=b'DDew5we83',
SESSION_COOKIE_NAME="HaveYouEverHeardDontUseF12",
#SESSION_COOKIE_DOMAIN=""
)

# 重導
@app.route('/')
def main():
    return redirect("login")

#設置session timeout
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
#登入介面 and session
@app.route('/login',methods=["POST","GET"])
def login():
    try:
        if 'login' not in session:
            session['login'] = 0
        if 'login_uid' not in session:
            session['login_uid'] = "X"
    except:
        print("F?")
    if session['login'] == 1:
        return redirect("/admin")
    if request.method == "POST":
        uid = request.form["uid"]
        upass = request.form["upass"]
        db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
        cursor = db.cursor()
        print(uid,upass)
        try:
            cursor.execute("SELECT password from MC_OLD where email=%(uid)s",{'uid':uid})
            password = cursor.fetchone()
            print(password[0])
            if upass == password[0]:
                session['login'] = 1
                session['login_uid'] = uid
                return redirect("admin")
            else:
                print("Error")
                return render_template("login.html",errorMsg="錯誤的使用者帳號密碼")
        except Exception as e:
            return render_template("login.html",errorMsg=f"錯誤的使用者帳號密碼1")
    else:
        return render_template("login.html",errorMsg=" ")

# 管理頁面
@app.route('/admin')
def admin():

    if 'login' not in session:
        session['login'] = 0
    if 'login_uid' not in session:
        session['login_uid'] = "X"
    if 'message' not in session:
        session['message'] = ""
    try:
        if session['login'] == 1:
            uid=session["login_uid"]
            #SQL CONN
            db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
            cursor = db.cursor()
            cursor.execute("SELECT status from MC_OLD where email=%(uid)s",{'uid':uid})
            status = list(cursor)[0][0]
            if status == "OK":
                cursor.execute("UPDATE MC_OLD SET STATUS = 'BROKEN' WHERE email=%(uid)s",{'uid':uid})
                db.commit()
                cursor.execute("SELECT email, password FROM MC_NEW WHERE status='OK'")
                result = cursor.fetchall()
                new_acc = result[0][0]
                cursor.execute("UPDATE MC_NEW SET owned = %(uid)s WHERE email=%(change)s",{'change':new_acc,"uid":uid})
                db.commit()
                cursor.execute("UPDATE MC_NEW SET status = 'USED' WHERE owned=%(uid)s",{"uid":uid})
                db.commit()
                cursor.execute("SELECT email, password FROM MC_NEW WHERE status='USED' and owned=%(uid)s",{'uid':uid})
                result = cursor.fetchall()
                new_acc = result[0][0]
                new_acc_pass = result[0][1]
                print(new_acc,new_acc_pass)
                html =f' \
                    <tr> \
                        <td>{new_acc}</td>\
                        <td>{new_acc_pass}</td>\
                    </tr> '
            elif status == "BROKEN":
                cursor.execute("SELECT email, password FROM MC_NEW WHERE status='USED' and owned=%(uid)s",{'uid':uid})
                result = cursor.fetchall()
                new_acc = result[0][0]
                new_acc_pass = result[0][1]
                print(new_acc,new_acc_pass)
                html =f' \
                    <tr> \
                        <td>{new_acc}</td>\
                        <td>{new_acc_pass}</td>\
                    </tr> '
            return render_template("admin.html",uid=uid,html=html)
        else:
            return redirect("login")
    except pymysql.Error as e:
        print("DB Failed"+str(e))
        return redirect("login")

# 登出
@app.route('/logout')
def logout():
    session['login'] = 0
    return redirect("login")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port=8081, debug=True ,ssl_context=('server.crt', 'server.key',))