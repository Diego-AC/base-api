from dotenv import load_dotenv

load_dotenv()

from .setup import create_app

__all__ = ['create_app']
