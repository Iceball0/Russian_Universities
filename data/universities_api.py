from flask import jsonify
from flask_restful import abort, Resource
from sqlalchemy.sql import func
from data import db_session
from data.universities import Universities
from data.news import News
from data.reviews import Reviews
from bs4 import BeautifulSoup
from requests import get


class UniversitiesResource(Resource):
    def get(self, university_id):
        abort_if_university_not_found(university_id)
        db_sess = db_session.create_session()
        university = db_sess.query(Universities).get(university_id)
        news = parser(university_id)
        avg = db_sess.query(func.avg(Reviews.rating)).filter(Reviews.university_id == university_id).first()[0]
        count = db_sess.query(func.count(Reviews.rating)).filter(Reviews.university_id == university_id).first()[0]
        return jsonify(
            {
                'university': university.to_dict(only=(
                    'name', 'description', 'city', 'image', 'placeInRussianTop',
                    'specialties.budgetary_places',
                    'specialties.specialties.name', 'specialties.specialties.code',
                    'specialties.specialties.description',
                    'reviews.user_name', 'reviews.text', 'reviews.rating')),
                'news': news,
                'avg': avg,
                'count': count
            }
        )


class UniversitiesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        university = db_sess.query(Universities).all()
        return jsonify(
            {
                'universities':
                    [item.to_dict(only=('id', 'name', 'description', 'city', 'image', 'placeInRussianTop'))
                     for item in university],
                'ratings':
                    [db_sess.query(func.avg(Reviews.rating)).filter(Reviews.university_id == item.id).first()[0]
                     for item in university],
                'counts':
                    [db_sess.query(func.count(Reviews.rating)).filter(Reviews.university_id == item.id).first()[0]
                     for item in university],
            }
        )


def abort_if_university_not_found(university_id):
    session = db_session.create_session()
    university = session.query(Universities).get(university_id)
    if not university:
        abort(404, message=f"University {university_id} not found")


def parser(university_id):
    session = db_session.create_session()
    news = session.query(News).get(university_id)

    r = get(news.url)
    soup = BeautifulSoup(r.text, 'html.parser')

    titles = []
    texts = []
    dates = []

    for link in soup.find_all(news.title.split()[0], class_=news.title.split()[1])[:5]:
        titles.append(link.text.strip())

    for link in soup.find_all(news.date.split()[0], class_=news.date.split()[1])[:5]:
        dates.append(' '.join(link.text.strip().split()))

    if news.text != '':
        for link in soup.find_all(news.text.split()[0], class_=news.text.split()[1])[:5]:
            texts.append(link.text.strip())

    news_li = []
    for i in range(5):
        dict1 = {'title': titles[i], 'text': texts[i], 'date': dates[i]}
        news_li.append(dict1)

    return news_li
