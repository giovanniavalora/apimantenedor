# pull official base image
FROM python:3.8.2-alpine

# set work directory
WORKDIR /usr/src/apimantenedor

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install Timezones for alpine
RUN apk add tzdata
RUN cp /usr/share/zoneinfo/America/Santiago /etc/localtime
RUN echo "America/Santiago" > /etc/timezone
# RUN apk del tzdata

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add libffi-dev
# Por si no es suficiente libffi para azure-storage-blob, instalar:
# RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev openssl-dev

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
