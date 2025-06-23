from pydantic import BaseModel

class MoodleConn(BaseModel):
    host: str
    port: int
    db_user: str
    db_password: str
    db_name: str
    db_programs: str
    lms_name: str