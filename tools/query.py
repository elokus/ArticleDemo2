from typing import Type, Union, Literal

from pydantic import BaseModel
from sqlmodel import Session, select, SQLModel

from database.db import engine
from database.models import *
from tools.base import ToolResult, Tool


TABLES = {
    "expense": Expense,
    "revenue": Revenue,
    "customer": Customer
}


class WhereStatement(BaseModel):
    column: str
    operator: Literal["eq", "gt", "lt", "gte", "lte", "ne", "ct"]
    value: str


class QueryConfig(BaseModel):
    table_name: str
    select_columns: list[str]
    where: list[Union[WhereStatement, None]]


def query_data_function(query_config: QueryConfig) -> ToolResult:
    """Query the database via natural language."""
    if query_config.table_name not in TABLES:
        return ToolResult(content=f"Table name {query_config.table_name} not found in database models", success=False)

    sql_model = TABLES[query_config.table_name]

    # query_config = validate_query_config(query_config, sql_model)
    data = sql_query_from_config(query_config, sql_model)

    return ToolResult(content=f"Query results: {data}", success=True)


query_data_tool = Tool(
    name="query_data_tool",
    model=QueryConfig,
    function=query_data_function,
    parse_model=True
)


# === Helper ===

def sql_query_from_config(
        query_config: QueryConfig,
        sql_model: Type[SQLModel]):

    with Session(engine) as session:
        selection = []
        for column in query_config.select_columns:
            if column not in sql_model.__annotations__:
                return f"Column {column} not found in model {sql_model.__name__}"
            selection.append(getattr(sql_model, column))
        statement = select(*selection)
        wheres = query_config.where
        if wheres:
            for where in wheres:

                if where.column not in sql_model.__annotations__:  # noqa
                    return f"Column {where['column']} not found in model {sql_model.__name__}"

                elif where.operator == "eq":
                    statement = statement.where(getattr(sql_model, where.column) == where.value)
                elif where.operator == "gt":
                    statement = statement.where(getattr(sql_model, where.column) > where.value)
                elif where.operator == "lt":
                    statement = statement.where(getattr(sql_model, where.column) < where.value)
                elif where.operator == "gte":
                    statement = statement.where(getattr(sql_model, where.column) >= where.value)
                elif where.operator == "lte":
                    statement = statement.where(getattr(sql_model, where.column) <= where.value)
                elif where.operator == "ne":
                    statement = statement.where(getattr(sql_model, where.column) != where.value)
                elif where.operator == "ct":
                    statement = statement.where(getattr(sql_model, where.column).contains(where.value))

        result = session.exec(statement)
        data = result.all()
        try:
            data = [repr(d) for d in data]
        except:
            pass
    return data
