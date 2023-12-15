from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    MONGO_URI: str
    DATABASE: str = "timestyr"
    USER_SMART_TRANSACTIONS_COLLECTION: str = "UserSmartTransactionsDS"
    USER_SMART_TRANS_SCORE_COLLECTION: str = "UserSmartTransScoreDS"
    TRANSACTIONS_COLLECTION: str = "ProjTransDS"


settings = Config()  # type: ignore
