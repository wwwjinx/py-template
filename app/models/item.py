from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    """示例表，按需改或删。"""

    id: int | None = Field(default=None, primary_key=True)
    name: str
