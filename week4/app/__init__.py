from flask import Flask
from flask_mail import Mail

app = Flask(__name__)

# 메일 설정
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'b9358945@gmail.com'
app.config['MAIL_PASSWORD'] = '비밀'
app.config['MAIL_DEFAULT_SENDER'] = 'b9358945@gmail.com'

mail = Mail(app)

from app import routes

