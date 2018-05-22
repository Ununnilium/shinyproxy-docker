#!/usr/bin/env python3
"""Script to start Shiny Proxy in a Docker container."""

# Copyright 2018 Fabian Heller
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby
# granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR # CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.


import os
import signal
import subprocess
import sys
import time

import docker
import yaml

__author__ = "Fabian Heller"
__copyright__ = "Copyright 2018, Fabian Heller"
__license__ = "ISC"


# Edit configuration here
docker_pull_images = True  # if True, app images are pulled from Docker Hub or a private registry at start
shinyproxy_image = 'shinyproxy'  # image in which Shiny proxy runs itself
docker_network = 'shinyproxy'  # name of the network which is used to communicate with the app containers
registry_url = None  # e.g. 'https://my_registry.com/v2/' or None if Docker Hub is used
registry_username = None  # only needed if authentication necessary
registry_password = None


docker_unix_socket = '/var/run/docker.sock'
docker_url= 'unix:/' + docker_unix_socket
app_images = []


def eprint(*args, **kwargs):
    """Prints to STDERR."""
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()


def signal_handler(signal, frame):
    """Trap SIGINT and remove created Docker containers and network."""
    eprint("Cleaning up …")
    client = docker.DockerClient(base_url=docker_url)
    for image in app_images:
        for app_container in client.containers.list(all=True, filters={'ancestor': image}):
            app_container.remove(v=True, force=True)
    shiny_network = client.networks.get(docker_network)
    for shiny_container in client.containers.list(all=True, filters={'ancestor': shinyproxy_image}):
        shiny_network.disconnect(shiny_container)
    shiny_network.remove()
    sys.exit(0)


if __name__ == "__main__":
    eprint("Make Docker available on port 2375 …")
    subprocess.Popen(["socat", "TCP-LISTEN:2375,reuseaddr,fork,bind=127.0.0.1", "UNIX-CONNECT:" + docker_unix_socket])

    # Get names of Docker app images
    with open("application.yml", 'r') as f:
        config = yaml.load(f)
        for app in config["shiny"]["apps"]:
            if app["docker-image"] not in app_images:
                app_images.append(app["docker-image"])

    # Pull all necessary docker images
    client = docker.DockerClient(base_url=docker_url)
    if registry_username and registry_password and registry_url:
        eprint("Login into registry …")
        client.login(username=registry_username, password=registry_password, registry=registry_url)
    if docker_pull_images:
        eprint("Pulling Docker images …")
        for image in app_images:
            client.images.pull(image)

    # Clean up before exiting
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    try:
        network = client.networks.create(docker_network, driver="bridge", check_duplicate=True)
    except docker.errors.APIError:
        network = client.networks.get(docker_network)

    eprint("Connecting shiny proxy container(s) to app network …")
    for container in client.containers.list(all=True, filters={'ancestor': shinyproxy_image}):
        network.connect(container)

    # Create a fork to listen if a Shiny proxy app container is created
    pid = os.fork()
    if pid == 0:
        events = client.events(decode=True)
        for event in events:
            if 'status' in event and event["status"] == "create" and "from" in event and event["from"] in app_images:
                new_container = client.containers.get(event["id"])
                eprint("Connecting newly created app container to network …")
                network.connect(new_container)
        os._exit(0)

    # Start application and automatic restart in case of crash
    while True:
        eprint("Starting ShinyProxy …")
        subprocess.call(['java', '-jar', 'shinyproxy.jar'])
        time.sleep(20)
