import os

import docker
from docker.types import Mount
from termcolor import colored


class DockerContainer:
    def __init__(self, image):
        print(colored("Connecting to Docker...", "green"))
        self.client = docker.from_env()
        print(colored("Pulling image...", "green"))
        self.client.images.pull(image)

        current_directory = os.getcwd()
        mount = Mount(
            target="/work", source=current_directory, type="bind", read_only=True
        )

        os.makedirs("./output", exist_ok=True)
        mount_output = Mount(
            target="/output",
            source=os.path.abspath("output"),
            type="bind",
            read_only=False,
        )

        print(colored("Creating container...", "green"))
        self.container = self.client.containers.create(
            image,
            command="/bin/bash",
            tty=True,
            mounts=[mount, mount_output],
            environment=["DEBIAN_FRONTEND=noninteractive"],
        )
        print(colored("Starting container...", "green"))
        self.container.start()

    def run_command(self, command):
        _, output = self.container.exec_run(
            f"bash -c '{command}'", stream=True, workdir="/work"
        )

        result = []
        for line in output:
            line = line.decode("utf-8")
            print(colored(line, "green"), end="")
            result.append(line)

        return "".join(result)

    def __del__(self):
        if hasattr(self, "container"):
            self.container.stop(timeout=0)
            self.container.remove()
