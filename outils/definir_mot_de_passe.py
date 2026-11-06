"""Définit le mot de passe d'un employé (stocké sous forme de hash).

Usage : python outils/definir_mot_de_passe.py <login> <mot_de_passe>
Utilise le compte SQL admin (DSN_ADMIN dans .env).
"""
import os
import sys

import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    login, mot_de_passe = sys.argv[1], sys.argv[2]
    if len(mot_de_passe) < 8:
        sys.exit("Le mot de passe doit contenir au moins 8 caractères.")

    load_dotenv()
    with psycopg2.connect(os.environ["DSN_ADMIN"]) as conn, conn.cursor() as cur:
        cur.execute("UPDATE employe SET mot_de_passe_hash = %s WHERE login = %s",
                    (generate_password_hash(mot_de_passe), login))
        if cur.rowcount == 0:
            sys.exit(f"Aucun employé avec le login « {login} ».")
    print(f"Mot de passe de « {login} » mis à jour.")


if __name__ == "__main__":
    main()
