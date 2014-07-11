#!/usr/bin/env python
import docker
import ConfigParser
import json

from flask import render_template
from flask import Flask

app = Flask(__name__)
config = ConfigParser.ConfigParser()
config.read('config/sample.cfg')
host_entries = config.get('main','hosts').split(",")

class Host(object):
    def __init__(self, location):
        self.location = location
        if "tcp" == location.split(":")[0]:
            self.name = location[6:].split(":")[0]
        else:
            self.name = "Localhost"

hosts={}
for host in host_entries:
    newhost = Host(host)
    hosts[newhost.name] = newhost

@app.route("/old")
def oldindex():
    template_data = {"hosts":[]}
    template_data['containers'] = {}
    for host in hosts.values():
        template_data['hosts'].append(host.name)
        conn = docker.Client(base_url=host.location,
                            version='1.12',
                            timeout=10)
        template_data['containers'][host.name] = [x for x in conn.containers()]
    return render_template("index.html.old", **template_data)

@app.route("/")
def index():
    #template_data = {"hosts":[]}
    #template_data['containers'] = {}
    #for host in hosts.values():
        #template_data['hosts'].append(host.name)
        #conn = docker.Client(base_url=host.location,
                            #version='1.12',
                            #timeout=10)
        #template_data['containers'][host.name] = [x for x in conn.containers()]
    #return render_template("index.html", **template_data)
    return render_template("index.html")

@app.route("/hosts")
def get_hosts():
    return json.dumps(hosts.keys())

@app.route("/hosts/<hostname>")
def get_host_detail(hostname):
    host = hosts[hostname]
    conn = docker.Client(base_url=host.location,
                            version='1.12',
                            timeout=10)
    containers = [x for x in conn.containers()]
    return json.dumps(containers)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
