FROM python:3.9

USER root

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["sh", "entry.sh"]
