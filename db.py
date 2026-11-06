"""Connexion PostgreSQL avec le compte SQL correspondant au rôle connecté."""
import psycopg2
from flask import current_app, g, session


def _dsn_pour(role: str) -> str:
    dsn = {
        "AUTH": current_app.config["DSN_AUTH"],
        "SERVEUR": current_app.config["DSN_SERVEUR"],
        "ADMIN": current_app.config["DSN_ADMIN"],
    }.get(role)
    if dsn is None:
        raise PermissionError("Aucun rôle valide.")
    return dsn


def get_db(role: str | None = None):
    """Retourne la connexion de la requête en cours.

    Sans argument, utilise le rôle de l'employé connecté (session["role"]).
    """
    role = role or session.get("role")
    cle = f"db_{role}"
    if cle not in g:
        setattr(g, cle, psycopg2.connect(_dsn_pour(role)))
    return getattr(g, cle)


def close_db(_exc=None):
    for cle in ("db_AUTH", "db_SERVEUR", "db_ADMIN"):
        conn = g.pop(cle, None)
        if conn is not None:
            conn.close()
