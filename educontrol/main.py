#!/usr/bin/env python3
"""
Proyecto EduControl
"""

from src.utils.logging.logger_factory import setup_logging
from src.extract_data_flow import extract_data_flow
from src.utils.db import get_db, get_available_api_lms

def main():
    setup_logging()
    db = next(get_db())
    available_api_lms = get_available_api_lms(db)
    for api_lms in available_api_lms:
        extract_data_flow(api_lms, max_workers=4)


if __name__ == "__main__":
    main()
