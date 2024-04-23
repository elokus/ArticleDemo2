from typing import Type, Callable, Union

from tools.utils import convert_to_openai_tool
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel


class ToolResult(BaseModel):
    content: str
    success: bool


class Tool(BaseModel):
    name: str
    model: Union[Type[BaseModel], Type[SQLModel], None]
    function: Callable
    validate_missing: bool = True
    parse_model: bool = False
    exclude_keys: list[str] = ["id"]

    model_config = ConfigDict(arbitrary_types_allowed=True)


    def run(self, **kwargs) -> ToolResult:
        missing_values = self.validate_input(**kwargs)
        if missing_values:
            content = f"Missing values: {', '.join(missing_values)}"
            return ToolResult(content=content, success=False)

        if self.parse_model:
            if hasattr(self.model, "model_validate"):
                input_ = self.model.model_validate(kwargs)
            else:
                input_ = self.model(**kwargs)
            result = self.function(input_)

        else:
            result = self.function(**kwargs)
        return ToolResult(content=str(result), success=True)

    def validate_input(self, **kwargs):
        if not self.validate_missing or not self.model:
            return []
        model_keys = set(self.model.__annotations__.keys()) - set(self.exclude_keys)
        input_keys = set(kwargs.keys())
        missing_values = model_keys - input_keys
        return list(missing_values)

    @property
    def openai_tool_schema(self):
        schema = convert_to_openai_tool(self.model)
        schema["function"]["name"] = self.name
        if schema["function"]["parameters"].get("required"):
            del schema["function"]["parameters"]["required"]
        schema["function"]["parameters"]["properties"] = {
            key: value for key, value in schema["function"]["parameters"]["properties"].items()
            if key not in self.exclude_keys
        }
        return schema


class ReportSchema(BaseModel):
    report: str


def report_function(report: ReportSchema) -> str:
    return report.report


report_tool = Tool(
    name="report_tool",
    model=ReportSchema,
    function=report_function,
    validate_missing=False,
    parse_model=True
)
