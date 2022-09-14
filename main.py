# импорт библиотек и модулей
import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_restful import abort, Api
from requests import get
from sqlalchemy.sql import func
from authlib.integrations.flask_client import OAuth
from data import db_session, specialties_api, universities_api
from data.universities_specialties import Universities_Specialties
from data.universities import Universities
from data.specialties import Specialties
from data.reviews import Reviews
from data.news import News
from data.users import User
from data.parser import parser

# инициализация Flask и login manager
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'russian_universities_secret_key_1396'
login_manager = LoginManager()
login_manager.init_app(app)

# oauth config
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='652011356373-89fc26iqg67fpdk027qoc1svh2jk4mlp.apps.googleusercontent.com',
    client_secret='dP9EcZYCTvbWnCxcpA18U2mm',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)


def main():
    # инициализация базы данных
    db_session.global_init("db/universities.db")

    # нициализация api
    api.add_resource(specialties_api.SpecialtiesListResource, '/api/specialties')
    api.add_resource(specialties_api.SpecialtiesResource, '/api/specialties/<int:specialty_id>')

    api.add_resource(universities_api.UniversitiesListResource, '/api/universities')
    api.add_resource(universities_api.UniversitiesResource, '/api/universities/<int:university_id>')

    # запуск приложения
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


# загрузка аккаунта администратора
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# загрузка начальной страницы
@app.route("/", methods=['POST', 'GET'])
def index():
    db_sess = db_session.create_session()

    # удаление сессии регистрации
    if 'profile' in session:
        session.pop('profile', None)

    message = ''

    # проверка на POST запрос
    if request.method == 'POST':
        # перенаправление на главную страницу при попытке отправить POST запрос неавторизованным пользователем
        if not current_user.is_authenticated:
            return redirect("/")

        # если запрос был отправлен из формы добавления университета
        if 'add-submit' in request.form:
            # добавляем данные формы в БД
            university_add = Universities()
            university_add.name = request.form['title']
            university_add.description = request.form['description']
            university_add.city = request.form['city']
            university_add.placeInRussianTop = request.form['TopInRussia']

            # получаем файл картинки из формы, сохраняем и заносим название в БД
            f = request.files['photo']
            f.save(f'static/images/universities/{f.filename}')
            university_add.image = f.filename

            # добавляем все данные в БД, комитим и перенаправляем на главную страницу
            db_sess.add(university_add)
            db_sess.commit()
            redirect('/')

        # если запрос был отправлен из формы редактирования университета
        else:
            # получаем данные университета из БД по айди
            university_edit = db_sess.query(Universities).filter(Universities.id == request.form['univ-id']).first()

            # если такой университет существует, то редактируем его, иначе вызываем ошибку 404
            if university_edit:
                # редактируем данные, заменяя их на данные из формы
                university_edit.name = request.form['title']
                university_edit.description = request.form['description']
                university_edit.city = request.form['city']
                university_edit.placeInRussianTop = request.form['TopInRussia']

                # если был прикреплён файл картинки, то сохраняем её, удаляем прошлую и запоминаем название в БД
                if request.files['photo']:
                    f = request.files['photo']
                    try:
                        os.remove(f'static/images/universities/{university_edit.image}')
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        message = e
                    f.save(f'static/images/universities/{f.filename}')
                    university_edit.image = f.filename

                # подтверждаем изменения и возвращаемся на главную страницу
                db_sess.commit()
                redirect('/')
            else:
                abort(404)

    # получаем список всех университетов, а также массивы из оценок и количества отзывов каждого из них
    all_universities = db_sess.query(Universities).all()
    ratings = [db_sess.query(func.avg(Reviews.rating)).filter(Reviews.university_id == item.id).first()[0]
               for item in all_universities]
    counts = [db_sess.query(func.count(Reviews.rating)).filter(Reviews.university_id == item.id).first()[0]
              for item in all_universities]

    # загружаем страницу и передаём все нужные данные
    return render_template('index.html', universities=all_universities, counts=counts, ratings=ratings, message=message)


