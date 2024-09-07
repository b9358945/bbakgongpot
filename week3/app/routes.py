from app import app
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, session
from datetime import datetime
import pymysql, os, json
import math

#------------------------ 업로드 폴더 경로 설정 ------------------------#
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
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

#------------------------ index 페이지 ------------------------#
# index.html 전체 기사 조회
@app.route('/')
def index():
    # DB에서 데이터 가져와서 게시판에 보여주기

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
    SELECT article.title, article.bigcontent, article.detailcontent, article.author, article.date, article.filedir, article.idx, images.imgurl
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
    idx = request.args.get('idx')

    conn, cur = connect_db()
    sql=f"SELECT * FROM article WHERE idx={idx}"
    cur.execute(sql)
    close_db(conn)

    id = session.get('id', None)

    row = cur.fetchone()
    return render_template('article.html',
                           row=row,
                           id=id)

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
    filedir=""

    query = """
    INSERT INTO article (title, bigcontent, detailcontent, author, date, filedir)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    conn, cur = connect_db()
    cur.execute(query, (title, bigcontent, detailcontent, author, date, filedir))
    conn.commit()
    close_db(conn)

    # 업로드한 파일 upload 폴더랑 files DB테이블에 저장하기
    # for문써서 이미지 여러개면 여러번 저장하기
    article_idx = cur.lastrowid
    imgurls = json.loads(request.form['imgurls'])

    firstImage = 1
    for imgurl in imgurls:
        insertdb_image(article_idx, imgurl, firstImage)
        firstImage = 0

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

#------------------------ 회원 가입 ------------------------#
# 회원 가입 페이지
@app.route('/registerpage')
def registerpage():
    return render_template('registerpage.html')

# 회원 가입
@app.route('/register', methods=['POST'])
def register():

    id = request.form['id']
    pw = request.form['pw']
    nickname = request.form['nickname']
    email = request.form['email']
    member_type = request.form['member_type']


    query = """
    INSERT INTO member (id, pw, nickname, email, member_type)
    VALUES (%s, %s, %s, %s, %s)
    """

    conn, cur = connect_db()
    cur.execute(query, (id, pw, nickname, email, member_type))
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
#-------------------------------------------------------#

#------------------------ 로그인, 로그아웃 ------------------------#
# 로그인 페이지
@app.route('/loginpage')
def loginpage():
    return render_template('loginpage.html')

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