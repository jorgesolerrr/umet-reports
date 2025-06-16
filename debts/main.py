from src.logging.logger_factory import setup_logging
from src.db import get_connection





def main():
    setup_logging()
    conn = get_connection()
    print(conn)

if __name__ == "__main__":
    main()