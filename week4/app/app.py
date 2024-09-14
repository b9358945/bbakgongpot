from app import app
from flask_mail import Mail, Message

app.secret_key = 'bbakgongpot'


if __name__ == '__main__':
    app.run(debug=True)

