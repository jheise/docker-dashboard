#!/usr/bin/env python
"""Flask based dashboard to monitor multiple docker instances"""

import docker
import ConfigParser
import json
import logging

from flask import render_template
from flask import Flask
from flask import request
from flask import Response
from flask_sockets import Sockets

from functools import wraps

import gevent
from geventwebsocket.websocket import WebSocketError

# setup flask app, make sure static content loads easily
app = Flask(__name__, static_url_path='')
sockets = Sockets(app)

#grab the config
config = ConfigParser.ConfigParser()
config.read('/config/dashboard.cfg')

address = config.get('main', 'host')
port = config.get('main', 'port')
admin_name = config.get('main', 'admin_name')
admin_password = config.get('main', 'password')
update_url = config.get('main', 'update_socket')


class Host(object):
    """Object to represent hosts and hold connections"""

    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.conn = docker.Client(base_url=self.location,
                                  version='1.12',
                                  timeout=10)


hosts = {}
for hostname, server_location in config.items('hosts'):
    try:
        new_host = Host(hostname, server_location)
        hosts[hostname] = new_host
    except ConnectionError as e:
        app.logger.error(e)


class UpdateBackend(object):
    """sub process to handle polling updates and sending them to clients"""

    def __init__(self):
        self.clients = []

    def register(self, client):
        """register client connection"""
        app.logger.info("Registering client {0}".format(client))
        self.clients.append(client)
        app.logger.info("registering {0}".format(client))
        self.send(client, {"message_type":"init",
                           "body":"First Message"})

    def send(self, client, data):
        """send data to client"""
        try:
            client.send(data)
        except WebSocketError:
            self.clients.remove(client)

    def run(self):
        """run websocket server"""
        while True:
            for client in self.clients:
                app.logger.info("sending update")
                for host in hosts.values():
                    containers = [x for x in host.conn.containers(all=True)]
                    gevent.spawn(self.send, client, json.dumps(
                        {"message_type": "update",
                         "host": host.name,
                         "containers": containers}))
            gevent.sleep(15)

    def start(self):
        """spawn process"""
        gevent.spawn(self.run)

#create an UpdateBackend and start it
updater = UpdateBackend()
updater.start()

@app.before_first_request
def setup_logging():
    """setup logging so we can actually see whats happening"""
    if not app.debug:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == admin_name and password == admin_password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    """decorator for authenication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route("/")
@requires_auth
def index():
    """assemble basic layout and serve page"""
    app.logger.info("Loading page")
    template_data = {"hosts": {}, "update_url": update_url}
    for host in hosts.values():
        host_data = []
        try:
            for container in [ x for x in  host.conn.containers(all=True)]:
                name = container["Names"][0][1:]
                container_data = {"name":name}
                container_data["data"] = container
                container_data["details"] = host.conn.inspect_container(name)
                host_data.append(container_data)
        except Exception as e:
            app.logger.error(e)
        template_data["hosts"][host.name] = host_data

    return render_template("index.html", **template_data)


@app.route("/hosts")
@requires_auth
def get_hosts():
    """return a list of hosts"""
    return json.dumps(hosts.keys())


@app.route("/hosts/<target>")
@requires_auth
def get_host_detail(target):
    """return details for the given host"""
    host = hosts[target]
    containers = [x for x in host.conn.containers(all=True)]
    return json.dumps(containers)


@app.route("/hosts/<target>/containers")
@requires_auth
def get_host_containers(target):
    """get all containers for the target host"""
    host = hosts[target]
    containers = [x for x in host.conn.containers(all=True)]
    return json.dumps(containers)


@app.route("/hosts/<target>/containers/<container>", methods=["POST"])
@requires_auth
def container_actions(target, container):
    """stop or start given container on given host"""
    action = request.form["action"]
    response = {"result": "failure",
                "reason": "Action {0} unsupported".format(action)}
    app.logger.info("{0} on {1}/{2}".format(action, target, container))
    if action in ["start", "stop"]:
        response = container_start_stop(target, container, action)

    return json.dumps(response)


@app.route("/massaction", methods=["POST"])
@requires_auth
def mass_action():
    """perfom action against all given hosts"""
    action = request.form["action"]
    data = json.loads(request.form["instances"])
    for target, instances in data.items():
        for instance in instances:
            container_start_stop(target, instance, action)
    response = {"result": "failure",
                "reason": "Action {0} unsupported".format(action)}

    return json.dumps(response)


#websocket stuff
@sockets.route("/updates")
def updates(ws):
    """add client connection to backend"""
    app.logger.info("registering websocket {0}".format(ws))
    updater.register(ws)

    while not ws.closed:
        gevent.sleep()


#start and stop actions
def container_start_stop(target, container, action):
    """actually perform start stop"""
    try:
        host = hosts[target]
        if action == "start":
            host.conn.start(container)
        else:
            host.conn.stop(container, timeout=10)
        return {"result": "success"}
    except Exception as e:
        return {"result": "failure", "reason": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
