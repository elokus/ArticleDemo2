from langchain_core.utils.function_calling import _rm_titles
from typing import Type, Optional
from langchain_core.utils.json_schema import dereference_refs
from pydantic import BaseModel
from typing import Type
import types
import typing

import sqlalchemy
from pydantic import BaseModel

def convert_to_openai_tool(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
) -> dict:
    """Converts a Pydantic model to a function description for the OpenAI API."""
    function = convert_pydantic_to_openai_function(
        model, name=name, description=description
    )
    return {"type": "function", "function": function}


def convert_pydantic_to_openai_function(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rm_titles: bool = True,
) -> dict:
    """Converts a Pydantic model to a function description for the OpenAI API."""

    model_schema = model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema()
    schema = dereference_refs(model_schema)
    schema.pop("definitions", None)
    title = schema.pop("title", "")
    default_description = schema.pop("description", "")
    return {
        "name": name or title,
        "description": description or default_description,
        "parameters": _rm_titles(schema) if rm_titles else schema,
    }