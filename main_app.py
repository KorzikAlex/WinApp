from flask import Flask, url_for, render_template, redirect, request
from forms.user import LoginForm, RegisterForm
from data import db_session
from data.users import User
from data.apps import App
import os
from flask_login import LoginManager, login_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user


def get_info():
    db_sess = db_session.create_session()
    table = {'apps': []}
    name_apps = [i.name_app.capitalize() for i in db_sess.query(App).all()]
    descriptions = [i.description.capitalize() for i in db_sess.query(App).all()]
    urls = [f'../app/{i.name_app}' for i in db_sess.query(App).all()]
    download_urls = [i.link for i in db_sess.query(App).all()]
    icons = [f'../{i.icon}' for i in db_sess.query(App).all()]
    for i in range(len(name_apps)):
        table['apps'].append({'name': name_apps[i], 'description': descriptions[i], 'url': urls[i], 'icon': icons[i],
                              'link': download_urls[i]})
    return table


@app.route('/')
@app.route('/home')
def home():
    return render_template('home_page.html', title='WinApp', table=get_info())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("../home")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data,
                    email=form.email.data,
                    surname=form.surname.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('../login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/app/<app_name>')
def app_page(app_name):
    table = get_info()
    for i in table['apps']:
        if i['name'] == app_name:
            table = i
            print(i)
            break
    return render_template('app_page.html', title=app_name, name=app_name, table=table)


@app.route('/addapp/<app_name>')
def add_app(app_name):
    os.mkdir(f'static/apps/{app_name}')
    app = App(name_app=app_name,
              description='Нелинейный видеоредактор с открытым исходным кодом на основе Framework MLT и KDE.',
              company='KDE',
              page_company='https://kde.org/',
              link='https://download.kde.org/stable/kdenlive/21.12/windows/kdenlive-21.12.3.exe',
              icon=f'static/apps/{app_name}/icon',
              user_id=1
              )
    db_sess = db_session.create_session()
    db_sess.add(app)
    db_sess.commit()
    return render_template('base.html')


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1', debug=True)
