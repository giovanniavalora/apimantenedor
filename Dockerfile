# pull official base image
FROM python:3.7.6-alpine

# set work directory
WORKDIR /usr/src/apimantenedor

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN python3 -m pip install --upgrade pip
COPY ./requirements.txt /usr/src/apimantenedor/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/apimantenedor/entrypoint.sh

# copy project
COPY . /usr/src/apimantenedor/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/apimantenedor/entrypoint.sh"]
