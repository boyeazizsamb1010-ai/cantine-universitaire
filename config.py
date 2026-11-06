import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "a-changer-en-production")

    # Une chaîne de connexion par compte SQL (voir sql/01_roles_et_base.sql)
    DSN_AUTH = os.environ["DSN_AUTH"]
    DSN_SERVEUR = os.environ["DSN_SERVEUR"]
    DSN_ADMIN = os.environ["DSN_ADMIN"]
