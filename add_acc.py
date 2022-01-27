import pymysql
import csv
db = pymysql.connect(host="gg60.mc2021.net",user="hmt",passwd="12345678",database="hmt_data")

with open('backup9.acc', newline='', encoding = 'utf-8') as csvfile:

    # 以冒號分隔欄位，讀取檔案內容 , delimiter='  '
    rows_stu = list(csv.reader(csvfile))

    for rows in rows_stu:
        cursor = db.cursor()
        cursor.execute("INSERT INTO MC_NEW (email, password) VALUES (%(uid)s,%(pass)s)",{'uid':rows[0], 'pass':rows[1]})
        db.commit()
        print(rows)