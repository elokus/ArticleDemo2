from openai import OpenAI

import colorama

from agents.task import TaskAgent

from agents.utils import parse_function_args


SYSTEM_MESSAGE = """You are a helpful assistant.
Role: You are an AI Assistant designed to serve as the primary point of contact for users interacting through a chat interface. 
Your primary role is to understand users' requests related to database operations and route these requests to the appropriate tool.

Capabilities: 
You have access to a variety of tools designed for Create, Read operations on a set of predefined tables in a database. 

Tables:
{table_names}
"""

NOTES = """Important Notes:
Always confirm the completion of the requested operation with the user.
Maintain user privacy and data security throughout the interaction.
If a request is ambiguous or lacks specific details, ask follow-up questions to clarify the user's needs."""


PROMPT_EXTRA = {
    "table_names": "expense, revenue, customer"
}

class RoutingAgent:

    def __init__(
            self,
            tools: list[TaskAgent] = None,
            client: OpenAI = OpenAI(),
            system_message: str = SYSTEM_MESSAGE,
            model_name: str = "gpt-3.5-turbo",
            max_steps: int = 5,
            verbose: bool = True,
            prompt_extra: dict = None,
            examples: list[dict] = None,
            context: str = None
    ):
        self.tools = tools
        self.client = client
        self.model_name = model_name
        self.system_message = system_message
        self.memory = []
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.prompt_extra = prompt_extra or PROMPT_EXTRA
        self.examples = self.load_examples(examples)
        self.context = context or ""

    def load_examples(self, examples: list[dict] = None):
        examples = examples or []
        for agent in self.tools:
            examples.extend(agent.routing_example)
        return examples

    def run(self, user_input: str, employee_id: int = None, **kwargs):
        context = kwargs.get("context") or self.context
        if context:
            user_input_with_context = f"{context}\n---\n\nUser Message: {user_input}"
        else:
            user_input_with_context = user_input
        self.to_console("START", f"Starting Routing Agent with Input:\n'''{user_input_with_context}'''")
        partial_variables = {**self.prompt_extra, "context": context}
        system_message = self.system_message.format(**partial_variables)

        # TODO: get user roles
        messages = [
            {"role": "system", "content": system_message},
            *self.examples,
            {"role": "user", "content": user_input}
        ]

        tools = [tool.openai_tool_schema for tool in self.tools]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools
        )
        self.step_history.append(response.choices[0].message)
        self.to_console("RESPONSE", response.choices[0].message.content, color="blue")
        tool_kwargs = parse_function_args(response)
        tool_name = response.choices[0].message.tool_calls[0].function.name
        self.to_console("Tool Name", tool_name)
        self.to_console("Tool Args", tool_kwargs)

        agent = self.prepare_agent(tool_name, tool_kwargs)
        return agent.run(user_input)

    def prepare_agent(self, tool_name, tool_kwargs):
        for agent in self.tools:
            if agent.name == tool_name:
                input_kwargs = agent.arg_model.model_validate(tool_kwargs)
                return agent.load_agent(**input_kwargs.dict())
        raise ValueError(f"Agent {tool_name} not found")

    def to_console(self, tag: str, message: str, color: str = "green"):
        if self.verbose:
            color_prefix = colorama.Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")