# SQLAlchemy basic example

SQLAlchemy example code about basic usage with PostgreSQL

## run with docker

```
# build (required after editing main.py)
COMPOSE_DOCKER_CLI_BUILD=1 docker-compose build
docker-compose run py

# clean up (down db container)
docker-compose down
```

## run with venv (using SQLite in-memory DB)
```
# setup virtualenv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run
python main.py

# clean up
deactivate
```

## result

```

# Select from single table
SQL:  SELECT category.id, category.name 
FROM category ORDER BY category.id
Category(id=1, name=diary)
Category(id=2, name=poem)
Category(id=3, name=tech)

# join One-to-Many tables
SQL:  SELECT article.id, article.category_id, article.title, article.body, category.id AS id_1, category.name 
FROM category JOIN article ON category.id = article.category_id ORDER BY article.id
Article(id=1, category_id=3, title=SQLAlchemy Syntax) Category(id=3, name=tech)
Article(id=2, category_id=1, title=Day 1) Category(id=1, name=diary)
Article(id=3, category_id=1, title=Day 2) Category(id=1, name=diary)

# join Many-to-Many tables
SQL:  SELECT article.id, article.category_id, article.title, article.body, tag.id AS id_1, tag.name 
FROM article JOIN article_tag_map AS article_tag_map_1 ON article.id = article_tag_map_1.article_id JOIN tag ON tag.id = article_tag_map_1.tag_id ORDER BY article.id

## result rows
Article(id=1, category_id=3, title=SQLAlchemy Syntax) Tag(id=3, name=database)
Article(id=1, category_id=3, title=SQLAlchemy Syntax) Tag(id=2, name=python)
Article(id=2, category_id=1, title=Day 1) Tag(id=1, name=private)
Article(id=3, category_id=1, title=Day 2) Tag(id=1, name=private)

## structured output
Article(id=1, title=SQLAlchemy Syntax, category_id=3)
    Tag(id=3, name=database)
    Tag(id=2, name=python)
Article(id=2, title=Day 1, category_id=1)
    Tag(id=1, name=private)
Article(id=3, title=Day 2, category_id=1)
    Tag(id=1, name=private)

```

