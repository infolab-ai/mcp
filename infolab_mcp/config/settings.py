"""MCP Infolab server configuration."""
import os

from dotenv import load_dotenv
from pydantic import HttpUrl, SecretStr, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Infolab OAuth Settings
    load_dotenv()

# Initialize settings
settings = Settings()
