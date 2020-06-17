FROM python:3.8

WORKDIR /opt/app

RUN pip install -U pip && \
    pip install uwsgi

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uwsgi", "--ini", "/opt/app/uwsgi.ini"]