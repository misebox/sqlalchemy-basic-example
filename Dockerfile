# syntax = docker/dockerfile:1.2
FROM python:3.9

WORKDIR /app 
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY main.py ./

CMD ["python", "main.py"]

