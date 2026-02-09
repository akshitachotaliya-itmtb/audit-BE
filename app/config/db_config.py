import os


RUNNING_ENV = os.getenv("RUNNING_ENV", "dev")

def get_db_config():
    if RUNNING_ENV == "dev":
        return {
            "host": os.getenv("DATABASE_HOST", "localhost"),
            "user": os.getenv("DATABASE_USER", "root"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "database": os.getenv("DATABASE_NAME"),
            "port": os.getenv("DATABASE_PORT", "3306"),
        }

    # WE WILL USE LATER THAT
    # elif RUNNING_ENV in ("test", "prod"):
    #     # Example: AWS Secrets Manager / Vault / etc.
    #     secrets = get_secrets(os.getenv("SECRET_NAME"))

    #     return {
    #         "host": secrets["SN_DATABASE_HOST"],
    #         "user": secrets["SN_DATABASE_USER"],
    #         "password": secrets["SN_DATABASE_PASSWORD"],
    #         "database": secrets["SN_DATABASE_NAME"],
    #         "port": secrets.get("SN_DATABASE_PORT", "3306"),
    #     }

    else:
        raise ValueError(f"Unknown RUNNING_ENV: {RUNNING_ENV}")