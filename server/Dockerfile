FROM python:3.10

WORKDIR /src
COPY . ./

RUN apt-get update
RUN apt-get install -y --no-install-recommends default-jre default-jdk
RUN pip install -r requirements.txt

EXPOSE 8000