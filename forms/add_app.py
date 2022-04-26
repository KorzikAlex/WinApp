import os
from data.apps import App
from data import db_session
import json


def add_app():
    answer = input('Режим json/Вручную(впишите нужный вариант)')
    if answer.lower() == 'вручную':
        a = ''
        while a == '' or a.lower() == 'y' or a.lower() == 'да' or a.lower() == 'yes':
            name = input('Имя приложения:')
            os.mkdir(f'static/apps/{name}')

            description = input('Описание: ')
            company = input('Название компании: ')
            page_company = input('Cайт компании: ')
            link = input('Прямая ссылка на скачивание: ')

            icon_href = input('Cсылка на иконку приложения: ')
            with open(icon_href, 'rb') as file:
                icon = file.read()
            icon_href = icon_href.split('.')[-1]
            with open(f'static/apps/{name}/icon.{icon_href}', 'wb') as file:
                file.write(icon)

            app = App(name_app=name,
                      description=description,
                      company=company,
                      page_company=page_company,
                      link=link,
                      icon=f'static/apps/{name}/icon.{icon_href}')

            db_sess = db_session.create_session()
            db_sess.add(app)
            db_sess.commit()

            a = input('App is added! Хотите добавить ещё? ')
    if answer.lower() == 'режим json':
        a = input('Ccылка на файл: ')
        with open(a, encoding='UTF-8') as file:
            lines = json.load(file)
        for name, data in lines.items():
            os.mkdir(f'static/apps/{name}')
            description = data['description']
            company = data['company']
            page_company = data['page_company']
            link = data['link']
            icon_href = data['icon']
            with open(icon_href, 'rb') as file:
                icon = file.read()
            icon_href = icon_href.split('.')[-1]
            with open(f'static/apps/{name}/icon.{icon_href}', 'wb') as file:
                file.write(icon)

            app = App(name_app=name,
                      description=description,
                      company=company,
                      page_company=page_company,
                      link=link,
                      icon=f'static/apps/{name}/icon.{icon_href}')
            db_sess = db_session.create_session()
            db_sess.add(app)
            db_sess.commit()
            print('Apps is added!')
