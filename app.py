from flask import Flask, redirect, session, url_for

from config import Config
from db import close_db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.teardown_appcontext(close_db)

    from auth.routes import bp as auth_bp
    from serveur.routes import bp as serveur_bp
    from admin.routes import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(serveur_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def accueil():
        role = session.get("role")
        if role == "ADMIN":
            return redirect(url_for("admin.historique"))
        if role == "SERVEUR":
            return redirect(url_for("serveur.nouvelle_commande"))
        return redirect(url_for("auth.login"))

    @app.template_filter("fcfa")
    def fcfa(valeur):
        return f"{int(valeur):,} FCFA".replace(",", " ")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
