import os
import yaml
import boto3
from dotenv import load_dotenv


class SecretHandler:
    """_summary_"""

    def get_secrets(self, aws_parameter_keys: list = []) -> dict:
        # .envからシークレットを取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(f"{current_dir}/.env"):
            load_dotenv(dotenv_path=f"{current_dir}/.env")

        secrets = os.environ

        if len(aws_parameter_keys) == 0:
            return secrets

        """
        AWSのパラメータストアからシークレット情報を取得
        """
        # Create a session using your current creds
        boto3_session = boto3.Session(
            aws_access_key_id=secrets["AMAZON_ACCESS_KEY_ID"],
            aws_secret_access_key=secrets["AMAZON_SECRET_ACCESS_KEY"],
            region_name="ap-northeast-1",
        )

        # Create a client of Systems Manager
        ssm = boto3_session.client("ssm")

        # 10件ずつに分割
        parameter_names_unit = []
        tmp_aws_parameter_keys = []
        for i, secret_key in enumerate(aws_parameter_keys):
            tmp_aws_parameter_keys.append(secret_key)
            if i % 10 == 9:
                parameter_names_unit.append(tmp_aws_parameter_keys)
                tmp_aws_parameter_keys = []
        if len(tmp_aws_parameter_keys) > 0:
            parameter_names_unit.append(tmp_aws_parameter_keys)

        for parameter_names in parameter_names_unit:
            response = ssm.get_parameters(
                Names=parameter_names,
                WithDecryption=True,
            )
            print(response)

            for parameter in response["Parameters"]:
                values = yaml.safe_load(parameter["Value"])
                self.set_secrets(
                    base_key=parameter["Name"],
                    values=values,
                    secrets=secrets,
                )

        return secrets

    def set_secrets(self, base_key: str, values: dict, secrets: dict):
        print(f"base_key: {base_key}")
        for key, value in values.items():
            secret_key = base_key
            if isinstance(value, dict):
                print(f"is_dict: {value}")
                secret_key = f"{secret_key}_{key}"
                self.set_secrets(base_key=secret_key, values=value, secrets=secrets)
                continue
            print(f"secret_key: {secret_key}, value: {value}")
            secrets[f"{secret_key}_{key}"] = value
