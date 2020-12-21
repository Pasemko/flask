from itertools import product
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from model import Article, User, ArticleChange, Session
from schemas import UserSchema, ArticleSchema, ArticleChangeSchema
from marshmallow import ValidationError


variant = list(product(
    ('python 3.8.*', 'python 3.7.*', 'python 3.6.*'),
    ('venv + requirements.txt', 'virtualenv + requirements.txt', 'poetry', 'pipenv')))[21 % 12]

main = Flask(__name__)
bcrypt = Bcrypt(main)
session = Session()


@main.route('/api/v1/hello-world-<string:var>')
def hello(var):
    return f'Hello World {var}'


def generate_unique_id(obj):
    obj_id_list = [i.id for i in list(session.query(obj).all())]
    if obj_id_list is []:
        return 1
    return list(set(list(range(1, max(obj_id_list) + 2))) - set(obj_id_list))[0]


@main.route('/user', methods=['POST'])
def create_user():
    data = request.json
    user_schema = UserSchema()
    parsed_data = {
        'username': data['username'],
        'name': data['name'],
        'surname': data['surname'],
        'email': data['email'],
        'password': bcrypt.generate_password_hash(data['password']).decode('utf-8'),
    }

    if not session.query(User).filter(User.username == parsed_data['username']).one_or_none() is None:
        return 'SUCH USERNAME ALREADY EXIST', '400'

    try:
        user = user_schema.load(parsed_data)
    except ValidationError as error:
        return error.messages, '400'
    user.id = generate_unique_id(User)
    user.is_moderator = False
    session.add(user)
    session.commit()

    return '200'


@main.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    found_user = session.query(User).filter(User.id == user_id).one_or_none()

    try:
        user = UserSchema(exclude=['password']).dump(found_user)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_user is None:
        return 'USER NOT FOUND', '404'

    return user, '200'


@main.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    found_user = session.query(User).filter(User.id == user_id).one_or_none()

    try:
        UserSchema().dump(found_user)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_user is None:
        return 'USER NOT FOUND', '404'

    session.delete(found_user)
    session.commit()
    return '200'


@main.route('/user/<user_id>', methods=['PUT'])
def edit_user(user_id):
    found_user = session.query(User).filter(User.id == user_id).one_or_none()

    if found_user is None:
        return 'USER NOT FOUND', '404'

    try:
        UserSchema().dump(found_user)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    data = request.json
    if found_user is session.query(User).filter(User.username == data['username']).one_or_none():
        return 'SUCH USERNAME ALREADY EXIST', '400'

    found_user.username = data['username']
    found_user.name = data['name']
    found_user.surname = data['surname']
    found_user.email = data['email']

    session.commit()
    return UserSchema(exclude=['password']).dump(found_user), '200'


@main.route('/user/login', methods=['GET'])
def login():
    pass    # TODO


@main.route('/user/logout', methods=['GET'])
def logout():
    pass    # TODO


@main.route('/articles', methods=['GET'])
def articles():

    article_list = session.query(Article).filter(Article.title != 'MOD REVIEW')
    if article_list:
        return jsonify(ArticleSchema(many=True).dump(article_list)), '200'
    else:
        return 'ARTICLES NOT FOUND', '404'


