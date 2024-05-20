from enum import Enum
import os
from dotenv import load_dotenv
load_dotenv()

# All the configurations and magic values are stored in enums
class Config(Enum):
    SLACK_WORKSPACE_URL = os.getenv("SLACK_WORKSPACE_URL")
    SLACK_EMAIL = os.getenv("SLACK_EMAIL")
    SLACK_PASSWORD = os.getenv("SLACK_PASSWORD")
    CHANNEL_NAME = os.getenv("CHANNEL_NAMES")
    START_DATE = os.getenv("START_DATE")
    START_MONTH = os.getenv("START_MONTH")
    START_YEAR = os.getenv("START_YEAR")

class LoginPage(Enum):
    ENTER_EMAIL = "email"
    ENTER_PASSWORD = "password"
    SIGNIN = "signin_btn"

class ChannelsPage(Enum):
    BASE_CONTAINER = 'c-message_kit__gutter'
    DATE_BUTTON = "c-message_list__day_divider__label__pill"
    SCROLL_BAR = "c-scrollbar__bar"
    PROFILE = "c-button-unstyled.c-message_kit__avatar.c-avatar.c-avatar--interactive"
    USERNAME = 'button[data-qa="message_sender_name"]'
    TIMESTAMP = 'c-timestamp__label'
    INTRODUCTION = 'c-message_kit__gutter__right'
