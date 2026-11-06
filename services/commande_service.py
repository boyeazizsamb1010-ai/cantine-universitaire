"""Enregistrement et encaissement des commandes (accès base de données)."""
from decimal import Decimal

from services.tarification import calculer_commande

MODES_PAIEMENT = ("ESPECES", "WAVE", "ORANGE_MONEY", "CARTE")


class CommandeErreur(Exception):
    """Erreur métier affichable à l'utilisateur."""


def enregistrer_commande(conn, matricule_client: str, id_employe: int,
                         panier: dict[int, int]) -> tuple[int, Decimal]:
    """Crée la commande et ses lignes dans UNE transaction. Retourne (id_commande, total)."""
    with conn:                      # psycopg2 : COMMIT si succès, ROLLBACK si exception
        with conn.cursor() as cur:
            # 1. Retrouver le client et le taux de SA catégorie
            cur.execute("""
                SELECT c.id_client, c.actif, cc.taux_reduction
                FROM client c
                JOIN categorie_client cc USING (code_categorie)
                WHERE c.matricule = %s
            """, (matricule_client,))
            client = cur.fetchone()
            if client is None:
                raise CommandeErreur("Client introuvable.")
            id_client, actif, taux = client
            if not actif:
                raise CommandeErreur("Ce client est désactivé.")

            # 2. Charger les prix ACTUELS depuis la base (jamais depuis le formulaire !)
            cur.execute("""
                SELECT id_plat, nom, prix_base FROM plat
                WHERE id_plat = ANY(%s) AND disponible = TRUE
            """, (list(panier.keys()),))
            plats = {id_p: (nom, prix) for id_p, nom, prix in cur.fetchall()}

            # 3. Calculer (logique métier pure)
            try:
                lignes, total = calculer_commande(Decimal(taux), plats, panier)
            except ValueError as e:
                raise CommandeErreur(str(e)) from e

            # 4. Enregistrer la commande puis les lignes, avec les prix figés
            cur.execute("""
                INSERT INTO commande (id_client, id_employe, montant_total)
                VALUES (%s, %s, %s) RETURNING id_commande
            """, (id_client, id_employe, total))
            id_commande = cur.fetchone()[0]

            cur.executemany("""
                INSERT INTO ligne_commande (id_commande, id_plat, quantite,
                    prix_base_applique, taux_reduction_applique, prix_unitaire_applique)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [(id_commande, l.id_plat, l.quantite, l.prix_base,
                   l.taux_reduction, l.prix_unitaire) for l in lignes])

    return id_commande, total


def encaisser_commande(conn, id_commande: int, id_employe: int, mode_paiement: str) -> Decimal:
    """Enregistre le paiement d'une commande EN_COURS et la passe à PAYEE."""
    if mode_paiement not in MODES_PAIEMENT:
        raise CommandeErreur("Mode de paiement invalide.")
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT statut, montant_total FROM commande
                WHERE id_commande = %s FOR UPDATE
            """, (id_commande,))
            ligne = cur.fetchone()
            if ligne is None:
                raise CommandeErreur("Commande introuvable.")
            statut, montant = ligne
            if statut != "EN_COURS":
                raise CommandeErreur(f"Commande déjà {statut.lower()}.")

            cur.execute("""
                INSERT INTO encaissement (id_commande, montant, mode_paiement, id_employe)
                VALUES (%s, %s, %s, %s)
            """, (id_commande, montant, mode_paiement, id_employe))
            cur.execute("UPDATE commande SET statut = 'PAYEE' WHERE id_commande = %s",
                        (id_commande,))
    return montant


def annuler_commande(conn, id_commande: int) -> None:
    """Annule une commande non encore payée."""
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE commande SET statut = 'ANNULEE'
                WHERE id_commande = %s AND statut = 'EN_COURS'
            """, (id_commande,))
            if cur.rowcount == 0:
                raise CommandeErreur("Seule une commande en cours peut être annulée.")
