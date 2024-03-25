import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DBConfig:
    PG_NAME = os.environ.get('POSTGRES_NAME')
    PG_HOST = os.environ.get('POSTGRES_HOST') or 'postgres'
    PG_PORT = os.environ.get('POSTGRES_PORT') or 5432
    PG_USER = os.environ.get('POSTGRES_USER')
    PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD')