# загрузка страницы отдельного вуза
@app.route("/universities/<int:university_id>", methods=['POST', 'GET'])
def university(university_id):
    # проверяем существование вуза по его айди и в случае успеха создаём сессию
    abort_if_university_not_found(university_id)
    db_sess = db_session.create_session()

    # проверка на POST запрос
    if request.method == 'POST':
        # перенаправление на страницу вуза при попытке отправить POST запрос неавторизованным пользователем
        if not current_user.is_authenticated:
            return redirect(f"/universities/{university_id}")

        # если запрос был отправлен из формы редактирования новостного раздела
        if 'edit-news-submit' in request.form:
            # получаем данные университета из БД по айди
            news_edit = db_sess.query(News).get(university_id)
            edit = True

            # если данные существуют, то редактируем их и сохраняем, иначе добавляем их
            if not news_edit:
                news_edit = News()
                edit = False
            news_edit.url = request.form['url']
            news_edit.block = request.form['block']
            news_edit.title = request.form['title']
            news_edit.image = request.form['image']
            if request.form['text'] == '-':
                news_edit.text = ''
            else:
                news_edit.text = request.form['text']
            news_edit.date = request.form['date']
            news_edit.news_url = request.form['news_url']
            if not edit:
                db_sess.add(news_edit)
            db_sess.commit()
            redirect(f'/university/{university_id}')

        # если запрос был отправлен из формы добавления отзывов
        elif 'add-submit' in request.form:
            # добавляем отзыв в БД
            review = Reviews()
            if current_user.permission == 'user':
                review.user_name = f"{current_user.surname} {current_user.name}"
            else:
                review.user_name = request.form['name']
            review.user_email = current_user.login
            review.text = request.form['opinion']
            review.rating = request.form['rating']
            review.university_id = university_id
            db_sess.add(review)
            db_sess.commit()
            redirect(f'/university/{university_id}')

        # если запрос был отправлен из формы редактирования специальностей вуза
        elif 'edit-specialties-submit' in request.form:
            for i in enumerate(request.form.getlist('checkbox')):
                connection = db_sess.query(Universities_Specialties).filter(
                    Universities_Specialties.university_id == university_id,
                    Universities_Specialties.specialty_id == i[0] + 1).first()
                if i[1]:
                    if not connection:
                        connection = Universities_Specialties()
                        connection.university_id = university_id
                        connection.specialty_id = i[0] + 1
                        db_sess.add(connection)
                        db_sess.commit()
                        redirect(f'/university/{university_id}')
                else:
                    if connection:
                        db_sess.delete(connection)
                        db_sess.commit()
                        redirect(f'/university/{university_id}')

        # если запрос был отправлен из формы редактирования количества бюджетных мест
        elif 'edit-budgetary_places-submit' in request.form:
            connection = db_sess.query(Universities_Specialties).filter(
                Universities_Specialties.university_id == university_id,
                Universities_Specialties.specialty_id == request.form['spec-id']).first()
            connection.budgetary_places = request.form['budgetary_places']
            db_sess.commit()
            redirect(f'/university/{university_id}')

    # получем данные университета и его новостей из БД, координаты из api поиска по орг, оценку вуза, и парсим новости
    university_data = db_sess.query(Universities).get(university_id)
    all_specialties = db_sess.query(Specialties).all()
    university_specialties_id = [i.specialties.id for i in university_data.specialties]
    news_ = db_sess.query(News).get(university_id)
    coordinates = finder(university_data.name)
    if news_:
        news = parser(university_id)
        news_url = news_.url
        avg = db_sess.query(func.avg(Reviews.rating)).filter(Reviews.university_id == university_id).first()[0]
        if not avg:
            avg = 0
        else:
            avg = round(avg, 1)
    else:
        news = []
        avg = 0
        news_url = ''
    return render_template('university.html', university=university_data, avg=avg, news=news, news_url=news_url,
                           coordinates=coordinates, news_data=news_, specialties=all_specialties,
                           university_specialties_id=university_specialties_id)


