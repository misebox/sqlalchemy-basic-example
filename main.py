import os
import json

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String


class _base:
    def to_dict(self):
        d = dict(self.__dict__)
        d.pop('_sa_instance_state', None)
        return d

Base = declarative_base(cls=_base)


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

    print('\n# Select from single table')
    stmt = select(Category)\
            .order_by(Category.id)
    print('SQL: ',stmt.compile())
    rows = ss.execute(stmt).all()

    categories = []
    for row in rows:
        (cat,) = row
        print(cat)
        categories.append(cat.to_dict())

    # Insert into Articles
    articles = [
        Article(title='SQLAlchemy Syntax', category_id=cat_tech.id, body='select(Article)'),
        Article(title='Day 1', category_id=cat_diary.id, body='stayed home all day'),
        Article(title='Day 2', category_id=cat_diary.id, body='went to a cafe'),
        Article(title='untitled draft', category_id=cat_diary.id, body='...'),
    ]
    ss.add_all(articles)
    ss.commit()

    print('\n# join One-to-Many tables')
    stmt = select(Article, Category)\
            .join(Article)\
            .order_by(Article.id)
    print('SQL: ',stmt.compile())
    rows = ss.execute(stmt).all()
    for art, cat in rows:
        print(art, '|', cat)

    # Insert into Tags
    tag_prv = Tag(name='private')
    tag_py = Tag(name='python')
    tag_db = Tag(name='database')
    tags = [tag_prv, tag_py, tag_db]
    ss.add_all(tags)
    ss.commit()
    # associate articles and tags(insert into article_tag_map)
    articles[0].tags.append(tag_db)
    articles[0].tags.append(tag_py)
    articles[1].tags.append(tag_prv)
    articles[2].tags.append(tag_prv)
    ss.commit()

    print('\n# join Many-to-Many tables')
    stmt = select(Article, Tag)\
            .outerjoin(Article.tags)\
            .order_by(Article.id)
            # use  `.join(Article.tags)`  to inner join
    print('SQL: ',stmt.compile())
    rows = ss.execute(stmt).all()

    for art, tag in rows:
        print(art, '|', tag)

    print('\n# join Many-to-Many tables and eagerload')
    stmt = select(Article)\
            .options(
                # To avoid n+1 query when accessing Article.tags
                joinedload(Article.tags)
            )\
            .order_by(Article.id)
    print('SQL: ',stmt.compile())
    rows = ss.execute(stmt).unique().all()

    for (art,) in rows:
        print(f'{art}')
        # n+1 query is not issued
        tags = []
        for tag in art.tags:
            print(f'   {tag}')

    print('\n# output as dict')
    articles = []
    for (art,) in rows:
        tags = []
        for tag in art.tags:
            tags.append(tag.to_dict())
        art_dict = art.to_dict()
        art_dict['tags'] = tags
        articles.append(art_dict)

        print(art_dict)

    print('\n# output as JSON')

    data = dict(
        categories=categories,
        articles=articles,
    )
    print(json.dumps(data, indent=2))
