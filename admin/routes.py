from decimal import Decimal, InvalidOperation

import psycopg2
from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth.decorators import role_requis
from db import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------- Historique des commandes et encaissements ----------------
@bp.route("/historique")
@role_requis("ADMIN")
def historique():
    debut = request.args.get("debut") or None
    fin = request.args.get("fin") or None
    with get_db().cursor() as cur:
        cur.execute("""
            SELECT c.id_commande, c.date_commande,
                   cl.prenom || ' ' || cl.nom, cc.libelle,
                   e.prenom || ' ' || e.nom, c.montant_total, c.statut,
                   en.mode_paiement
            FROM commande c
            JOIN client cl           USING (id_client)
            JOIN categorie_client cc USING (code_categorie)
            JOIN employe e           ON e.id_employe = c.id_employe
            LEFT JOIN encaissement en ON en.id_commande = c.id_commande
            WHERE (%(debut)s::date IS NULL OR c.date_commande::date >= %(debut)s::date)
              AND (%(fin)s::date   IS NULL OR c.date_commande::date <= %(fin)s::date)
            ORDER BY c.date_commande DESC
            LIMIT 200
        """, {"debut": debut, "fin": fin})
        commandes = cur.fetchall()

        cur.execute("""
            SELECT COALESCE(SUM(montant), 0), COUNT(*)
            FROM encaissement en
            WHERE (%(debut)s::date IS NULL OR en.date_encaissement::date >= %(debut)s::date)
              AND (%(fin)s::date   IS NULL OR en.date_encaissement::date <= %(fin)s::date)
        """, {"debut": debut, "fin": fin})
        total_encaisse, nb_encaissements = cur.fetchone()

    return render_template("admin/historique.html", commandes=commandes,
                           total_encaisse=total_encaisse,
                           nb_encaissements=nb_encaissements,
                           debut=debut or "", fin=fin or "")


# ---------------- Gestion des plats ----------------
@bp.route("/plats", methods=["GET", "POST"])
@role_requis("ADMIN")
def plats():
    conn = get_db()
    if request.method == "POST":
        try:
            prix = Decimal(request.form["prix_base"])
            with conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO plat (nom, description, prix_base, id_categorie_plat)
                    VALUES (%s, %s, %s, %s)
                """, (request.form["nom"].strip(), request.form.get("description", ""),
                      prix, int(request.form["id_categorie_plat"])))
            flash("Plat ajouté.", "succes")
        except (InvalidOperation, ValueError):
            flash("Prix ou catégorie invalide.", "erreur")
        except psycopg2.IntegrityError:
            flash("Ce plat existe déjà ou le prix est invalide.", "erreur")
        return redirect(url_for("admin.plats"))

    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id_plat, p.nom, cp.libelle, p.prix_base, p.disponible
            FROM plat p JOIN categorie_plat cp USING (id_categorie_plat)
            ORDER BY cp.libelle, p.nom
        """)
        liste = cur.fetchall()
        cur.execute("SELECT id_categorie_plat, libelle FROM categorie_plat ORDER BY libelle")
        categories = cur.fetchall()
    return render_template("admin/plats.html", plats=liste, categories=categories)


@bp.route("/plats/<int:id_plat>/basculer", methods=["POST"])
@role_requis("ADMIN")
def basculer_disponibilite(id_plat):
    conn = get_db()
    with conn, conn.cursor() as cur:
        cur.execute("UPDATE plat SET disponible = NOT disponible WHERE id_plat = %s", (id_plat,))
    return redirect(url_for("admin.plats"))


@bp.route("/plats/<int:id_plat>/prix", methods=["POST"])
@role_requis("ADMIN")
def modifier_prix(id_plat):
    conn = get_db()
    try:
        prix = Decimal(request.form["prix_base"])
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE plat SET prix_base = %s WHERE id_plat = %s", (prix, id_plat))
        flash("Prix mis à jour (l'historique des commandes n'est pas modifié).", "succes")
    except (InvalidOperation, psycopg2.IntegrityError):
        flash("Prix invalide.", "erreur")
    return redirect(url_for("admin.plats"))


# ---------------- Clients ----------------
@bp.route("/clients", methods=["GET", "POST"])
@role_requis("ADMIN")
def clients():
    conn = get_db()
    if request.method == "POST":
        try:
            with conn, conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO client (matricule, nom, prenom, email, telephone, code_categorie)
                    VALUES (%s, %s, %s, NULLIF(%s, ''), NULLIF(%s, ''), %s)
                """, (request.form["matricule"].strip(), request.form["nom"].strip(),
                      request.form["prenom"].strip(), request.form.get("email", "").strip(),
                      request.form.get("telephone", "").strip(), request.form["code_categorie"]))
            flash("Client ajouté.", "succes")
        except psycopg2.IntegrityError:
            flash("Matricule ou email déjà utilisé.", "erreur")
        return redirect(url_for("admin.clients"))

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.matricule, c.prenom || ' ' || c.nom, cc.libelle, cc.taux_reduction, c.actif
            FROM client c JOIN categorie_client cc USING (code_categorie)
            ORDER BY c.nom, c.prenom
        """)
        liste = cur.fetchall()
        cur.execute("SELECT code_categorie, libelle FROM categorie_client ORDER BY libelle")
        categories = cur.fetchall()
    return render_template("admin/clients.html", clients=liste, categories=categories)


# ---------------- Stocks ----------------
@bp.route("/stocks", methods=["GET", "POST"])
@role_requis("ADMIN")
def stocks():
    conn = get_db()
    if request.method == "POST":
        try:
            ajout = Decimal(request.form["quantite"])
            with conn, conn.cursor() as cur:
                cur.execute("""
                    UPDATE ingredient SET quantite_stock = quantite_stock + %s
                    WHERE id_ingredient = %s
                """, (ajout, int(request.form["id_ingredient"])))
            flash("Stock mis à jour.", "succes")
        except (InvalidOperation, ValueError, psycopg2.IntegrityError):
            flash("Quantité invalide (le stock ne peut pas devenir négatif).", "erreur")
        return redirect(url_for("admin.stocks"))

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id_ingredient, libelle, unite, quantite_stock, seuil_alerte,
                   quantite_stock < seuil_alerte AS en_alerte
            FROM ingredient ORDER BY en_alerte DESC, libelle
        """)
        ingredients = cur.fetchall()
    return render_template("admin/stocks.html", ingredients=ingredients)
