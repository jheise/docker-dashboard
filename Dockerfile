FROM ubuntu:14.04

RUN apt-get update && apt-get install -y python-flask python-pip
RUN pip install docker-py
COPY docker-dashboard /docker-dashboard
EXPOSE 4000
CMD cd docker-dashboard && ./dashboard.py
