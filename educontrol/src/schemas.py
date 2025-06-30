from pydantic import BaseModel

class MoodleAPIConn(BaseModel):
    url: str
    token: str
    periods: list[str]
    report_params: dict
    current_cort: int
    lmsName: str


