import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=os.path.join(Path(__file__).parent, '.env'))


class Settings(BaseSettings):
    app_name: str = 'API Mi Body Composition 2 Garmin Connect'
    app_version: str = '0.0.17'
    api_port: int = os.getenv('API_PORT', 90655)
    gc_user: str = os.getenv('GC_USER', 'user@gmail.com')
    gc_pass: str = os.getenv('GC_PASS', 'pass')
    gc_api: str = os.getenv('GC_API')
    max_weight: int = os.getenv('MAX_W', 85)
    min_weight: int = os.getenv('MIN_W', 70)
    birth_date: str = os.getenv('BIRTH', '24-02-2022')
    sex: str = os.getenv('SEX', 'male')
    height: int = os.getenv('HEIGHT', 180)


settings = Settings()
