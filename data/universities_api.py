from flask import jsonify
from flask_restful import abort, Resource
from sqlalchemy.sql import func
from data import db_session
from data.universities import Universities
from data.news import News
from data.reviews import Reviews
from bs4 import BeautifulSoup
from requests import get
from data.parser import parser


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
