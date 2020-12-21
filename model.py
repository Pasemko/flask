from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean, Text, ARRAY
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:admin@localhost:5432/postgres')
Session = sessionmaker(bind=engine)
db_session = scoped_session(Session)

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

    articles = relationship('Article', back_populates='author', cascade="all, delete", passive_deletes=True)
    changed_articles = relationship('ArticleChange', back_populates='author', cascade="all, delete", passive_deletes=True)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    text = Column(Text)
    author_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    author = relationship('User', back_populates='articles', lazy=False)
    changes = relationship('ArticleChange', back_populates='article', cascade="all, delete", passive_deletes=True)


class ArticleChange(Base):
    __tablename__ = "article_changes"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    text = Column(String)
    author_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    author = relationship('User', back_populates='changed_articles', lazy=False)
    article_id = Column(Integer, ForeignKey(Article.id, ondelete="CASCADE"))
    article = relationship(Article, back_populates='changes', lazy=False)

