from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Define application settings here.
    # These can be overridden by environment variables.
    # For example, setting SANDBOX_IMAGE_NAME in the environment will override the default.
    
    sandbox_image_name: str = "my-sandbox-image"

    # This allows pydantic to read from environment variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

# Create a single instance of the settings to be used throughout the application
settings = Settings()
