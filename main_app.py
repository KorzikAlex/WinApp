from flask import Flask, url_for, render_template, redirect, request
from forms.user import LoginForm, RegisterForm
from data import db_session
from data.users import User
from data.apps import App
import os
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.add_app import add_app

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def get_info(key=''):
    db_sess = db_session.create_session()
    table = {'apps': []}
    if key:
        name_apps = [i.name_app for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        descriptions = [i.description for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        companies = [i.company for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        pages_companies = [i.page_company for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        urls = [f'../app/{i.name_app}' for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        download_urls = [i.link for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        icons = [f'../{i.icon}' for i in db_sess.query(App).filter(App.name_app.like(f'%{key}%'))]
        for i in range(len(name_apps)):
            table['apps'].append(
                {'name': name_apps[i], 'description': descriptions[i], 'url': urls[i], 'icon': icons[i],
                 'link': download_urls[i], 'company': companies[i], 'page_company': pages_companies[i]})
    else:
        name_apps = [i.name_app for i in db_sess.query(App).all()]
        descriptions = [i.description for i in db_sess.query(App).all()]
        pages_companies = [i.page_company for i in db_sess.query(App).all()]
        companies = [i.company for i in db_sess.query(App).all()]
        urls = [f'../app/{i.name_app}' for i in db_sess.query(App).all()]
        download_urls = [i.link for i in db_sess.query(App).all()]
        icons = [f'../{i.icon}' for i in db_sess.query(App).all()]
        for i in range(len(name_apps)):
            table['apps'].append(
                {'name': name_apps[i], 'description': descriptions[i], 'url': urls[i], 'icon': icons[i],
                 'link': download_urls[i], 'company': companies[i], 'page_company': pages_companies[i]})
    return table


@app.route('/search/<search>', methods=['GET', 'POST'])
def app_search(search):
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            redirect(f'/{search}')
        redirect('/')
    table = get_info(key=search)
    return render_template('search_page.html', title='Поиск', table=table, search=search,
                               count_search=len(table["apps"]))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('home_page.html', title='WinApp', table=get_info())
    elif request.method == 'POST':
        search = request.form.get('search')
        if search:
            return redirect(f'/search/{search}')
        return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    search = request.form.get('search')
    if search:
        return redirect(f'/search/{search}')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("..")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    search = request.form.get('search')
    if search:
        return redirect(f'/search/{search}')
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
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/app/<app_name>', methods=['GET', 'POST'])
def app_page(app_name):
    search = request.form.get('search')
    if search:
        return redirect(f'../search/{search}')
    table = get_info()
    for i in table['apps']:
        if i['name'] == app_name:
            table = i
            print(i)
            break
    return render_template('app_page.html', title=app_name, name=app_name, table=table)


if __name__ == '__main__':
    # answer = input('Вы хотите добавить приложение?(Y/n) ')
    db_session.global_init("db/users_apps.db")
    # if answer.lower() == 'y' or answer.lower() == 'yes':
    #     add_app()
    # чтобы не запускать режим добавления приложений нужно закомментировать начальную и верхние 2 строчки
    # OBSStudio не трогайте
    app.run(port=8080, host='127.0.0.1', debug=False)
