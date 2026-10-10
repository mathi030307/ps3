import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "PS-03 Ad-to-Landing-Page Message Match Auditor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Request limits
    MAX_URL_LENGTH: int = 2048
    MAX_HTML_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    FETCH_TIMEOUT_SECONDS: float = 8.0
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (MessageMatchAuditor/1.0)"

    # Matching & Scoring thresholds
    SUPPORTED_SIMILARITY_THRESHOLD: float = 85.0
    PARTIAL_MATCH_SIMILARITY_THRESHOLD: float = 60.0
    UNCERTAIN_SIMILARITY_THRESHOLD: float = 40.0

settings = Settings()
