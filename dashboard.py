#!/usr/bin/env python
import docker
import ConfigParser
import json

from flask import render_template
from flask import Flask
from flask import request
from flask import Response

from functools import wraps

app = Flask(__name__,static_url_path='')
config = ConfigParser.ConfigParser()
config.read('config/sample.cfg')



def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

class Host(object):
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.conn = docker.Client(base_url=self.location,
                            version='1.12',
                            timeout=10)

hosts={}
for name,location in config.items('main'):
    newhost = Host(name, location)
    hosts[name] = newhost

@app.route("/old")
def oldindex():
    template_data = {"hosts":[]}
    template_data['containers'] = {}
    for host in hosts.values():
        template_data['hosts'].append(host.name)
        template_data['containers'][host.name] = [x for x in host.conn.containers()]
    return render_template("index.html.old", **template_data)

@app.route("/new")
@requires_auth
def newindex():
    template_data = {"hosts":[]}
    template_data['containers'] = {}
    for host in hosts.values():
        template_data['hosts'].append(host.name)
        template_data['containers'][host.name] = [x for x in host.conn.containers(all=True)]
    return render_template("index.html.new", **template_data)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/hosts")
@requires_auth
def get_hosts():
    return json.dumps(hosts.keys())

@app.route("/hosts/<hostname>")
@requires_auth
def get_host_detail(hostname):
    host = hosts[hostname]
    containers = [x for x in host.conn.containers(all=True)]
    return json.dumps(containers)

@app.route("/hosts/<hostname>/containers")
@requires_auth
def get_host_containers(hostname):
    host = hosts[hostname]
    containers = [x for x in host.conn.containers(all=True)]
    return json.dumps(containers)

@app.route("/hosts/<hostname>/containers/<container>", methods=["POST"])
@requires_auth
def container_actions(hostname,container):
    action = request.form["action"]
    response = {"result":"failure","reason":"Action {0} unsupported".format(action)}
    if action in ["start","stop"]:
        response = container_start_stop(hostname, container, action)

    return json.dumps(response)

#start and stop actions
def container_start_stop(hostname, container, action):
    try:
        host = hosts[hostname]
        if action == "start":
            host.conn.start(container)
        else:
            host.conn.stop(container,timeout=10)
        return { "result":"success"}
    except Exception as e:
        return { "result":"failure","reason":str(e) }



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
