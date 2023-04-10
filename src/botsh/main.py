"""Task runner powered by OpenAI and Docker.

Invoke botsh by providing a task as a command line argument.

botsh will create a bare Ubuntu Docker container associated with
the current directory, or create one if one does not exist. botsh
will then attach the OpenAI API to a shell running in the container
to attempt to complete the given task.
"""

import argparse
from os import environ

from botsh.docker_exec import DockerContainer
from botsh.llm import LLM
from botsh.logging import log
from botsh.task_driver import TaskDriver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="Prompt to execute.")
    parser.add_argument("--max-rounds", type=int, default=10)
    parser.add_argument(
        "--model",
        default="text-davinci-003",
        help="OpenAI text completion model to use.",
    )
    parser.add_argument(
        "--image",
        default="ubuntu:latest",
        help="Docker image to use."
        "The current hard-coded prompt works for Debian-derived distributions.",
    )
    parser.add_argument(
        "--shell-command",
        default="/bin/bash",
        help="Shell to invoke within the container.",
    )
    args = parser.parse_args()

    if "OPENAI_API_KEY" not in environ:
        log.error(
            "OpenAI API key not found."
            "Please set the OPENAI_API_KEY environment variable."
        )
        return

    llm = LLM(args.model, save_transcript=True)
    container = DockerContainer(args.image, args.shell_command, wipe=False)
    task_runner = TaskDriver(args.prompt, container, llm)

    for _ in range(args.max_rounds):
        result = task_runner.step()
        if result:
            break
    else:
        log.warning(
            f"Task did not complete, stopped after exhausting {args.max_rounds} rounds."
            " Usually this means it got stuck, but you can try passing a higher "
            "value to --max-rounds."
        )


if __name__ == "__main__":
    main()
