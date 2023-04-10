from botsh.task_driver import CommandExecution
from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader("botsh", "templates"))
TEMPLATE = ENV.get_template("prompt.jinja2")

def generate_prompt(task: str, history: list[CommandExecution]) -> str:
    return TEMPLATE.render(
        task = task,
        history = history,
    )