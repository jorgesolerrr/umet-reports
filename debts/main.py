from src.logging.logger_factory import setup_logging
from src.db import get_db, get_suspended_users





def main():
    setup_logging()
    db = get_db()
    suspended_users = get_suspended_users(db, "CESDEL-CARRERAS(NEW)")
    

if __name__ == "__main__":
    main()