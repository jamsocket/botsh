import os

import docker
from docker.types import Mount
from termcolor import colored
import hashlib


class DockerContainer:
    current_directory: str

    def __init__(self, image, wipe: bool):
        self.current_directory = os.getcwd()
        dir_hash = hashlib.sha256(self.current_directory.encode("utf-8")).hexdigest()
        container_name = f"botsh-{dir_hash}"

        print(colored("Connecting to Docker...", "green"))
        self.client = docker.from_env()

        self.container = self._get_container(container_name, image, wipe)

    def _get_mounts(self) -> list[Mount]:
        mount = Mount(target="/work", source=self.current_directory, type="bind")

        return [mount]

    def _get_container(self, container_name: str, image: str, wipe: bool):
        try:
            print(colored("Locating existing container...", "green"))
            container = self.client.containers.get(container_name)
            if not wipe:
                print(colored("Using existing container.", "green"))
                if container.status != "running":
                    print(colored("Starting container...", "green"))
                    container.start()
                return container
            else:
                print(colored("Terminating existing container.", "green"))
                container.stop(timeout=0)
                container.remove(force=True)
        except docker.errors.NotFound:
            print(colored("No container exists, creating one.", "green"))
            pass

        print(colored("Pulling image...", "green"))
        self.client.images.pull(image)

        mounts = self._get_mounts()

        print(colored("Creating container...", "green"))
        container = self.client.containers.create(
            image,
            name=container_name,
            command="/bin/bash",
            tty=True,
            mounts=mounts,
            environment=["DEBIAN_FRONTEND=noninteractive"],
        )
        print(colored("Starting container...", "green"))
        container.start()
        return container

    def run_command(self, command: str) -> tuple[int, str]:
        exec = self.client.api.exec_create(
            self.container.id, f"bash -c '{command}'", workdir="/work"
        )
        exec_id = exec["Id"]

        output = self.client.api.exec_start(exec_id, stream=True)

        result = []
        for line in output:
            line = line.decode("utf-8")
            print(colored(line, "green"), end="")
            result.append(line)

        exit_code = self.client.api.exec_inspect(exec_id)["ExitCode"]

        return exit_code, "".join(result)

    def __del__(self):
        if hasattr(self, "container"):
            print(colored("Terminating container.", "green"))
            self.container.stop(timeout=0)
            # self.container.remove()
