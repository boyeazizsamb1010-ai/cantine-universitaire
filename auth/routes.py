from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import get_db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_saisi = request.form.get("login", "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "")

        with get_db("AUTH").cursor() as cur:
            cur.execute("""
                SELECT id_employe, mot_de_passe_hash, nom, prenom, role, actif
                FROM employe WHERE login = %s
            """, (login_saisi,))
            employe = cur.fetchone()

        # Même message dans tous les cas : on ne révèle pas si le login existe
        if (employe is None or not employe[5]
                or not employe[1].startswith(("pbkdf2:", "scrypt:"))
                or not check_password_hash(employe[1], mot_de_passe)):
            flash("Identifiants incorrects.", "erreur")
            return render_template("login.html"), 401

        session.clear()
        session["id_employe"] = employe[0]
        session["nom_complet"] = f"{employe[3]} {employe[2]}"
        session["role"] = employe[4]
        return redirect(url_for("accueil"))

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
