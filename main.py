import os

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


Base = declarative_base()


# get DSN from environment variable
DB_DSN = os.environ.get('DB_DSN') or 'sqlite://' # If not set, SQLite inmemory DB is used

ECHO_LOG = False
engine = create_engine(DB_DSN, echo=ECHO_LOG)
session = sessionmaker(engine)


"""
Models
"""
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)

    def __str__(self):
        return f'Category(id={self.id}, name={self.name})'


article_tag_map = Table('article_tag_map', Base.metadata,
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
    Column('article_id', ForeignKey('article.id'), primary_key=True)
)


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    title = Column(String, index=True)
    body = Column(String)
    tags = relationship('Tag', secondary=article_tag_map, back_populates="articles")

    def __str__(self):
        return f'Article(id={self.id}, category_id={self.category_id}, title={self.title})'


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, index=True)
    articles = relationship("Article", secondary=article_tag_map, back_populates="tags")

    def __str__(self):
        return f'Tag(id={self.id}, name={self.name})'


# reset DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


with session() as ss:
    # Insert Categories
    cat_poem = Category(name='poem')
    cat_tech = Category(name='tech')
    cat_diary = Category(name='diary')
    ss.add_all([cat_diary, cat_poem, cat_tech])
    ss.commit()

    print()
    print('# Select from single table')
    stmt = select(Category)\
            .order_by(Category.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    for row in res.fetchall():
        (cat,) = row
        print(str(cat))
    print()

    # Insert into Articles
    articles = [
        Article(title='SQLAlchemy Syntax', category_id=cat_tech.id),
        Article(title='Day 1', category_id=cat_diary.id),
        Article(title='Day 2', category_id=cat_diary.id),
    ]
    ss.add_all(articles)
    ss.commit()

    print('# One to Many')
    stmt = select(Category, Article)\
            .join(Article)\
            .order_by(Article.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    for cat, art in res.fetchall():
        print(str(cat), str(art))
    print()

    # Insert into Tags
    t_prv = Tag(name='private')
    t_py = Tag(name='python')
    t_db = Tag(name='database')
    tags = [t_prv, t_py, t_db]
    ss.add_all(tags)
    ss.commit()
    # associate articles and tags(insert into article_tag_map)
    articles[0].tags.append(t_db)
    articles[0].tags.append(t_py)
    articles[1].tags.append(t_prv)
    articles[2].tags.append(t_prv)
    ss.commit()

    print('# Many to Many')
    stmt = select(Tag, Category, Article)\
            .join(Tag.articles)\
            .join(Category)\
            .order_by(Tag.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    for tag, cat, art in res.fetchall():
        print(str(tag), str(cat), str(art))

    print()


