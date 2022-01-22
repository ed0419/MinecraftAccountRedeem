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
            cursor.execute("SELECT PASSWORD from SYS_USERS where USER=%(uid)s",{'uid':uid})
            result = list(cursor)[0][0]
            print(result)
            if upass == result:
                session['login'] = 1
                session['login_uid'] = uid
                return redirect("admin")
            else:
                print("Error")
                return render_template("login.html",errorMsg="錯誤的使用者帳號密碼")
        except:
            return render_template("login.html",errorMsg="錯誤的使用者帳號密碼")
    else:
        return render_template("login.html",errorMsg=" ")

@app.route("/new",methods=["POST","GET"])
def newhost():
    if 'login' not in session:
        session['login'] = 0
    if 'login_uid' not in session:
        session['login_uid'] = "X"
    if request.method == "POST":
        if session['login'] == 1:
            uid = session['login_uid']
            hname = request.form["hname"]
            hip = request.form["hip"]
            hport = request.form["hport"]
            
            #check patarn
            IPREGEX = "^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            PORTREGEX = "^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
            if re.search(IPREGEX,hip):
                ok_hip = hip
            else:
                print("SQLi Dectected!",hip)
            if re.search(PORTREGEX,hport):
                ok_hport = hport
            else:
                print("SQLi Dectected!",hport)
            try:
                db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
                cursor = db.cursor()
                cursor.execute("INSERT INTO SYS_HOSTS (OWNEDBY, NAME, IP, PORT) VALUES (%(uid)s,%(hname)s,%(ok_hip)s,%(ok_hport)s)",{'uid':uid, 'hname':hname, 'ok_hip':ok_hip, 'ok_hport':ok_hport})
                db.commit()
                return '<script>alert("成功")</script><meta http-equiv="refresh" content="0; url=".">'
            except:
                return '<script>alert("Faild")</script><meta http-equiv="refresh" content="0; url=".">'
        else:
            return redirect("/admin")
        
    else:
        if session['login'] == 1:
            return render_template("new.html",uid=session['login_uid'])
        else:
            return redirect("/admin")

@app.route("/delete",methods=["POST","GET"])
def delete_host():
    Msg =""
    if 'login' not in session:
        session['login'] = 0
    if 'login_uid' not in session:
        session['login_uid'] = "X"
    try:
        if request.method == "GET":
            if session['login'] == 1:
                uid=session["login_uid"]
                html = ""
                #SQL CONN
                db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
                cursor = db.cursor()
                #cursor.execute(f"SELECT SERVER_ID, NAME, IP, PORT from SYS_HOSTS where OWNEDBY='{uid}'")
                cursor.execute("SELECT SERVER_ID, NAME, IP, PORT from SYS_HOSTS where OWNEDBY=%(uid)s", {'uid':uid})
                results = cursor.fetchall()
                print(results)
                for i in range(len(results)):
                    server_id = results[i][0]
                    name = results[i][1]
                    ip = results[i][2]
                    port = results[i][3]
                    print(server_id,name,ip,port)
                    html +=f' \
                        <tr> \
                            <td>{server_id}</td>\
                            <td><a href="/server/{ip}">{ip}</a></td>\
                            <td class="hostname">{name}</td>\
                            <td><form action="#" method="POST"><input type="hidden" name="hip" value={ip}><button type="submit" class="btn btn-sm btn-block btn-outline-primary">確認刪除</button></form></td>\
                        </tr> '
                
                return render_template("delete.html",uid=uid,html=html)
            else:
                return redirect("/admin")
        if request.method == "POST":
            if session['login'] == 1:
                print(request.path)
                delete_ip = request.form['hip']
                print(delete_ip)
                #SQL CONN
                db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
                cursor = db.cursor()
                #cursor.execute(f"DELETE FROM SYS_HOSTS WHERE IP='{delete_ip}'")
                cursor.execute("DELETE FROM SYS_HOSTS WHERE IP=%(delete_ip)s",{'delete_ip':delete_ip})
                db.commit()
                return '<script>alert("成功")</script><meta http-equiv="refresh" content="0; url=".">'
            else:
                return redirect("/admin")
    except:
        print("Error")
        return render_template("delete.html",uid=session['login_uid'],Msg="Error")
            


# 管理頁面
@app.route('/admin')
def admin():
    failed_html = ""
    if 'login' not in session:
        session['login'] = 0
    if 'login_uid' not in session:
        session['login_uid'] = "X"
    if 'message' not in session:
        session['message'] = ""
    try:
        if session['login'] == 1:
            uid=session["login_uid"]
            faild_count = 0
            html = ""
            #SQL CONN
            db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")
            cursor = db.cursor()
            # OLD
            #cursor.execute(f"SELECT SERVER_ID, NAME, IP, PORT from SYS_HOSTS where OWNEDBY='{uid}'")
            # NEW
            cursor.execute("SELECT SERVER_ID, NAME, IP, PORT from SYS_HOSTS where OWNEDBY=%(uid)s",{'uid':uid})
            results = cursor.fetchall()

            for i in range(len(results)):
                server_id = results[i][0]
                name = results[i][1]
                ip = results[i][2]
                port = results[i][3]
                print(server_id,name,ip,port)
                try:
                    r_player = requests.get(f"http://{ip}:{port}/players.json", timeout=1).json()
                    r_info = requests.get(f"http://{ip}:{port}/DYNAMIC.json", timeout=1).json()
                    hostname = r_info['hostname']
                    players = len(r_player)
                    print(hostname)
                    ping = []

                    for i in r_player:
                        ping.append(i['ping'])
                    if sum(ping) <= 0:
                        ping_avg = -1
                    else:
                        ping_avg = str(round(sum(ping)/len(r_player),2))

                    html +=f' \
                        <tr> \
                            <td>{server_id}</td>\
                            <td><a href="http://{ip}:{port}/ ">{ip}</a></td>\
                            <td>{name}</td>\
                            <td class="hostname">{hostname}</td>\
                            <td>{players}</td>\
                            <td>{ping_avg}</td>\
                        </tr> '
                except Exception as e:
                    faild_count += 1
                    offlineMsg= '<h3 class="h5 mb-3 font-weight-normal">離線主機</h3>'
                    if faild_count == 1:
                        failed_html +=f' \
                        <tr>\
                        <th>No.</th>\
                        <th>IP</th>\
                        <th>主機名稱</th>\
                        <th>RP名稱</th>\
                        </tr></thead>'
                        failed_html +=f' \
                        <tbody> \
                        <tr> \
                            <td>{server_id}</td>\
                            <td><a href="http://{ip}:{port}/ ">{ip}</a></td>\
                            <td>{name}</td>\
                            <td class="hostname">Offline</td>\
                        </tr>'
                    else:
                        failed_html +=f' \
                        <tr> \
                            <td>{server_id}</td>\
                            <td><a href="http://{ip}:{port}/ ">{ip}</a></td>\
                            <td>{name}</td>\
                            <td class="hostname">Offline</td>\
                        </tr>'
                    print("Cant Fetch",server_id,name,ip,port,e)
            return render_template("admin.html",html=html,uid=uid,host_count=len(results),faild_count=faild_count,faild_html=failed_html,offlineMsg=offlineMsg)
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
    app.run(host = "0.0.0.0", port=8080, debug=True)