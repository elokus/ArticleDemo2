from typing import Type, Callable, Optional

from agents.base import OpenAIAgent
from tools.base import Tool
from tools.report_tool import report_tool
from pydantic import BaseModel, ConfigDict, Field

from tools.utils import convert_to_openai_tool


SYSTEM_MESSAGE = """You are tasked with completing specific objectives and must report the outcomes. At your disposal, you have a variety of tools, each specialized in performing a distinct type of task.

For successful task completion:
Thought: Consider the task at hand and determine which tool is best suited based on its capabilities and the nature of the work. 
If you can complete the task or answer a question, soley by the information provided you can use the report_tool directly.

Use the report_tool with an instruction detailing the results of your work or to answer a user question.
If you encounter an issue and cannot complete the task:

Use the report_tool to communicate the challenge or reason for the task's incompletion.
You will receive feedback based on the outcomes of each tool's task execution or explanations for any tasks that couldn't be completed. This feedback loop is crucial for addressing and resolving any issues by strategically deploying the available tools.

On error: If information are missing consider if you can deduce or calculate the missing information and repeat the tool call with more arguments.

Use the information provided by the user to deduct the correct tool arguments.
Before using a tool think about the arguments and explain each input argument used in the tool. 
Return only one tool call at a time! Explain your thoughts!
{context}
"""


class EmptyArgModel(BaseModel):
    pass


class TaskAgent(BaseModel):
    name: str
    description: str
    arg_model: Type[BaseModel] = EmptyArgModel
    access_roles: list[str] = ["all"]

    create_context: Callable = None
    create_user_context: Callable = None
    tool_loader: Callable = None

    system_message: str = SYSTEM_MESSAGE
    tools: list[Tool]
    examples: list[dict] = None
    routing_example: list[dict] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def load_agent(self, **kwargs) -> OpenAIAgent:

        input_kwargs = self.arg_model(**kwargs)
        kwargs = input_kwargs.dict()

        context = self.create_context(**kwargs) if self.create_context else None
        user_context = self.create_user_context(**kwargs) if self.create_user_context else None

        if self.tool_loader:
            self.tools.extend(self.tool_loader(**kwargs))

        if report_tool not in self.tools:
            self.tools.append(report_tool)

        return OpenAIAgent(
            tools=self.tools,
            context=context,
            user_context=user_context,
            system_message=self.system_message,
            examples=self.examples,
        )

    @property
    def openai_tool_schema(self):
        return convert_to_openai_tool(self.arg_model, name=self.name, description=self.description)
