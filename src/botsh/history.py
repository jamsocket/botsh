class CommandExecution:
    explanation: str
    command: str
    result: str
    exit_code: int

    def __init__(self, explanation: str, command: str, result: str, exit_code: int):
        self.explanation = explanation
        self.command = command
        self.result = result
        self.exit_code = exit_code
