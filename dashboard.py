#!/usr/bin/env python
import docker

from flask import render_template
from flask import Flask

app = Flask(__name__)

hosts = ["localhost:4242","glados:4242"]

@app.route("/")
def index():
    template_data = {"hosts":hosts}
    template_data['containers'] = {}
    for host in hosts:
        conn = docker.Client(base_url="tcp://{0}".format(host),
                            version='1.12',
                            timeout=10)
        template_data['containers'][host] = [x for x in conn.containers()]
    return render_template("index.html", **template_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
