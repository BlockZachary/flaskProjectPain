import os
import random

import pymysql
from flask import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
showimg_path = './static/read_from_mysql.png'


# TODO 这里修改一下数据库配置
def conn_mysql():
    conn = pymysql.connect(host="localhost", port=3306, user='root', passwd="980226", charset='utf8', db='new_pain')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    return conn, cursor


@app.route('/')
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/loginer', methods=['GET'])
def loginer():
    username = request.args.get("username")
    password = request.args.get("password")

    if not username or not password:
        flash('请输入完整的用户名和密码!')
        return redirect(url_for('login'))
    conn, cursor = conn_mysql()
    my_query = "SELECT * FROM user WHERE usr = %s"
    cursor.execute(my_query, [username])
    res = cursor.fetchall()

    if res:
        my_query = "SELECT * FROM user WHERE usr = %s and password = %s"
        cursor.execute(my_query, [username, password])
        res = cursor.fetchall()
        cursor.close()
        conn.close()
        if res:
            # 加上session
            session['login_success'] = 'permission'
            return redirect(url_for('patientSearchPage'))
        else:
            flash('密码错误，请重试!')
            return redirect(url_for('login'))
    else:
        cursor.close()
        conn.close()
        flash('用户名不存在请先注册!')
        return redirect(url_for('login'))


@app.route('/register', methods=['GET'])
def register():
    username = request.args.get("username")
    password = request.args.get("password")
    if not username or not password:
        flash('请输入完整的用户名和想要设置的密码')
        return redirect(url_for('login'))

    conn, cursor = conn_mysql()
    my_query = f"SELECT * FROM user where usr = %s"
    cursor.execute(my_query, [username])
    res = cursor.fetchall()

    if res:
        flash('用户已经存在! 请登录，或者重新输入用户名！')
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    else:
        my_query = "INSERT INTO user(usr,password) VALUES(%s,%s)"
        cursor.execute(my_query, (username, password))
        conn.commit()
        flash('新用户已注册成功！')
        cursor.close()
        conn.close()
        return redirect(url_for('login'))


@app.route('/patientSearchPage', methods=['GET'])
def patientSearchPage():
    permission = session.get('login_success')
    if not permission:
        return redirect(url_for('login'))
    try:
        os.remove(showimg_path)
    except:
        print("No Imgpath")
    return render_template("2.html", res=None)


@app.route('/sameCasePage', methods=['GET'])
def sameCasePage():
    permission = session.get('login_success')
    if not permission:
        return redirect(url_for('login'))
    try:
        os.remove(showimg_path)
    except:
        print("No Imgpath")
    return render_template("3.html", res=None, case=None)


@app.route('/patientSearchDetial', methods=['GET'])
def patientSearchDetial():
    curname = request.args.get("curname")
    if not curname:
        flash('请输入患者姓名进行查询！')
        return redirect(url_for('patientSearchPage'))
    conn, cursor = conn_mysql()

    my_query = f"SELECT * FROM new_patient where name = %s"
    cursor.execute(my_query, [curname])
    res = cursor.fetchall()
    cursor.close()
    conn.close()

    if res:
        fout = open(showimg_path, 'wb')
        fout.write(res[0]['img'])
        fout.close()
        return render_template('2.html', res=res[0])
    else:
        try:
            os.remove(showimg_path)
        finally:
            flash('没有该患者记录！')
            return redirect(url_for('patientSearchPage'))


@app.route('/sameCasePageDetial/confirm', methods=['GET'])
def confirm():
    curname = request.args.get("curname")
    if not curname:
        flash('请输入患者姓名进行查询！')
        return redirect(url_for('sameCasePage'))
    conn, cursor = conn_mysql()

    my_query = f"SELECT * FROM new_patient where name = %s"
    cursor.execute(my_query, [curname])
    res = cursor.fetchall()


    if res:
        curpainlevel = res[0]['painlevel']
        case_query = f"SELECT * FROM new_patient where painlevel = %s and name != %s"
        cursor.execute(case_query, [curpainlevel, curname])

        result = cursor.fetchall()
        length_result = len(result)
        ran_num = random.sample(range(length_result), 3)

        # case = cursor.fetchmany(3)
        case = [result[ran_num[0]], result[ran_num[1]], result[ran_num[2]]]
        cursor.close()
        conn.close()

        fout = open(showimg_path, 'wb')
        fout.write(res[0]['img'])
        fout.close()
        return render_template('3.html', res=res[0], case=case)
    else:
        cursor.close()
        conn.close()
        try:
            os.remove(showimg_path)
        finally:
            flash('没有该患者记录！')
            return redirect(url_for('sameCasePage'))


@app.route('/sameCasePageDetial/cancel', methods=['GET'])
def cancel():
    try:
        os.remove(showimg_path)
    finally:
        return render_template('3.html', res=None, case=None)


if __name__ == '__main__':
    app.run()
