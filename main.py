import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, make_response, request, abort, jsonify

from data import news_api, jobs_api, users_api, news_resources, users_resources, jobs_resources
from data.__all_models import Jobs, User, News, Department
from data.db_session import global_init, create_session
from forms.department import DepartmentForm
from forms.jobs import JobsForm
from forms.login import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from work_api import get_address_coords, MAP_API_SERVER
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    db_sess = create_session()
    posts = db_sess.query(News).all()
    return render_template('index.html', posts=posts, current_user=current_user)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            address=form.address.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = create_session()
        job = Jobs()
        job.team_leader = form.team_leader.data
        job.job = form.job.data
        job.is_finished = form.is_finished.data
        job.collaborators = form.collaborators.data
        job.work_size = form.work_size.data
        current_user.jobs.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/job_list')
    return render_template('jobs.html', title='Добавление работы',
                           form=form)


@app.route('/departments_add', methods=['GET', 'POST'])
@login_required
def add_departments():
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = create_session()
        department = Department()
        department.chief = form.chief.data
        department.title = form.title.data
        department.members = form.members.data
        department.email = form.email.data
        current_user.department.append(department)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/departments')

    return render_template('department_action.html', title='Добавление отделения',
                           form=form)


@app.route('/job_list')
@login_required
def jobs():
    db_sess = create_session()
    job_list = db_sess.query(Jobs).all()
    return render_template('job_list.html', jobs=job_list, current_user=current_user)


@app.route('/departments')
@login_required
def departments():
    db_sess = create_session()
    department_list = db_sess.query(Department).all()
    return render_template('departments.html', departments=department_list, current_user=current_user)


@app.route('/jobs/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(job_id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == job_id,
                                         Jobs.user == current_user
                                         ).first()
        if job:
            form.team_leader.data = job.team_leader
            form.job.data = job.job
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == job_id,
                                         Jobs.user == current_user
                                         ).first()
        if job:
            job.team_leader = form.team_leader.data
            job.job = form.job.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/job_list')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/departments_edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_departments(department_id):
    form = DepartmentForm()
    db_sess = create_session()
    department = db_sess.query(Department).filter(Department.id == department_id,
                                                  Department.user == current_user
                                                  ).first()
    if request.method == "GET":
        if department:
            form.title.data = department.title
            form.chief.data = department.chief
            form.email.data = department.email
            form.members.data = department.members
        else:
            abort(404)
    if form.validate_on_submit():
        if department:
            department.title = form.title.data
            department.chief = form.chief.data
            department.email = form.email.data
            department.members = form.members.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('department_action.html',
                           title='Редактирование отделения',
                           form=form
                           )


@app.route('/news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = create_session()
        news = db_sess.query(News).filter(News.id == news_id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:

            abort(404)
    if form.validate_on_submit():
        db_sess = create_session()
        news = db_sess.query(News).filter(News.id == news_id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


# START DELETING
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/departments_delete/<int:department_id>')
@login_required
def departments_delete(department_id):
    db_sess = create_session()
    department = db_sess.query(Department).filter(Department.id == department_id,
                                                  Department.user == current_user
                                                  ).first()
    if department:
        db_sess.delete(department)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id,
                                     Jobs.user == current_user
                                     ).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/job_list')


# END DELETING

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/users_show/<int:user_id>', methods=['GET'])
def get_city_photo(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    coords = get_address_coords(user.city_from)
    path = f'{MAP_API_SERVER}?ll={",".join(coords)}&l=sat&z=11'
    return render_template('nostalgy.html', user=user, img_path=path)


def main():
    global_init('db/blogs.db')
    app.register_blueprint(news_api.blueprint)
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    api.add_resource(news_resources.NewsListResource, '/api/v2/news')
    api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
    api.add_resource(users_resources.UsersListResource, '/api/v2/users')
    api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:job_id>')
    app.run()


if __name__ == '__main__':
    main()
