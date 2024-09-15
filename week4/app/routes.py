from app import app, mail
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, session
from datetime import datetime
import pymysql, os, json
import math, random
from flask_mail import Message

#------------------------ 업로드 폴더 경로 설정 ------------------------#
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
#-------------------------------------------------------#

#------------------------ 파일 폴더 경로 설정 ------------------------#
FILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file')
app.config['FILE_FOLDER'] = FILE_FOLDER

if not os.path.exists(app.config['FILE_FOLDER']):
    os.makedirs(app.config['FILE_FOLDER'])
#-------------------------------------------------------#

#------------------------ 프로필 이미지 폴더 경로 설정 ------------------------#
PROFILE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile_image')
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER

if not os.path.exists(app.config['PROFILE_FOLDER']):
    os.makedirs(app.config['PROFILE_FOLDER'])
#-------------------------------------------------------#

#------------------------ DB ------------------------#
# DB 연결
def connect_db():
    conn = pymysql.connect(host='127.0.0.1', 
                        user='root', 
                        password='1234', 
                        db='bbakgongpot', 
                        charset='utf8',
                        cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    return conn, cur

# DB 종료
def close_db(conn):
    conn.close()
#-------------------------------------------------------#

#------------------------ 회원 가입 ------------------------#
# 회원 가입 페이지
@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

# 회원 가입
@app.route('/register', methods=['POST'])
def register():

    member_type = int(request.form['member_type'])
    id = request.form['id']
    realname = request.form['realname']
    nickname = request.form['nickname']
    pw = request.form['pw']
    email = request.form['email']
    phone = request.form['phone']
    introduce = request.form['introduce']
    profile_image_src = request.form['profile_image_src']

    query = """
    INSERT INTO member (member_type, id, realname, nickname, pw, email, phone, introduce, profile_image_src)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn, cur = connect_db()
    cur.execute(query, (member_type, id, realname, nickname, pw, email, phone, introduce, profile_image_src))
    conn.commit()
    close_db(conn)
    
    return redirect(url_for('index'))

# 아이디 중복 확인
@app.route('/id_duplicate_check', methods=['POST'])
def id_duplicate_check():
    id = request.form['id']

    conn, cur = connect_db()

    query = """
    SELECT * FROM member WHERE id=%s
    """
    conn, cur = connect_db()
    cur.execute(query, (id))
    id_exist = cur.fetchone()
    close_db(conn)

    if id_exist is None:
        return jsonify({"id_exist" : False})
    else:
        return jsonify({"id_exist" : True})
    
# 프로필 이미지 image 폴더에 업로드
@app.route('/profile_image_upload', methods=['POST'])
def profile_image_upload():
    files = request.files.getlist('file')
    file = files[0]

    filename=file.filename
    filedir= os.path.join(app.config['PROFILE_FOLDER'], filename)

    # /upload 폴더에 이미지들 저장
    file.save(filedir)

    return jsonify({'url': f'/profile_image/{filename}'})

# html에서 방금 업로드한 프로필 이미지에 접근
@app.route('/profile_image/<filename>')
def uploaded_profile(filename):
    return send_from_directory(app.config['PROFILE_FOLDER'], filename)
#-------------------------------------------------------#

#------------------------ 로그인, 로그아웃 ------------------------#
# 로그인 페이지
@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

# 로그인 
@app.route('/login', methods=['POST'])
def login():

    id = request.form['id']
    pw = request.form['pw']

    query = """
    SELECT * FROM member WHERE id=%s and pw=%s
    """
    conn, cur = connect_db()
    cur.execute(query, (id, pw))
    user = cur.fetchone()
    close_db(conn)

    if user is None:
        return jsonify({"login_success":False, "message": "로그인 실패. 다시 시도해주세요"})
    
    session['id'] = user['id']
    session['nickname'] = user['nickname']

    return jsonify({"login_success":True})

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#-------------------------------------------------------#

#------------------------ 아이디 찾기, 비밀번호 찾기 ------------------------#
@app.route("/findidpage")
def findidpage():
    return render_template("findid.html")

@app.route("/findpwpage")
def findpwpage():
    return render_template("findpw.html")

# 아이디 이메일로 전송
@app.route("/send_email", methods=['POST'])
def send_email():
    realname = request.form['realname']
    email =  request.form['email']

    # DB에서 id 조회
    conn, cur = connect_db()
    query = """
            SELECT id from member WHERE email=%s
            """
    cur.execute(query, (email))
    id = cur.fetchone()['id']
    close_db(conn)

    try:
        msg = Message(f'보안뉴스의 아이디 찾기 메일입니다.', 
                    sender='b9358945@gmail.com', 
                    recipients=[email])
        msg.body = f'보안뉴스의 아이디는 [{id}] 입니다.'
        mail.send(msg)
        send_email = True
        message = "이메일로 아이디를 보냈습니다."
    except:
        send_email = False
        message = "이메일 보내기 실패했습니다. 다시 시도해 주세요"

    return jsonify({"message":message})

# 인증 코드 생성해서 이메일 전송
@app.route("/send_verifycode", methods=['GET'])
def send_verifycode() :
    id = request.args.get('id')
    realname = request.args.get('realname')
    email =  request.args.get('email')

    # DB 조회
    conn, cur = connect_db()
    query = """
            SELECT * FROM member WHERE id=%s AND realname=%s AND email=%s
            """
    cur.execute(query, (id, realname, email))
    row =  cur.fetchone()

    if row :
        verifycode = str(random.randint(000000, 999999)).zfill(6)
        # verifycode 이메일로 전송
        try:
            msg = Message(f'보안뉴스의 아이디 찾기 인증코드 메일입니다.', 
                        sender='b9358945@gmail.com', 
                        recipients=[email])
            msg.body = f'보안뉴스의 아이디 찾기 인증코드는 [{verifycode}] 입니다.'
            mail.send(msg)
            send_verifycode = True
            message = "인증 코드를 메일로 보냈습니다.유효 시간은 3분 입니다."
        except:
            send_verifycode = False
            message = "인증 코드 메일로 보내기 실패"

        date = datetime.now()
        # 잘 보냈으면 member DB에 인증코드, 현재 시간이랑 해서 넣기, 나중에 비교할 때는 시간이 3분이 지났는지 비교해서 가져오기

        query = """ UPDATE member set verifycode=%s, date=%s WHERE email=%s
                """
        cur.execute(query, (verifycode, date, email))
        conn.commit()
    else : 
        send_verifycode = False
        message = "회원 정보 확인에 실패하였습니다."

    close_db(conn)

    return jsonify({"send_verifycode":send_verifycode,"message": message})

# 인증 코드 맞는지 비교
@app.route("/check_verifycode", methods=['POST'])
def check_veryficode() :
    id = request.form['id']
    email = request.form['email']
    realname = request.form['realname']
    verifycode_client = request.form['verifycode']

    conn, cur = connect_db()
    query = """
        SELECT verifycode, date, pw FROM member WHERE id=%s AND email=%s AND realname=%s
        """
    cur.execute(query, (id, email, realname))
    row =  cur.fetchone()
    close_db(conn)

    date = row['date']
    verifycode_server = row['verifycode']
    pw = row['pw']

    # 인증 코드 3분 유효시간 체크
    if 0 < (datetime.now()-date).total_seconds() <= 180 :
        if verifycode_client == verifycode_server :
            message = '인증 성공'
            return jsonify({"message":message, "pw":pw})
        else :
            message = "인증 코드가 일치하지 않습니다."
    else :
        message = "인증 코드가 만료되었습니다. 인증 코드를 다시 발급해주세요"
    
    return jsonify({"message":message})
#-------------------------------------------------------#

#------------------------ 프로필 ------------------------#
@app.route("/profile/<string:id>")
def profile(id):

    conn, cur = connect_db()
    query = """
        SELECT * FROM member WHERE id = %s
        """
    cur.execute(query, (id,))
    row = cur.fetchone()
    close_db(conn)

    try :
        if session['id'] == id :
            return render_template("myprofile.html",
                            row=row)
        else :
            return render_template("profile.html", 
                    row=row)
    except:
        return render_template("profile.html", 
                row=row)
    
@app.route("/profile_edit", methods=['POST'])
def profile_edit() :
    id = request.form['id']
    realname = request.form['realname']
    nickname = request.form['nickname']
    pw = request.form['pw']
    email = request.form['email']
    phone = request.form['phone']
    introduce = request.form['introduce']
    profile_image_src = request.form['profile_image_src']

    conn, cur = connect_db()
    query= """
            UPDATE member SET nickname=%s, pw=%s, email=%s, phone=%s, introduce=%s, profile_image_src=%s
            WHERE id=%s
            """
    cur.execute(query, (nickname, pw, email, phone, introduce, profile_image_src, id ))
    conn.commit()

    # 다시 내 정보 화면에 뿌려주기
    query = """
        SELECT * FROM member WHERE id = %s
        """
    cur.execute(query, (id))
    row = cur.fetchone()
    close_db(conn)

    return render_template("myprofile.html",
                           row=row)

#-------------------------------------------------------#

#------------------------ index 페이지 ------------------------#
# index.html 전체 기사 조회
@app.route('/')
def index():
    # 페이지네이션
    page = request.args.get('page', 1, type=int)
    per_page = 10

    conn, cur = connect_db()
    query = "SELECT COUNT(*) as count FROM article"
    cur.execute(query)

    total_count = cur.fetchone()['count']    
    total_pages = math.ceil(total_count / per_page)
    offset = (page - 1) * per_page
    page_range = range(1, total_pages + 1)

    # DB에서 데이터 가져와서 게시판에 보여주기
    query = f"""
    SELECT article.title, article.bigcontent, article.detailcontent, article.author, article.date, article.idx, article.viewcount, article.secret_article, article.secret_article_pw, images.imgurl
    FROM article article
    LEFT JOIN images images ON article.idx = images.article_idx AND images.firstimage=1
    LIMIT {per_page} OFFSET {offset}
    """
    cur.execute(query)
    rows = cur.fetchall()

    close_db(conn)

    return render_template('index.html',
                           rows=rows,
                           page=page,
                           total_pages=total_pages,
                           page_range=page_range
                           )


# article.html 기사 1개 조회 페이지
@app.route('/article', methods=['GET'])
def article():
    article_idx = request.args.get('idx')
    
    conn, cur = connect_db()
    # 게시글 가져오기
    sql=f"SELECT * FROM article WHERE idx={article_idx}"
    cur.execute(sql)
    id = session.get('id', None)
    row = cur.fetchone()

    if row['secret_article'] == 1 :
        if not session.get(f'article_{article_idx}_pass', False):
            return render_template("secret_article.html", article_idx=article_idx)

    # 조회수 카운트 늘리기
    query = """ UPDATE article SET viewcount = viewcount + 1 WHERE idx = %s
            """
    cur.execute(query, (article_idx,))
    conn.commit()

    # 파일 가져오기
    query = "SELECT * FROM file WHERE article_idx = %s"
    cur.execute(query, (article_idx,))
    files = cur.fetchone()
    if files :
        files['filename'] = files['file_url'].split('\\')[-1]
    else :
        files = None

    close_db(conn)
    return render_template('article.html',
                           row=row,
                           id=id,
                           files=files)

@app.route('/check_article_pw', methods=['POST'])
def check_article_pw() :
    secret_article_pw = request.form['secret_article_pw']
    article_idx = request.form['article_idx']

    conn, cur = connect_db()
    query = "SELECT * FROM article WHERE idx=%s"
    cur.execute(query, (article_idx, ))
    row = cur.fetchone()

    # 세션에 비밀번호 통과 상태 저장
    if row['secret_article_pw'] == secret_article_pw :
        session[f'article_{article_idx}_pass'] = True
        return redirect(url_for('article', idx=article_idx))
    else: 
        return redirect(url_for('article', idx=article_idx))


# search.html 검색 버튼
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    select_option = request.args.get('select_option')

    if (select_option == "all"): 
        query = "SELECT * FROM article WHERE title LIKE %s OR bigcontent LIKE %s OR detailcontent LIKE %s"
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    elif (select_option == "title"): 
        query = "SELECT * FROM article WHERE title LIKE %s"
        params = [f"%{keyword}%"]
    elif (select_option == "content"):
        query = "SELECT * FROM article WHERE bigcontent LIKE %s OR detailcontent LIKE %s"
        params = [f"%{keyword}%", f"%{keyword}%"]

    conn, cur = connect_db()
    cur.execute(query, params)
    rows = cur.fetchall()
    close_db(conn)

    return render_template('index.html',
                           rows=rows)
#-------------------------------------------------------#


#------------------------ 게시글 수정 ------------------------#
@app.route('/editpage/<int:article_idx>')
def editpage(article_idx):
    con, cur = connect_db()
    query = f"SELECT * FROM article WHERE idx={article_idx}"
    cur.execute(query)
    row = cur.fetchone()

    return render_template("editpage.html",
                           row=row)

@app.route('/edit', methods=['POST'])
def edit():
    title = str(request.form['title'])
    bigcontent=str(request.form['bigcontent'])
    detailcontent=str(request.form['detailcontent'])
    date=datetime.now().date()
    idx=request.form['idx']

    query="""UPDATE article SET title=%s, bigcontent=%s, detailcontent=%s, date=%s
            WHERE idx=%s
            """
    conn, cur = connect_db()
    cur.execute(query, (title, bigcontent, detailcontent, date, idx))
    conn.commit()
    close_db(conn)

    return redirect(url_for('article', idx=idx))
#-------------------------------------------------------#


#------------------------ 게시글 삭제 ------------------------#
@app.route('/delete_article/<int:article_idx>')
def delete_article(article_idx):

    query=f"DELETE FROM article WHERE idx={article_idx}"

    conn, cur = connect_db()
    cur.execute(query)
    conn.commit()
    close_db(conn)


    return redirect(url_for('index'))
#-------------------------------------------------------#


#------------------------ 게시글 쓰기 ------------------------#
@app.route('/writePage', methods=['GET', 'POST'])
def writePage():
    return render_template('write.html')

# 에디터에 실시간 이미지 삽입
@app.route('/insertImage', methods=['POST'])
def insertImage():

    files = request.files.getlist('file')
    file = files[0]

    filename=file.filename
    filedir= os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # /upload 폴더에 이미지들 저장
    file.save(filedir)

    return jsonify({'url': f'/upload/{filename}'})

# 에디터에서 방금 삽입한 이미지에 바로 접근해서 띄울 수 있게
@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# db에 기사 넣기
@app.route('/write', methods=['GET', 'POST'])
def write():
    title = str(request.form['title'])
    bigcontent=str(request.form['bigcontent'])
    detailcontent=str(request.form['detailcontent'])
    author=str(request.form['author'])
    date=datetime.now().date()
    file = request.files.getlist('files')[0]

    secret_article = 0
    secret_article_pw = None
    # 비밀글인지 체크
    if 'secret_article' in request.form :
        if request.form['secret_article'] == 'on' :
            secret_article_pw = request.form['secret_article_pw']
            secret_article = 1

    query = """
    INSERT INTO article (title, bigcontent, detailcontent, author, date, secret_article, secret_article_pw)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    conn, cur = connect_db()
    cur.execute(query, (title, bigcontent, detailcontent, author, date, secret_article, secret_article_pw))
    conn.commit()

    # summornote에 첨부된 이미지 저장
    article_idx = cur.lastrowid
    imgurls = json.loads(request.form['imgurls'])

    firstImage = 1
    for imgurl in imgurls:
        insertdb_image(article_idx, imgurl, firstImage)
        firstImage = 0

    # 첨부된 파일들 file 폴더에 저장하기
    if 'file' :
        if file.filename != '' :
            filename= file.filename
            file_url = os.path.join(app.config['FILE_FOLDER'], filename)
            file.save(file_url)

            # file DB에 저장
            query = """
                    INSERT INTO file (article_idx, file_url) VALUES (%s, %s)
                    """
            cur.execute(query, (article_idx, file_url))
            conn.commit()
    close_db(conn)

    return redirect(url_for('index'))

# summernote에 삽입된 이미지들 db에 저장
def insertdb_image(article_idx, imgurl, firstImage):
    conn, cur = connect_db()
    query = """
            INSERT INTO images (article_idx, imgurl, firstimage) VALUES (%s, %s, %s) 
            """
    cur.execute(query, (article_idx, imgurl, firstImage))
    conn.commit()
    close_db(conn)

    return True

#-------------------------------------------------------#