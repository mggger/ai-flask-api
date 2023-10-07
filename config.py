import os

Config = {
    "openai_api_key": os.environ.get("API_KEY", "xxxx"),
    "model": "gpt-3.5-turbo",
    "is_local": os.environ.get("IS_LOCAL", False)
}
