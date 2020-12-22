from marshmallow import Schema, fields, post_load
from model import User, Article, ArticleChange


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    name = fields.Str()
    surname = fields.Str()
    email = fields.Str()
    password = fields.Str()
    is_moderator = fields.Bool(default=False)

    @post_load
    def create_user(self, data, **kwargs):
        return User(**data)


class ArticleSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    text = fields.Str()
    author_id = fields.Int()

    @post_load
    def create_article(self, data, **kwargs):
        return Article(**data)


class ArticleChangeSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    text = fields.Str()
    author_id = fields.Int()
    article_id = fields.Int()

    @post_load
    def create_article_change(self, data, **kwargs):
        return ArticleChange(**data)
