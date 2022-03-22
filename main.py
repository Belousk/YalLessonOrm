import datetime as dt

from flask import Flask, render_template
from data.__all_models import Jobs, User
from data.db_session import global_init, create_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    db_sess = create_session()
    return render_template('index.html', jobs=db_sess.query(Jobs).all())


def main():
    global_init('db/blogs.db')
    app.run()


if __name__ == '__main__':
    main()
