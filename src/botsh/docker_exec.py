import hashlib
import os
import shlex

import docker
from docker.types import Mount
from termcolor import colored

from botsh.logging import log


class DockerContainer:
    current_directory: str
    shell_command: str

    def __init__(self, image: str, shell_command: str, wipe: bool):
        self.current_directory = os.getcwd()
        self.shell_command = shell_command
        dir_hash = hashlib.sha256(self.current_directory.encode("utf-8")).hexdigest()
        container_name = f"botsh-{dir_hash}"

        log.info("Connecting to Docker...")
        self.client = docker.from_env()

        self._get_container(container_name, image, wipe)

    def _get_mounts(self) -> list[Mount]:
        mount = Mount(target="/work", source=self.current_directory, type="bind")

        return [mount]

    def _get_container(self, container_name: str, image: str, wipe: bool):
        try:
            log.info("Locating existing container...")
            container = self.client.containers.get(container_name)
            if not wipe:
                log.info("Using existing container.")
                if container.status != "running":
                    log.info("Starting container...")
                    container.start()
                return container
            else:
                log.info("Terminating existing container.")
                container.stop(timeout=0)
                container.remove(force=True)
        except docker.errors.NotFound:
            log.info("No container exists, creating one.")
            pass

        log.info("Pulling image...")
        self.client.images.pull(image)

        mounts = self._get_mounts()

        log.info("Creating container...")
        container = self.client.containers.create(
            image,
            name=container_name,
            command=self.shell_command,
            tty=True,
            mounts=mounts,
            environment=["DEBIAN_FRONTEND=noninteractive"],
        )
        log.info("Starting container...")
        container.start()
        log.info("Updating apt-get...")
        self.container = container
        self.run_command("apt-get -qq update")

    def run_command(self, command: str, quiet: bool = False) -> tuple[int, str]:
        quoted_command = shlex.quote(command)

        exec = self.client.api.exec_create(
            self.container.id,
            f"{self.shell_command} -c {quoted_command}",
            workdir="/work",
        )
        exec_id = exec["Id"]

        output = self.client.api.exec_start(exec_id, stream=True)

        result = []
        for line in output:
            line = line.decode("utf-8")
            if not quiet:
                print(colored(line, "green"), end="")
            result.append(line)

        exit_code = self.client.api.exec_inspect(exec_id)["ExitCode"]

        return exit_code, "".join(result)

    def __del__(self):
        if hasattr(self, "container"):
            log.info("Terminating container.")
            self.container.stop(timeout=0)
            # self.container.remove()
