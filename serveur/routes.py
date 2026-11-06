from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth.decorators import role_requis
from db import get_db
from services.commande_service import (MODES_PAIEMENT, CommandeErreur,
                                       annuler_commande, encaisser_commande,
                                       enregistrer_commande)

bp = Blueprint("serveur", __name__, url_prefix="/serveur")


def _plats_du_jour(cur):
    """Plats du menu du jour ; à défaut, tous les plats disponibles."""
    cur.execute("""
        SELECT DISTINCT p.id_plat, p.nom, p.prix_base, cp.libelle
        FROM plat p
        JOIN categorie_plat cp USING (id_categorie_plat)
        JOIN menu_plat mp USING (id_plat)
        JOIN menu m USING (id_menu)
        WHERE m.date_menu = CURRENT_DATE AND p.disponible
        ORDER BY cp.libelle, p.nom
    """)
    plats = cur.fetchall()
    if not plats:
        cur.execute("""
            SELECT p.id_plat, p.nom, p.prix_base, cp.libelle
            FROM plat p JOIN categorie_plat cp USING (id_categorie_plat)
            WHERE p.disponible ORDER BY cp.libelle, p.nom
        """)
        plats = cur.fetchall()
    return plats


@bp.route("/commandes/nouvelle", methods=["GET", "POST"])
@role_requis("SERVEUR")
def nouvelle_commande():
    conn = get_db()
    if request.method == "POST":
        matricule = request.form.get("matricule", "").strip()
        try:
            # Le formulaire envoie des champs "qte_<id_plat>" ; AUCUN prix n'est envoyé
            panier = {int(k[4:]): int(v) for k, v in request.form.items()
                      if k.startswith("qte_") and v.strip() and int(v) > 0}
            id_cmd, total = enregistrer_commande(conn, matricule, session["id_employe"], panier)
            flash(f"Commande n°{id_cmd} enregistrée : {int(total)} FCFA", "succes")
            return redirect(url_for("serveur.commandes_du_jour"))
        except ValueError:
            flash("Quantité invalide.", "erreur")
        except CommandeErreur as e:
            flash(str(e), "erreur")

    with conn.cursor() as cur:
        plats = _plats_du_jour(cur)
    return render_template("serveur/nouvelle_commande.html", plats=plats)


@bp.route("/commandes")
@role_requis("SERVEUR")
def commandes_du_jour():
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT c.id_commande, c.date_commande, cl.prenom || ' ' || cl.nom,
                   cl.code_categorie, c.montant_total, c.statut
            FROM commande c JOIN client cl USING (id_client)
            WHERE c.date_commande::date = CURRENT_DATE AND c.id_employe = %s
            ORDER BY c.date_commande DESC
        """, (session["id_employe"],))
        commandes = cur.fetchall()
    return render_template("serveur/commandes.html", commandes=commandes,
                           modes=MODES_PAIEMENT)


@bp.route("/commandes/<int:id_commande>/encaisser", methods=["POST"])
@role_requis("SERVEUR")
def encaisser(id_commande):
    try:
        montant = encaisser_commande(get_db(), id_commande, session["id_employe"],
                                     request.form.get("mode_paiement", ""))
        flash(f"Commande n°{id_commande} encaissée : {int(montant)} FCFA", "succes")
    except CommandeErreur as e:
        flash(str(e), "erreur")
    return redirect(url_for("serveur.commandes_du_jour"))


@bp.route("/commandes/<int:id_commande>/annuler", methods=["POST"])
@role_requis("SERVEUR")
def annuler(id_commande):
    try:
        annuler_commande(get_db(), id_commande)
        flash(f"Commande n°{id_commande} annulée.", "succes")
    except CommandeErreur as e:
        flash(str(e), "erreur")
    return redirect(url_for("serveur.commandes_du_jour"))
