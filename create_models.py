from model import db_session, User, Article, ArticleChange

session = db_session()

user_1 = User(id=1, username="Test1", email="test@test.com", name="TestName", surname="TestSurname", password="testpass1", is_moderator=False)
user_2 = User(id=2, username="Test2", email="test2@test.com", name="TestName2", surname="TestSurname2", password="testpass2", is_moderator=False)
user_3 = User(id=3, username="Test3", email="test3@test.com", name="TestName3", surname="TestSurname3", password="testpass3", is_moderator=False)


article_1 = Article(id=1, title="1st title", text="First text", author=user_1)
article_2 = Article(id=2, title="2nd title", text="Second text", author=user_3)
article_3 = Article(id=3, title="3rd title", text="Third text", author=user_2)


articlechange_1 = ArticleChange(id=1, title="1st change title", text="First change text", author=user_1, article=article_2)
articlechange_2 = ArticleChange(id=2, title="1st change title", text="Second change text", author=user_3, article=article_1)

session.add(user_1)
session.add(user_2)
session.add(user_3)


session.add(article_1)
session.add(article_2)
session.add(article_3)

session.add(articlechange_1)
session.add(articlechange_2)

session.commit()

print(session.query(User).all())
print(session.query(Article).all())
print(session.query(ArticleChange).all())
