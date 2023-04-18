from jinja2 import Environment, PackageLoader

from botsh.history import CommandExecution
from botsh.logging import log

ENV = Environment(loader=PackageLoader("botsh", "templates"))
TEMPLATE = ENV.get_template("prompt.jinja2")

PROMPT_TRAILER = "EXPLANATION:"
COMMAND_TRAILER = "COMMAND:"

def generate_prompt(task: str, history: list[CommandExecution]) -> str:
    return (
        TEMPLATE.render(
            task=task,
            history=history,
        )
        + PROMPT_TRAILER
    )


class Response:
    command = None
    explanation = None


def parse_response(response: str) -> dict[str, str]:
    lines = response.splitlines()
    explanation = next(lines)

    command = ""
    command_line = next(lines)
    if command_line.startswith(COMMAND_TRAILER):
        command = command_line[len() + 1 :]
    else:
        log.warning(
            "Expected a command, got this instead.", command_line=command_line
        )

    for line in lines:
        command += line.strip()

    return Response(command=command, explanation=explanation)
