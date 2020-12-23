from itertools import product
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from model import Article, User, ArticleChange, Session
from schemas import UserSchema, ArticleSchema, ArticleChangeSchema
from marshmallow import ValidationError
from flask_httpauth import HTTPBasicAuth

variant = list(product(
    ('python 3.8.*', 'python 3.7.*', 'python 3.6.*'),
    ('venv + requirements.txt', 'virtualenv + requirements.txt', 'poetry', 'pipenv')))[21 % 12]

main = Flask(__name__)
bcrypt = Bcrypt(main)
session = Session()
auth = HTTPBasicAuth()


@main.route('/api/v1/hello-world-<string:var>')
def hello(var):
    return f'Hello World {var}'


@auth.verify_password
def verify_password(username, password):
    found_user = session.query(User).filter_by(username=username).one_or_none()

    if found_user is not None and bcrypt.check_password_hash(found_user.password, password):
        return found_user


@main.route('/user', methods=['POST'])
def create_user():
    try:
        user = UserSchema().load(request.json)
    except ValidationError as error:
        return error.messages, '400'

    if session.query(User).filter(User.username == user.username).one_or_none() is not None:
        return 'SUCH USERNAME ALREADY EXIST', '400'

    user.password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')

    session.add(user)
    session.commit()

    return '', '200'


@main.route('/user/<user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    user_id = int(user_id)
    found_user = session.query(User).filter_by(id=user_id).one_or_none()

    try:
        user = UserSchema(exclude=['password']).dump(found_user)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_user is None:
        return 'USER NOT FOUND', '404'

    if found_user.id != auth.current_user().id:
        return 'You don\'t have required permission', '401'

    return user, '200'


@main.route('/user/<user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    if auth.current_user().id != user_id:
        return 'You can\'t delete this user!', '401'

    found_user = session.query(User).filter(User.id == user_id).one_or_none()

    if found_user is None:
        return 'USER NOT FOUND', '404'

    try:
        UserSchema().dump(found_user)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    session.delete(found_user)
    session.commit()
    return '', '200'


@main.route('/user/<user_id>', methods=['PUT'])
@auth.login_required
def edit_user(user_id):
    user_id = int(user_id)

    if auth.current_user().id != user_id:
        return 'You can\'t update this user!', '401'

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
@auth.login_required
def delete_article(article_id):
    found_article = session.query(Article).filter(Article.id == article_id).one_or_none()

    try:
        ArticleSchema().dump(found_article)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_article is None:
        return 'ARTICLE NOT FOUND', '404'

    if not auth.current_user().is_moderator and found_article.author != auth.current_user():
        return 'You don\'t have permission to delete article', '401'

    session.delete(found_article)
    session.commit()
    return ''


@main.route('/articleChanges', methods=['GET'])
@auth.login_required
def articles_changes():
    article_changes_list = session.query(ArticleChange)
    if not auth.current_user().is_moderator:
        article_changes_list = article_changes_list.filter_by(author=auth.current_user())

    if article_changes_list:
        return jsonify(ArticleSchema(many=True).dump(article_changes_list)), '200'
    else:
        return 'ARTICLE NOT FOUND', '404'


@main.route('/articleChanges', methods=['POST'])
@auth.login_required
def create_article_changes():
    data = request.json
    article_change_schema = ArticleChangeSchema()
    parsed_data = {
        'title': data['title'],
        'text': data['text'],
        'author_id': auth.current_user().id,
        'article_id': data['article_id'],  # If u wanna create new article put here '-1'!
    }

    if parsed_data['article_id'] == -1:
        if session.query(Article).filter(
                Article.title == parsed_data['title'] and Article.title != 'MOD REVIEW').one_or_none() is not None \
                or session.query(ArticleChange).filter_by(title=parsed_data['title']).one_or_none() is not None:
            return 'SUCH USERNAME ALREADY EXIST', '400'

        temp_art = ArticleSchema().load({'title': 'MOD REVIEW',
                                         'text': 'MOD REVIEW',
                                         'author_id': parsed_data['author_id']}
                                        )
        session.add(temp_art)
        session.commit()
        parsed_data['article_id'] = temp_art.id
    else:
        found_article = session.query(Article).filter(Article.id == parsed_data['article_id']).one_or_none()
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

    session.add(article_change)
    session.commit()

    return '', '200'


@main.route('/articleChanges/<change_id>', methods=['GET'])
@auth.login_required
def get_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    try:
        article_change = ArticleChangeSchema().dump(found_article_change)
    except ValidationError as error:
        return error.messages, 'INVALID ID', '400'

    if found_article_change is None:
        return 'ARTICLE_CHANGE NOT FOUND', '404'

    if not auth.current_user().is_moderator and found_article_change.author != auth.current_user():
        return 'You don\'t have permission to view this article', '401'

    return article_change, '200'


@main.route('/articleChanges/<change_id>', methods=['PUT'])
@auth.login_required
def edit_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    if found_article_change is None:
        return 'ARTICLE_CHANGE NOT FOUND', '404'

    if not auth.current_user().is_moderator and found_article_change.author != auth.current_user():
        return 'You don\'t have permission to edit this article', '401'

    data = request.json
    if not session.query(Article).filter(
            Article.title == data['title'] and Article.title != 'MOD REVIEW').one_or_none() is None or \
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
@auth.login_required
def approve_article_change(change_id):
    if not auth.current_user().is_moderator:
        return 'You don\'t have required permission', '401'

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
    found_article.author = found_article_change.author

    session.delete(found_article_change)
    session.commit()

    return ArticleSchema().dump(found_article), '200'


@main.route('/articleChanges/<change_id>', methods=['DELETE'])
@auth.login_required
def delete_article_change(change_id):
    found_article_change = session.query(ArticleChange).filter(ArticleChange.id == change_id).one_or_none()

    if found_article_change is None:
        return 'ArticleChange not found', '404'

    if not auth.current_user().is_moderator and found_article_change.author != auth.current_user():
        return 'You don\'t have permission to delete this article', '401'

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
