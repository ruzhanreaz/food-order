from pydantic import BaseModel

class MenuItem(BaseModel):
    id: str
    name: str
    price: float

class Restaurant(BaseModel):
    id: str
    name: str
    cuisine: str
    menu: list[MenuItem]