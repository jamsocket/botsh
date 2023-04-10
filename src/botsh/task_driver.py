from termcolor import colored

from botsh.docker_exec import DockerContainer
from botsh.history import CommandExecution
from botsh.llm import LLM
from botsh.prompt import parse_response

class TaskDriver:
    history: list[CommandExecution]
    task: str
    container: DockerContainer
    llm: LLM

    def __init__(self, task: str, llm: LLM, wipe: bool = False):
        self.task = task
        self.llm = llm
        self.container = DockerContainer("ubuntu:latest", wipe)
        print(colored("Updating apt-get...", "green"))
        self.container.run_command("apt-get -qq update")
        self.history = list()

        # Run a few commands. These serve both to orient the agent, and to
        # provide some examples of what we want.
        self.run_command_and_add_to_history(
            "I would like to know five files in the current directory.",
            "ls -al | head -n 5",
        )

        self.run_command_and_add_to_history(
            "I would like to know which directory I am in.", "pwd"
        )

    def run_command_and_add_to_history(self, explanation: str, command: str):
        exit_code, output = self.container.run_command(command)
        self.history.append(CommandExecution(explanation, command, output, exit_code))
        return output

    def step(self):
        response = self.llm.completion(self.task, self.history)
        print(colored(response, "blue"))

        result = parse_response(response)
        command = result.get("COMMAND", "")
        explanation = result.get("EXPLANATION", "")
        if explanation != "":
            print(colored(explanation, "yellow"))
        if command == "":
            print(colored("Task completed", "yellow"))
            return True

        print(colored("RESULT: ", "red"), end="")

        exit_code, output = self.container.run_command(command)
        lines = output.splitlines()
        if len(lines) > 10:
            truncated = len(lines) - 10
            result = (
                f"[ {truncated} lines truncated ]"
                + "\n".join(lines[-10:])
                + "\n[...]\n"
            )

        self.history.append(CommandExecution(explanation, command, output, exit_code))
