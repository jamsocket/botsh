import argparse

from botsh.task_driver import TaskDriver
from botsh.llm import LLM

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Prompt to execute.")
    args = parser.parse_args()

    llm = LLM(save_transcript=True)
    task_runner = TaskDriver(args.prompt, llm)

    for _ in range(10):
        result = task_runner.step()
        if result:
            break


if __name__ == "__main__":
    main()