# загрузка страницы со специальностями
@app.route("/specialties", methods=['POST', 'GET'])
def specialties():
    # создание сессии
    db_sess = db_session.create_session()

    message = ''

    # проверка на POST запрос
    if request.method == 'POST':
        # перенаправление на страницу специальностей при попытке отправить POST запрос неавторизованным пользователем
        if not current_user.is_authenticated:
            return redirect("/specialties")

        # если запрос был отправлен из формы добавления специальности
        if 'add-submit' in request.form:
            # добавляем данные формы в БД
            specialty_add = Specialties()
            specialty_add.name = request.form['title']
            specialty_add.description = request.form['description']
            specialty_add.code = request.form['code']

            # получаем файл картинки из формы, сохраняем и заносим название в БД
            f = request.files['photo']
            filename = f.filename.split('.')[-1]
            f.save(f"static/images/specialties/{request.form['code']}.{filename}")
            specialty_add.image = f"{request.form['code']}.{filename}"

            # добавляем все данные в БД, комитим и перенаправляем на страницу специальностей
            db_sess.add(specialty_add)
            db_sess.commit()
            redirect('/specialties')

        # если запрос был отправлен из формы редактирования специальности
        else:
            # получаем данные специальности из БД по айди
            specialty_edit = db_sess.query(Specialties).filter(Specialties.id == request.form['spec-id']).first()

            # если такой специальность существует, то редактируем её, иначе вызываем ошибку 404
            if specialty_edit:
                # редактируем данные, заменяя их на данные из формы
                specialty_edit.name = request.form['title']
                specialty_edit.description = request.form['description']
                specialty_edit.code = request.form['code']

                # если был прикреплён файл картинки, то сохраняем её, удаляем прошлую и запоминаем название в БД
                if request.files['photo']:
                    f = request.files['photo']
                    try:
                        os.remove(f'static/images/specialties/{specialty_edit.image}')
                    except FileNotFoundError:
                        pass
                    except Exception as e:
                        message = e
                    filename = f.filename.split('.')[-1]
                    f.save(f"static/images/specialties/{request.form['code']}.{filename}")
                    specialty_edit.image = f"{request.form['code']}.{filename}"

                # подтверждаем изменения и возвращаемся на страницу специальностей
                db_sess.commit()
                redirect('/specialties')
            else:
                abort(404)

    # получаем список всех специальностей, загружаем страницу и передаём все нужные данные
    all_specialties = db_sess.query(Specialties).all()

    return render_template('specialties.html', specialties=all_specialties, message=message)


# отображение страницы ошибки
@app.errorhandler(404)
def error_404(e):
    return render_template('404.html')


# функция, проверяющая существование вуза и вызывающая 404 при его отсутствии
def abort_if_university_not_found(university_id):
    abort_session = db_session.create_session()
    university_data = abort_session.query(Universities).get(university_id)
    if not university_data:
        abort(404, message=f"University {university_id} not found")


# функция, проверяющая существование специальности и вызывающая 404 при её отсутствии
def abort_if_specialty_not_found(specialty_id):
    abort_session = db_session.create_session()
    specialty_data = abort_session.query(Specialties).get(specialty_id)
    if not specialty_data:
        abort(404, message=f"Specialty {specialty_id} not found")


# загрузка страницы с отдельной специально
@app.route("/specialties/<int:specialty_id>")
def specialty(specialty_id):
    # проверяем существование специальности по её айди и в случае успеха создаём сессию, получаем данные и загружаем стр
    abort_if_specialty_not_found(specialty_id)
    db_sess = db_session.create_session()
    specialty_data = db_sess.query(Specialties).get(specialty_id)
    return render_template('specialty.html', specialty=specialty_data)


# обработка формы авторизации
@app.route("/login", methods=['POST', 'GET'])
def login():
    # если пользователь уже авторизирован, то возвращаем его на главную страницу
    if current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        # авторизируем пользователя
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == request.form['login']).first()
        if user and user.check_password(request.form['password'].lower()):
            if request.form['remember']:
                remember = True
            else:
                remember = False
            login_user(user, remember=remember)
            return redirect("/")
        else:
            return render_template('login.html',
                                   message="Неправильный логин или пароль")

    # загружаем страницу авторизации
    return render_template('login.html')


# обработка формы регистрации
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    # если нет сессии авторизации, то возвращаем его на страницу авторизации
    if 'profile' not in session:
        return redirect("/login")

    # проверяем пароль
    if request.method == 'POST':
        if request.form['password'] == request.form['password2']:
            if request.form['password'].lower() not in 'qwertyuiopasdfghjklzxcvbnm1234567890':
                # регистрируем пользователя
                db_sess = db_session.create_session()
                user = User()
                user.login = session['profile']['email']
                user.surname = session['profile']['family_name']
                user.name = session['profile']['given_name']
                user.permission = 'user'
                user.set_password(request.form['password'].lower())
                if request.form['remember']:
                    remember = True
                else:
                    remember = False
                db_sess.add(user)
                db_sess.commit()
                session.pop('profile', None)
                login_user(user, remember=remember)
                return redirect("/")
            else:
                return render_template('login.html',
                                       message="Пароль слишком простой", signup=True)
        else:
            return render_template('login.html',
                                   message="Пароли не совпадают", signup=True)

    # загружаем страницу авторизации
    return render_template('login.html', signup=True)


