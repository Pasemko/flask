from flask_testing import TestCase
# import model
from create_models import fillDB
# import create_tables
from main import main, create_user
import unittest
from marshmallow import ValidationError
from model import Session, Base, engine, User, Article, ArticleChange
from base64 import b64encode


class MyTest(TestCase):
    def create_app(self):
        app = main
        app.config['TESTING'] = True

        return app

    def setUp(self):
        # self.create_tables()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        fillDB()

    def tearDown(self):
        Session.remove()
        Session.close()
        Base.metadata.drop_all(engine)


    def test_create_user(self):
        self.assert200(self.client.post('/user', json={"username": "terminator", "name": "Andriy", "surname": "Pasemko", "email": "example@gmail.com", "password": "admin"}))
        self.assert400(self.client.post('/user', json={"username": "Test1", "name": "Andriy", "surname": "Pasemko",
                                                       "email": "example@gmail.com", "password": "admin"}))
        self.assert400(self.client.post('/user', json={"usname": "Tes1", "name": "Andriy", "surname": "Pasemko",
                                                       "email": "example@gmail.com", "password": "admin"}))


    def test_get_user(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')

        self.assert200(self.client.get('/user/2', headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.get('/user/8', headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.get('/user/3', headers={'Authorization': f'Basic {credentials}'}))

    def test_delete_user(self):
        credentials = b64encode(b"Test1:admin").decode('utf-8')
        self.assert403(self.client.delete('/user/2', headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.delete('/user/8', headers={'Authorization': f'Basic {credentials}'}))
        self.assert200(self.client.delete('/user/4', headers={'Authorization': f'Basic {credentials}'}))

    def test_edit_user(self):
        credentials = b64encode(b"Test3:admin").decode('utf-8')
        # self.assert400(self.client.put('/user/3', json={"username": "Test2", "name": "Andriy", "surname": "Pamko",
        #                                                 "email": "exampe@gmail.com", "password": "admin"},
        #                                headers={'Authorization': f'Basic {credentials}'}))
        #
        self.assert200(self.client.put('/user/3', json={"username": "termin", "name": "Andriy", "surname": "Pamko", "email": "exampe@gmail.com", "password": "admin"},
                                   headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.put('/user/12', json={"username": "termin", "name": "Andriy", "surname": "Pamko",
                                                        "email": "exampe@gmail.com", "password": "admin"},
                                       headers={'Authorization': f'Basic {credentials}'}))

    def test_articles(self):
        self.assert200(self.client.get('/articles'))

    def test_get_article(self):
        self.assert200(self.client.get('/articles/2'))
        self.assert404(self.client.get('/articles/10'))

    def test_delete_article(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert200(self.client.delete('/articles/2', headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.delete('/articles/20', headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.delete('/articles/1', headers={'Authorization': f'Basic {credentials}'}))

    def test_articles_changes(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert200(self.client.get('/articleChanges', headers={'Authorization': f'Basic {credentials}'}))


    def test_create_article_changes(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert200(self.client.post('/articleChanges', json={"title": "1st hanged", "text": "First text", "author_id": "2", "article_id": "2"},
                                       headers={'Authorization': f'Basic {credentials}'}))

        self.assert404(self.client.post('/articleChanges',
                                        json={"title": "1st hanged", "text": "First text", "author_id": "2",
                                              "article_id": "21"},
                                        headers={'Authorization': f'Basic {credentials}'}))
        self.assert400(self.client.post('/articleChanges',
                                        json={"title": "1st title", "text": "First text", "author_id": "2",
                                              "article_id": "-1"},
                                        headers={'Authorization': f'Basic {credentials}'}))
        # 'title': data['title'],
        # 'text': data['text'],
        # 'author_id': auth.current_user().id,
        # 'article_id': data['article_id'],


    def test_get_article_change(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert200(self.client.get('/articleChanges/2',headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.get('/articleChanges/1', headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.get('/articleChanges/18', headers={'Authorization': f'Basic {credentials}'}))


    def test_edit_article_change(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert200(self.client.put('/articleChanges/2',
                                        json={"title": "khkjhkj hanged", "text": "text", "author_id": "2",
                                              "article_id": "2"},
                                        headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.put('/articleChanges/5',
                                       json={"title": "khkjhkj hanged", "text": "text", "author_id": "2",
                                             "article_id": "2"},
                                       headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.put('/articleChanges/1',
                                       json={"title": "khkjhkj hanged", "text": "text", "author_id": "2",
                                             "article_id": "2"},
                                       headers={'Authorization': f'Basic {credentials}'}))
        self.assert400(self.client.put('/articleChanges/2',
                                       json={"title": "1st title", "text": "text", "author_id": "2",
                                             "article_id": "2"},
                                       headers={'Authorization': f'Basic {credentials}'}))

    def test_approve_article_change(self):
        credentials = b64encode(b"Test3:admin").decode('utf-8')
        self.assert404(self.client.get('/articleChanges/85/approve',headers={'Authorization': f'Basic {credentials}'}))
        self.assert200(self.client.get('/articleChanges/2/approve', headers={'Authorization': f'Basic {credentials}'}))

    def test_approve_article_change_2(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert404(self.client.get('/articleChanges/98/approve', headers={'Authorization': f'Basic {credentials}'}))
        # self.assert400(self.client.get('/articleChanges/2/approve', headers={'Authorization': f'Basic {credentials}'}))
        self.assert401(self.client.get('/articleChanges/1/approve', headers={'Authorization': f'Basic {credentials}'}))

    def test_delete_article_change(self):
        credentials = b64encode(b"Test2:admin").decode('utf-8')
        self.assert401(self.client.delete('/articleChanges/1', headers={'Authorization': f'Basic {credentials}'}))
        self.assert404(self.client.delete('/articleChanges/7', headers={'Authorization': f'Basic {credentials}'}))

    def test_delete_article_change_2(self):
        credentials = b64encode(b"Test3:admin").decode('utf-8')
        self.assert200(self.client.delete('/articleChanges/1', headers={'Authorization': f'Basic {credentials}'}))




if __name__ == '__main__':
    unittest.main()
