FROM python:3.5

RUN mkdir /bookstore

WORKDIR /bookstore

COPY requirements.txt /bookstore/requirements.txt

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . /bookstore

CMD ["uwsgi", "uwsgi.ini"]