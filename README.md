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
