import docker
from docker.types import Mount
import argparse
import openai
import os
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


class TaskDriver:
    def __init__(self, prompt):
        self.prompt = prompt
        self.container = DockerContainer("ubuntu:latest")
        print(colored("Updating apt-get...", "green"))
        self.container.run_command("apt-get -qq update")
        self.history = [
            {
                "EXPLANATION": "I would like to know what files are in the current directory.",
                "COMMAND": "ls -al",
                "RESULT": self.container.run_command("ls -al"),
            },
            {
                "EXPLANATION": "I would like to know which directory I am in.",
                "COMMAND": "pwd",
                "RESULT": self.container.run_command("pwd"),
            },
        ]

    def construct_prompt(self):
        history = "\n".join(
            "\n".join(f"{key}: {value}" for key, value in entry.items())
            for entry in self.history
        )

        return f"""You are given a task to accomplish by running commands in a Bash shell on Ubuntu Linux.

You may install software using `apt-get -qq -y`. Do not run software that requires user interaction.

Any files referenced in the prompt are relative to the current directory. You can read from this directory but not write to it.
If the prompt asks you to output a file, write it to /output. If you need to write a temporary file, write it to /tmp.

Answer in the format:

EXPLANATION: explain why you are running the command
COMMAND: the command you are running

When you have completed the task, respond with an empty COMMAND.

The task you are trying to accomplish is:

{self.prompt}

{history}
EXPLANATION:"""

    def step(self):
        prompt = self.construct_prompt()
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["DONE", "RESULT:", "EXPLANATION:"],
        )

        response = response.choices[0].text
        print(colored(response, "blue"))

        explanation, command = response.split("COMMAND:")
        command = command.strip()

        if command == "":
            print(colored("Task completed", "yellow"))
            return True

        print(colored("RESULT: ", "red"), end="")

        result = self.container.run_command(command)
        lines = result.splitlines()
        if len(lines) > 10:
            truncated = len(lines) - 10
            result = f"[ {truncated} lines truncated ]" + "\n".join(lines[-10:]) + "\n[...]\n"

        self.history.append(
            {"EXPLANATION": explanation, "COMMAND": command, "RESULT": result}
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt to execute.")
    args = parser.parse_args()

    task_runner = TaskDriver(args.prompt)

    for _ in range(10):
        result = task_runner.step()
        if result:
            break


if __name__ == "__main__":
    main()
