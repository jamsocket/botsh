class CommandExecution:
    explanation: str
    command: str
    result: str

    def __init__(self, explanation: str, command: str, result: str):
        self.explanation = explanation
        self.command = command
        self.result = result
