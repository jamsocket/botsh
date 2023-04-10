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
    parser.add_argument(
        "--save-transcript", action="store_true", help="Save transcript to file"
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Start with a fresh container even if one exists for this directory.",
    )
    parser.add_argument(
        "--rm",
        action="store_true",
        help="Remove the container after the task is complete.",
    )
    args = parser.parse_args()

    if "OPENAI_API_KEY" not in environ:
        log.error(
            "OpenAI API key not found."
            "Please set the OPENAI_API_KEY environment variable."
        )
        return

    llm = LLM(args.model, save_transcript=args.save_transcript)
    container = DockerContainer(
        args.image, args.shell_command, wipe=args.wipe, remove_on_exit=args.rm
    )
    task_runner = TaskDriver(args.prompt, container, llm)

    try:
        for _ in range(args.max_rounds):
            result = task_runner.step()
            if result:
                break
        else:
            log.warning(
                "Task did not complete, stopped after reaching its round limit. "
                "Usually this means it got stuck, but you can try passing a higher "
                "value to --max-rounds.",
                max_rounds=args.max_rounds,
            )
    except KeyboardInterrupt:
        log.warning("Task interrupted by user.")
    except EOFError:
        log.warning("Task interrupted by user.")


if __name__ == "__main__":
    main()
