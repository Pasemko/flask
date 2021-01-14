from model import Session, User, Article, ArticleChange
from main import bcrypt

# psql -h localhost -d postgres -U postgres -p 5432 -a -q -f create_tables.sql
def fillDB():
    session = Session()

    user_1 = User(id=4,
                  username="Test1",
                  email="test@test.com",
                  name="TestName",
                  surname="TestSurname",
                  password=bcrypt.generate_password_hash('admin').decode('utf-8'),
                  is_moderator=False)

    user_2 = User(id=2,
                  username="Test2",
                  email="test2@test.com",
                  name="TestName2",
                  surname="TestSurname2",
                  password=bcrypt.generate_password_hash('admin').decode('utf-8'),
                  is_moderator=False)

    user_3 = User(id=3,
                  username="Test3",
                  email="test3@test.com",
                  name="TestName3",
                  surname="TestSurname3",
                  password=bcrypt.generate_password_hash('admin').decode('utf-8'),
                  is_moderator=True)

    article_1 = Article(id=1, title="1st title", text="First text", author=user_1)
    article_2 = Article(id=2, title="2nd title", text="Second text", author=user_2)
    article_3 = Article(id=3, title="3rd title", text="Third text", author=user_3)

    articlechange_1 = ArticleChange(id=1, title="1st change title", text="First change text", author=user_1,
                                    article=article_1)
    articlechange_2 = ArticleChange(id=2, title="1st change title", text="Second change text", author=user_2,
                                    article=article_2)

    session.add(user_1)
    session.add(user_2)
    session.add(user_3)

    session.add(article_1)
    session.add(article_2)
    session.add(article_3)

    session.add(articlechange_1)
    session.add(articlechange_2)

    session.commit()

fillDB()