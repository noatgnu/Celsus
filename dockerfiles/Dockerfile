FROM python:3.9
LABEL maintainer="tphung001@dundee.ac.uk"

LABEL \
      org.label-schema.name="Celsus" \
      org.label-schema.description="Docker container for Celsus" \
      org.label-schema.version="$DOCKER_IMAGE_VERSION" \
      org.label-schema.vcs-url="https://github.com/noatgnu/Celsus" \
      org.label-schema.schema-version="1.0"

EXPOSE 8000

RUN mkdir /app
RUN mkdir /app/src
RUN mkdir /app/data

WORKDIR /app/src

RUN apt-get update
RUN apt-get upgrade -y


RUN git clone https://github.com/noatgnu/Celsus.git

WORKDIR /app/src/Celsus

RUN pip install --no-cache-dir -r requirements.txt
RUN sed -i -r "s|localhost|database|" /app/src/Celsus/alembic.ini

VOLUME ["/app/data"]

CMD ["alembic", "upgrade", "head"]