# обработка выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# авторизация через Google аккаунт
@app.route('/login_google')
def login_google():
    # если пользователь уже авторизирован, то возвращаем его на главную страницу
    if current_user.is_authenticated:
        return redirect("/")

    google_client = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google_client.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    try:
        google_auth = oauth.create_client('google')
        token = google_auth.authorize_access_token()
        resp = google_auth.get('userinfo')
        user_info = resp.json()
        # do something with the token and profile
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == user_info['email']).first()
        if user:
            login_user(user, remember=True)
            return redirect("/")
        else:
            session['profile'] = user_info
            return redirect('/signup')
    except Exception:
        return redirect('/')


# удаление вуза из БД
@app.route('/delete_university/<int:univ_id>', methods=['POST', 'GET'])
@login_required
def delete_univ(univ_id):
    if current_user.permission != 'admin':
        return redirect('/')

    db_sess = db_session.create_session()
    delete_university = db_sess.query(Universities).get(univ_id)

    # если вуз существует то удаляем, иначе вызываем 404
    if delete_university:
        # получаем все связанные с вузом специальности и удаляем связь с ними
        delete_specialties_connection = db_sess.query(Universities_Specialties).filter(Universities_Specialties.university_id == univ_id).all()
        if delete_specialties_connection:
            for i in delete_specialties_connection:
                db_sess.delete(i)
                db_sess.commit()

        # удаляем отзывы к вузу
        for i in delete_university.reviews:
            db_sess.delete(i)

        un_news = db_sess.query(News).get(univ_id)
        if un_news:
            db_sess.delete(un_news)

        # удаляем картинку
        os.remove(f'static/images/universities/{delete_university.image}')

        # подтверждаем удаление
        db_sess.delete(delete_university)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/")


# удаление специальности из БД
@app.route('/delete_specialty/<int:spec_id>', methods=['POST', 'GET'])
@login_required
def delete_spec(spec_id):
    if current_user.permission != 'admin':
        return redirect('/')

    db_sess = db_session.create_session()
    delete_specialty = db_sess.query(Specialties).get(spec_id)

    # если специальность существует то удаляем, иначе вызываем 404
    if delete_specialty:
        # получаем все связанные со специальностью вузы и удаляем связь с ними
        delete_universities_connection = db_sess.query(Universities_Specialties).filter(Universities_Specialties.specialty_id == spec_id).all()
        if delete_universities_connection:
            for i in delete_universities_connection:
                db_sess.delete(i)
                db_sess.commit()

        # удаляем картинку
        os.remove(f'static/images/specialties/{delete_specialty.image}')

        # подтверждаем удаление
        db_sess.delete(delete_specialty)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/specialties")


# удаление отзывов
@app.route('/delete_review/<int:review_id>', methods=['POST', 'GET'])
@login_required
def delete_review(review_id):
    db_sess = db_session.create_session()
    review = db_sess.query(Reviews).get(review_id)

    # если отзыв существует то удаляем, иначе вызываем 404
    if review:
        if review.user_email != current_user.login and current_user.permission != 'admin':
            return redirect('/')
        university_id = review.university_id

        # подтверждаем удаление
        db_sess.delete(review)
        db_sess.commit()

        return redirect(f"/universities/{university_id}")
    else:
        abort(404)


# олучаем координаты вуза по названию с api поиска по организациям
def finder(university_name):
    name = university_name.split()[:-1]

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "cba79e6e-d6c1-4dd8-8f2c-d758602c9480"

    search_params = {
        "apikey": api_key,
        "text": ' '.join(name),
        "lang": "ru_RU",
        "type": "biz"
    }

    response = get(search_api_server, params=search_params)
    if not response:
        return []

    json_response = response.json()

    organization = json_response["features"][0]

    point = organization["geometry"]["coordinates"]
    return point


if __name__ == '__main__':
    main()
