from functools import wraps

from flask import flash, redirect, session, url_for


def role_requis(*roles):
    """Restreint une route aux employés ayant l'un des rôles donnés."""
    def decorateur(vue):
        @wraps(vue)
        def enveloppe(*args, **kwargs):
            if "id_employe" not in session:
                flash("Veuillez vous connecter.", "erreur")
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                flash("Accès refusé.", "erreur")
                return redirect(url_for("accueil"))
            return vue(*args, **kwargs)
        return enveloppe
    return decorateur
