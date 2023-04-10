import os
from datetime import datetime

import openai

from botsh.history import CommandExecution
from botsh.prompt import generate_prompt


class LLM:
    def __init__(self, model, save_transcript: bool = False):
        self.model = model
        self.save_transcript = save_transcript
        self.count = 0
        self.session_time = datetime.now().strftime("%Y%m%d-%H%M%S")

    def completion(self, task: str, history: list[CommandExecution]):
        prompt = generate_prompt(task, history)
        transcript_dirname = os.path.join(
            os.getcwd(), "transcripts", self.session_time, str(self.count)
        )

        if self.save_transcript:
            os.makedirs(transcript_dirname, exist_ok=True)
            with open(os.path.join(transcript_dirname, "request.txt"), "w") as f:
                f.write(prompt)
            self.count += 1

        response = self._completion(prompt)

        if self.save_transcript:
            with open(os.path.join(transcript_dirname, "response.txt"), "w") as f:
                f.write(response)
        
        return response

    def _completion(self, prompt):
        response = openai.Completion.create(
            engine=self.model,
            prompt=prompt,
            temperature=0.0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["DONE", "OUTPUT:", "EXPLANATION:"],
        )

        return response.choices[0].text
