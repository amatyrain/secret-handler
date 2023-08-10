import os
from dotenv import load_dotenv


class SecretHandler:
    """_summary_"""

    def get_secrets(self) -> dict:
        # .envから環境変数を取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(f"{current_dir}/.env"):
            load_dotenv(dotenv_path=f"{current_dir}/.env")
        secrets = os.environ

        return secrets
