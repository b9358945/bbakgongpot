from app import app
from flask import render_template, request, url_for
from datetime import datetime
import pymysql, os

# DB 연결 해놓기
conn = pymysql.connect(host='127.0.0.1', 
                       user='root', 
                       password='1234', 
                       db='bbakgongpot', 
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# 업로드 폴더 경로 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# index.html 전체 기사 조회
@app.route('/')
def index():
    # DB에서 데이터 가져와서 게시판에 뿌리기
    query = """
    SELECT title, bigcontent, detailcontent, author, date, filedir, idx FROM article
    """
    cur.execute(query)
    rows = cur.fetchall()
    return render_template('index.html',
                           rows=rows)

# article.html 기사 1개 조회 페이지
@app.route('/article', methods=['GET'])
def article():
    idx = request.args.get('idx')

    sql=f"SELECT * FROM article WHERE idx={idx}"
    cur.execute(sql)
    row = cur.fetchone()
    return render_template('article.html',
                           row=row)

# write.html 기사 쓰는 페이지
@app.route('/writePage', methods=['GET', 'POST'])
def writePage():
    return render_template('write.html')

# 파일을 upload 폴더에 저장
def uploadfile(article_idx, files):
    # upload 폴더에 이미지 저장
    try:
        for file in files:
            filedir = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filedir)
    except Exception as e:
        return e
    
    # files db에 파일 정보 저장
    try:
        for file in files:
            filename=file.filename
            filedir= os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            firstImage = 0

            query = """INSERT INTO files (filename, article_idx, filedir, firstImage)
                    VALUES (%s, %s, %s, %s)
                    """
            cur.execute(query, (filename, article_idx, filedir, firstImage))
            conn.commit()

    except Exception as e:
        return e
    return 1

# db에 기사 넣기
@app.route('/write', methods=['POST'])
def write():
    title = str(request.form['title'])
    bigcontent=str(request.form['bigcontent'])
    detailcontent=str(request.form['detailcontent'])
    author=str(request.form['author'])
    date=datetime.now().date()
    filedir=""

    # DB에 데이터 넣을 차례
    query = """
    INSERT INTO article (title, bigcontent, detailcontent, author, date, filedir)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(query, (title, bigcontent, detailcontent, author, date, filedir))
    conn.commit()

    ###############################################################################

    # 업로드한 파일 upload 폴더랑 files DB테이블에 저장하기
    article_idx = cur.lastrowid
    files=request.files.getlist('files')
    uploadfile(article_idx, files)

    #conn.close()
    return render_template('index.html')

# search.html 검색 버튼
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    
    # 여기부터는 db 연결해서 새 조회 후 결과 뿌려주는 페이지
    rows = '1'

    return render_template('search.html',
                           rows=rows)