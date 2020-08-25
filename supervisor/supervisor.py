#!/usr/bin/env python3
import os
import json
import time
import pathlib
import asyncio
import time
import docker
from docker.models.containers import Container
from os.path import join
from aiohttp import web
import connexion
from connexion.resolver import RestyResolver
from dataclasses import dataclass
from service import Service
from utils.updater import Updater
from utils.singletondecorator import singleton
from subprocess import Popen, run

is_docker = True
current_path = pathlib.Path(__file__).parent.absolute()
ROOT = "/supervisor"
config_folder = join(current_path, ".config")
static_path = "/supervisor/static"

if not os.path.exists(config_folder):
    is_docker = False
    ROOT = current_path
    config_folder = join(current_path.parent.absolute(), "config")
    static_path = str(ROOT) + "/static"

@singleton
class Supervisor:
    """
        Main supervisor
        Reponsible for creating, stoping, and managing the docker containers
    """
    services: dict = {}
    last_versions_fetch: int = 0
    ttyd_session = None
    # updater: Updater = Updater()

    def __init__(self) -> None:
        with open(join(config_folder, "dockers.json")) as config_file:
            for service, config in json.load(config_file)["dockers"].items():
                # don't create supervisor service if running non-dockerized
                if not is_docker and service == "supervisor":
                    continue
                self.services[service] = Service(config)
        print(f"Found {len(self.services.keys())} Services:")
        for service in self.services.keys():
            print(service)

        asyncio.create_task(self.do_maintenance())

    async def enable(self, name: str) -> web.Response:
        """Enables a Docker container

        Args:
            name (str): Docker container to enable

        Returns:
            web.Response: 200 ("ok"), 404 if invalid name, 500 for internal error
        """
        if name is None or name not in self.services:
            return web.Response(status=404, text=f"Invalid image: {name}")
        self.services[name].enable()
        self.update_settings()
        return web.Response(status=200, text="ok")

    async def disable(self, name: str) -> web.Response:
        """Disables a Docker container

        Args:
            name (str): Docker container to disable

        Returns:
            web.Response: 200 ("ok"), 404 if invalid name, 500 for internal error
        """
        if name is None or name not in self.services:
            return web.Response(status=404, text=f"Invalid image: {name}")
        self.services[name].disable()
        self.update_settings()
        return web.Response(status=200, text="ok")

    async def attach(self, name: str) -> web.Response:
        """Starts a tty session attached to container "name"

        Args:
            name (str): Docker container to attach to

        Returns:
            web.Response: 200 ("ok"), 404 if invalid name, 500 for internal error
        """
        if name is None or name not in self.services:
            return web.Response(status=404, text=f"Invalid image: {name}")
        if self.ttyd_session is not None:
            self.ttyd_session.terminate()
            self.ttyd_session.wait()
            time.sleep(0.5)

        container_id = self.services[name].container.id
        print(container_id)
        self.ttyd_session = Popen(['/usr/bin/ttyd', '-p', '8082', '/usr/bin/docker', 'exec', '-it' , container_id,  '/usr/bin/tmux'])
        return web.Response(status=200, text="ok")

    async def setversion(self, name: str, version: str) -> web.Response:
        """Sets the version of a service

        Args:
            name (str): Service name as in the docker.json file
            version (str): the new version(tag) to use

        Returns:
            web.Response: 200 for success, 404 for invalid image
        """
        if name is None or name not in self.services:
            return web.Response(status=404, text=f"Invalid image: {name}")
        self.services[name].set_version(version)
        return web.Response(status=200, text="ok")

    async def top(self, name: str) -> web.Response:
        """Returns the running processes in the container

        Args:
            name (str): Name of the running container

        Returns:
            dict: described in https://docs.docker.com/engine/api/v1.24/#list-processes-running-inside-a-container
        """
        service = self.services.get(name, None)
        if service is None:
            return web.Response(status=404, text=f"Invalid image: {name}")
        return web.json_response(service.get_top())

    async def restart(self, name: str) -> web.Response:
        """ Restarts a docker container

        Args:
            name (str): name of the container to restart
        """
        service = self.services.get(name, None)
        if service is None:
            return web.Response(status=404, text=f"Invalid image: {name}")
        return web.json_response(service.restart())

    def update_settings(self) -> None:
        """Writes current settings to dockers.json
        """
        # TODO: implement this

    async def do_maintenance(self) -> None:
        """Periodically checks all running containers, starting and stopping
        them as necessary
        """
        while True:
            print("Doing maintenance...", id(self))
            try:
                for service_name, service in self.services.items():
                    service.update()
                    # Disables service if it fails too much
                    if service.starts > 10 and service.enabled:
                        print(
                            "service {service_name} failed to start 10 times, disabling it for sanity reasons...")
                        await self.disable(service_name)

            except Exception as error:
                print(f"error in do_maintenance: {error}")
            # self.updater.fetch_available_versions()
            await asyncio.sleep(1)

    async def get_status(self) -> web.Response:
        """Gets the status of all services

        Returns:
            web.Response: json status
        TODO: describe this json in yaml
        """
        status = {}
        for service_name, service in self.services.items():
            status[service_name] = service.get_status()
        return web.json_response(status)

    async def get_logs(self, name: str) -> web.Response:
        """Gets logs of a service

        Args:
            name (str): service name

        Returns:
            web.Response: Html response with the logs as pure text
        """
        if name not in self.services:
            return web.Response(status=404, text=f"Invalid image: {name}")
        return web.Response(status=200, text=self.services[name].get_logs())

# API methods


async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(str(ROOT) + '/index.html')

# These transparently forward the resquests to the Supervisor instance


async def status() -> web.Response:
    return await Supervisor().get_status()


async def enable(name: str) -> web.Response:
    return await Supervisor().enable(name)


async def disable(name: str) -> web.Response:
    return await Supervisor().disable(name)

async def attach(name: str) -> web.Response:
    return await Supervisor().attach(name)


async def top(name: str) -> web.Response:
    return await Supervisor().top(name)


async def restart(name: str) -> web.Response:
    return await Supervisor().restart(name)


async def log(name: str) -> web.Response:
    return await Supervisor().get_logs(name)


async def setversion(name: str, request: web.Request) -> web.Response:
    data = await request.post()
    version = (await request.json())["version"]
    return await Supervisor().setversion(name, version)

if __name__ == "__main__":
    app = connexion.AioHttpApp(__name__, specification_dir='openapi/')
    app.add_api(
        'supervisor.yaml',
        arguments={
            'title': 'Companion Supervisor'},
        pass_context_arg_name='request')
    app.app.router.add_static('/static/', path=str(static_path))
    app.app.router.add_route('GET', "/", index)
    app.run(port=8081)
