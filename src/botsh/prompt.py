from botsh.history import CommandExecution
from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader("botsh", "templates"))
TEMPLATE = ENV.get_template("prompt.jinja2")

PROMPT_TRAILER = "EXPLANATION:"

def generate_prompt(task: str, history: list[CommandExecution]) -> str:
    return TEMPLATE.render(
        task = task,
        history = history,
    ) + PROMPT_TRAILER

def parse_response(response: str) -> dict[str, str]:
    response = PROMPT_TRAILER + response

    return dict(m.strip().split(': ', 1) for m in response.splitlines() if m.strip())
