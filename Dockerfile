FROM python:2.7-jessie

COPY . /app

WORKDIR /app

CMD ["/bin/bash"]

RUN python setup.py install \
    && python setup.py test