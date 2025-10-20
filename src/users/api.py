import logging
from src.users.data import UserData
from src.users.service import UsersService

logger = logging.getLogger(__name__)


class UsersAPI:
    @staticmethod
    def initialize_users():
        logger.info("UsersAPI: Initializing users...")
        UserData.create_user_table()

    @staticmethod
    def add_user(name: str, location: str):
        if not UsersService.check_location(location):
            logger.error(f"Invalid location provided: {location}")
            raise ValueError("Invalid location")
        UserData.save_user_data(name, location)
