from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean, Text, ARRAY
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgres://postgres:nastya@localhost:5432/postgres')
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
# Base.metadata.create_all(engine)
#
# author_article = Table("author_articles",
#                       Base.metadata,
#                       Column("author_id", Integer(), ForeignKey("users.id"), primary_key=True),
#                       Column("article_id", Integer(), ForeignKey("articles.id"), primary_key=True))
# list_change_articles = Table("list_of_article_changes",
#                       Base.metadata,
#                       Column("article_id", Integer(), ForeignKey("articles.id"), primary_key=True),
#                       Column("articlechanges_id", Integer(), ForeignKey("articlechanges.id"), primary_key=True))
# articles = relationship(Article, secondary=author_article, lazy="subquery", backref=backref("playlists", lazy=True))

# users=relationship(User, secondary=author_article, lazy="subquery", backref=backref("articles", lazy=True))

class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    name = Column(String)
    surname = Column(String)
    email = Column(String)
    password = Column(String)
    is_moderator = Column(Boolean)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    text = Column(Text)
    author_id = Column(ForeignKey(User.id))
    author = relationship(User, backref="articles", lazy=False)


class ArticleChange(Base):
    __tablename__ = "article_changes"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    text = Column(String)
    author_id = Column(ForeignKey(User.id))
    author = relationship(User, backref="article_changes", lazy=False)
    article_id = Column(ForeignKey(Article.id))
    article = relationship(Article, backref="article_changes", lazy=False)

