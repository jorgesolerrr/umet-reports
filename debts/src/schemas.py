from pydantic import BaseModel

class MoodleConn(BaseModel):
    host: str
    port: int
    db_user: str
    db_password: str
    db_name: str
    db_programs: str
    
class UserMoodle(BaseModel):    
    userid : str
    firstname : str
    lastname : str
    email : str