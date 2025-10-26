from openai import OpenAI
import os
from dotenv import  load_dotenv

load_dotenv()

from agent_ui.input_registry import RegistryManager

class UIPrompt:
    def __init__(self, registry: RegistryManager, user_input: str):
        self.registry: RegistryManager = registry
        self.user_input: str = user_input
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.response: str = ""

    def _build_context(self):
        available_inputs = self.registry.list_inputs()
        details = "\n".join([f"- {inp['Input ID']}: {inp['Schema']}"
            for inp in [self.registry.get_input(i) for i in available_inputs]
        ])
        context = f"""
            You are an agentic UI generator for AR glasses.

            The user will describe what they want to see visually.
            You have access to these inputs (data sources):

            {details}

            Using these, write Python code that draws the requested UI
            using OpenCV. The code should:
            - Read from the provided data sample (simulate live data).
            - Draw simple overlays like text, gauges, or charts.
            - Use readable variable names and comments.
            - Avoid excessive imports or long logic.
            - Do not include commentary or content outside of the code block.
        """
        return context.strip()

    def get_response(self, model: str = "gpt-4o-mini", max_tokens: int = 800):
        system_context = self._build_context()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": self.user_input}
                ],
                max_completion_tokens=max_tokens
            )
            self.response = completion.choices[0].message.content.strip()
            return self.response

        except Exception as e:
            print("❌ Error calling OpenAI API:", e)
            return "Error: " + str(e)
