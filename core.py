import os
from dataclasses import dataclass

import openai

MODEL = "gpt-4-1106-preview"

# GPT-4 prices in USD, source:
# https://openai.com/pricing#language-models
USD_PER_INPUT_TOKEN = 0.01e-3
USD_PER_OUTPUT_TOKEN = 0.03e-3

TEMPERATURE = 0.1


def load_key():
    if 'OPENAI_API_KEY' not in os.environ:
        api_key_path = os.path.join(os.path.dirname(__file__), '.api_key')
        with open(api_key_path, 'r') as f:
            os.environ['OPENAI_API_KEY'] = f.read().strip()


class GptCore:
    """
    A class to interact with OpenAI's GPT-4 model.

    Attributes
    ----------
    input : function
        a function to get user input, takes no arguments, returns str or None
    output : function
        a function to output the model's response and info, takes str and Info
        object, returns None

    Methods
    -------
    main():
        The main loop to interact with the model.
    """
    def __init__(self, input, output):
        self.input = input
        self.output = output

        self.messages = []

        self.client = openai.OpenAI()

    def main(self):
        price = 0
        while prompt := self.input():
            self.messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=MODEL, messages=self.messages, temperature=TEMPERATURE)

            message = response.choices[0].message
            self.messages.append(message)

            content = message.content.strip()

            usage = response.usage
            prompt_tokens, completion_tokens = (
                usage.prompt_tokens, usage.completion_tokens)

            price += USD_PER_INPUT_TOKEN * prompt_tokens
            price += USD_PER_OUTPUT_TOKEN * completion_tokens

            self.output(content, Info(prompt_tokens, completion_tokens, price))


@dataclass
class Info:
    """
    A class representing the information about the interaction with the model.

    Attributes
    ----------
    prompt_tokens : int
        the number of tokens in the prompt
    completion_tokens : int
        the number of tokens in the completion
    price : float
        the total price of the interaction
    """
    prompt_tokens: int
    completion_tokens: int
    price: float

    def __repr__(self):
        return (
            f'Prompt tokens: {self.prompt_tokens}, '
            f'Completion tokens: {self.completion_tokens}, '
            f'Total price: {self.price:.3f} USD')
