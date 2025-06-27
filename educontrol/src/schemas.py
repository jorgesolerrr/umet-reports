from pydantic import BaseModel

class MoodleAPIConn(BaseModel):
    url: str
    token: str
    periods: list[str]


