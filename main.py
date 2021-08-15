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

    print('\n# Select from single table')
    stmt = select(Category)\
            .order_by(Category.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    for row in res.fetchall():
        (cat,) = row
        print(str(cat))

    # Insert into Articles
    articles = [
        Article(title='SQLAlchemy Syntax', category_id=cat_tech.id),
        Article(title='Day 1', category_id=cat_diary.id),
        Article(title='Day 2', category_id=cat_diary.id),
    ]
    ss.add_all(articles)
    ss.commit()

    print('\n# join One-to-Many tables')
    stmt = select(Article, Category)\
            .join(Article)\
            .order_by(Article.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    for art, cat in res.fetchall():
        print(str(art), str(cat))

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
            .join(Article.tags)\
            .order_by(Article.id)
    print('SQL: ',stmt.compile())
    res = ss.execute(stmt)
    ss.flush()

    def to_dict(o):
        d = o.__dict__
        d.pop('_sa_instance_state', None)
        return d

    art_map = {}
    print('\n## result rows')
    for art, tag in res.fetchall():
        print(str(art), str(tag))

        art_dict = art_map.get(art.id) or to_dict(art)
        art_dict['tags'] = art_dict.get('tags', [])
        art_dict['tags'].append(to_dict(tag))
        art_map[art.id] = art_dict

    print('\n## structured output')
    for _, art in art_map.items():
        print('Article(id={id}, title={title}, category_id={category_id})'.format(**art))
        for tag in art['tags']:
            print('    Tag(id={id}, name={name})'.format(**tag))


