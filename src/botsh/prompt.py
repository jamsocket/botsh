from jinja2 import Environment, PackageLoader

from botsh.history import CommandExecution
from botsh.logging import log

ENV = Environment(loader=PackageLoader("botsh", "templates"))
TEMPLATE = ENV.get_template("prompt.jinja2")

PROMPT_TRAILER = "EXPLANATION:"


def generate_prompt(task: str, history: list[CommandExecution]) -> str:
    return (
        TEMPLATE.render(
            task=task,
            history=history,
        )
        + PROMPT_TRAILER
    )


def _parse_response(response: str):
    response = PROMPT_TRAILER + response

    for line in response.splitlines():
        line = line.strip()
        if line == "":
            continue
        try:
            key, value = line.split(":", 1)
            yield key.strip(), value.strip()
        except ValueError:
            log.warning("Response line does not contain a colon; ignoring.", line=line)


def parse_response(response: str) -> dict[str, str]:
    return dict(_parse_response(response))