@main.route('/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    found_article = session.query(Article).filter(Article.id == article_id).one_or_none()

    try:
        article = ArticleSchema().dump(found_article)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_article is None:
        return 'ARTICLE NOT FOUND', '404'

    return article, '200'


@main.route('/articles/<article_id>', methods=['DELETE'])
def delete_article(article_id):
    found_article = session.query(Article).filter(Article.id == article_id).one_or_none()

    try:
        ArticleSchema().dump(found_article)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_article is None:
        return 'ARTICLE NOT FOUND', '404'

    session.delete(found_article)
    session.commit()
    return ''


# TODO: ArticleChanges must be visible for moderators and author only:
#  If not modefrator or author needed to return 401 ERROR

@main.route('/articleChanges', methods=['GET'])
def articles_changes():
    article_changes_list = session.query(ArticleChange)
    if article_changes_list:
        return jsonify(ArticleSchema(many=True).dump(article_changes_list)), '200'
    else:
        return 'ARTICLE NOT FOUND', '404'


@main.route('/articleChanges', methods=['POST'])
def create_article_changes():
    data = request.json
    article_change_schema = ArticleChangeSchema()
    parsed_data = {
        'title': data['title'],
        'text': data['text'],
        'author_id': data['author_id'],
        'article_id': data['article_id'],   # If u wanna create new article put here '-1'!
    }

    if not session.query(Article).filter(Article.title == parsed_data['title'] and Article.title != 'MOD REVIEW').one_or_none() is None or\
            not session.query(ArticleChange).filter(ArticleChange.title == parsed_data['title']).one_or_none() is None:
        return 'SUCH USERNAME ALREADY EXIST', '400'

    if parsed_data['article_id'] == '-1':
        new_id = generate_unique_id(Article)
        session.add(ArticleSchema().load({'title': 'MOD REVIEW',
                                          'text': 'MOD REVIEW',
                                          'id': f'{new_id}',
                                          'author_id': parsed_data['author_id']}
                                         ))
        parsed_data['article_id'] = str(new_id)

    else:
        found_article = session.query(Article).filter(Article.id == int(parsed_data['article_id'])).one_or_none()
        try:
            ArticleSchema().dump(found_article)
        except ValidationError as error:
            return error.messages, 'INVALID ID', '400'

        if found_article is None:
            return 'ARTICLE NOT FOUND', '404'

    try:
        article_change = article_change_schema.load(parsed_data)
    except ValidationError as error:
        return error.messages, '400'

    article_change.id = generate_unique_id(ArticleChange)
    session.add(article_change)
    session.commit()

    return '200'


@main.route('/articleChanges/<change_id>', methods=['GET'])
def get_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    try:
        article_change = ArticleChangeSchema().dump(found_article_change)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_article_change is None:
        return 'ARTICLE_CHANGE NOT FOUND', '404'

    return article_change, '200'


@main.route('/articleChanges/<change_id>', methods=['PUT'])
def edit_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    if found_article_change is None:
        return 'ARTICLE_CHANGE NOT FOUND', '404'

    data = request.json
    if not session.query(Article).filter(Article.title == data['title'] and Article.title != 'MOD REVIEW').one_or_none() is None or \
            not session.query(ArticleChange).filter(ArticleChange.title == data['title']).one_or_none() is None:
        return 'SUCH TITLE ALREADY EXIST', '400'

    try:
        article_change = ArticleChangeSchema().dump(found_article_change)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    found_article_change.title = data['title']
    found_article_change.text = data['text']

    session.commit()
    return article_change, '200'


@main.route('/articleChanges/<change_id>/approve', methods=['GET'])
def approve_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    try:
        ArticleChangeSchema().dump(found_article_change)
    except ValidationError as error:
        return error.messages, 'Invalid ID', '400'

    if found_article_change is None:
        return 'ArticleChange not found', '404'

    found_article = session.query(Article).filter(Article.id == found_article_change.article_id).one_or_none()
    found_article.title = found_article_change.title
    found_article.text = found_article_change.text

    session.delete(found_article_change)
    session.commit()

    return ArticleSchema().dump(found_article), '200'


@main.route('/articleChanges/<change_id>', methods=['DELETE'])
def delete_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    if found_article_change is None:
        return 'ArticleChange not found', '404'

    try:
        ArticleChangeSchema().dump(found_article_change)
    except ValidationError as error:
        return error.messages, 'Invalid ID', '400'

    session.delete(found_article_change)
    session.commit()
    return '200'


if __name__ == '__main__':
    print(variant)

    main.run(debug=True)


"""

_______USER METHODS________

1) create_user
curl -X POST http://127.0.0.1:5000/user -H "Content-Type: application/json" --data "{\"username\": \"terminator\", \"name\": \"Andriy\", \"surname\": \"Pasemko\", \"email\": \"example@gmail.com\", \"password\": \"admin\"}"

2) get_user
curl -X GET http://127.0.0.1:5000/user/1

3) delete_user
curl -X DELETE http://127.0.0.1:5000/user/1

4) edit_user
curl -X PUT http://127.0.0.1:5000/user/4 -H "Content-Type: application/json" --data "{\"username\": \"terminator\", \"name\": \"Andriy\", \"surname\": \"Pasemko\", \"email\": \"example@gmail.com\", \"password\": \"admin\"}"

_______ARTICLE METHODS________

1) articles
curl -X GET http://127.0.0.1:5000/articles

2) get_article
curl -X GET http://127.0.0.1:5000/articles/1

3) delete_article
curl -X DELETE http://127.0.0.1:5000/articles/1


_______СHANGE METHODS________

1) article_changes
curl -X GET http://127.0.0.1:5000/articleChanges

2) create_article_changes
curl -X POST http://127.0.0.1:5000/articleChanges -H "Content-Type: application/json" --data "{\"title\": \"1st title changed\", \"text\": \"First text\", \"author_id\": \"4\", \"article_id\": \"2\"}"

3) get_article_change
curl -X GET http://127.0.0.1:5000/articleChanges/1

4) edit_article_change
curl -X PUT http://127.0.0.1:5000/articleChanges/3 -H "Content-Type: application/json" --data "{\"title\": \"1st title new\", \"text\": \"First text\"}"

5) delete_article_change
curl -X DELETE http://127.0.0.1:5000/articleChanges/3

6) approve_article_change
curl -X GET http://127.0.0.1:5000/articleChanges/3/approve

"""
