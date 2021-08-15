import os
import enum
import uuid

from sqlalchemy.orm import registry
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Sequence
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr


Base = declarative_base()


# get DSN from environment variable
DB_DSN = os.environ.get('DB_DSN')

ECHO_LOG = True
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
    cat_poem = Category(name='poem')
    cat_tech = Category(name='tech')
    cat_diary = Category(name='diary')
    ss.add_all([cat_diary, cat_poem, cat_tech])
    ss.commit()
    articles = [
        Article(title='SQLAlchemy Syntax', category_id=cat_tech.id),
        Article(title='Day 1', category_id=cat_diary.id),
        Article(title='Day 2', category_id=cat_diary.id),
    ]
    ss.add_all(articles)
    ss.commit()

    # one to many
    stmt = select(Category, Article)\
            .join(Article)
    res = ss.execute(stmt)
    for cat, art in res.fetchall():
        print(str(cat), str(art))

    t_prv = Tag(name='private')
    t_py = Tag(name='python')
    t_db = Tag(name='database')
    tags = [t_prv, t_py, t_db]
    ss.add_all(tags)
    ss.commit()
    articles[0].tags.append(t_db)
    articles[0].tags.append(t_py)
    articles[1].tags.append(t_prv)
    articles[2].tags.append(t_prv)
    ss.commit()
    

    # many to many
    stmt = select(Tag, Category, Article)\
            .join(Tag.articles)\
            .join(Category)
    res = ss.execute(stmt)
    for tag, cat, art in res.fetchall():
        print(str(tag), str(cat), str(art))

