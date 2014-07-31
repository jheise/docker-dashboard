FROM ubuntu:14.04

RUN apt-get update && apt-get install -y python-flask python-pip python-dev
RUN pip install docker-py
RUN pip install flask_sockets
RUN pip install gunicorn
COPY src /docker-dashboard
EXPOSE 4000
CMD cd docker-dashboard && gunicorn -b 0.0.0.0:4000 -k flask_sockets.worker dashboard:app
