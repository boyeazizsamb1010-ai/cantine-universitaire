"""Calcul du prix d'une commande selon la catégorie du client.

Logique métier PURE : aucune dépendance à Flask ni à la base de données,
ce qui la rend simple à tester (voir tests/test_tarification.py).
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

ARRONDI_FCFA = Decimal("1")  # le FCFA n'a pas de centimes


@dataclass(frozen=True)
class LigneTarifee:
    id_plat: int
    nom: str
    quantite: int
    prix_base: Decimal
    taux_reduction: Decimal

    @property
    def prix_unitaire(self) -> Decimal:
        """Prix après réduction, arrondi au franc."""
        prix = self.prix_base * (Decimal("1") - self.taux_reduction)
        return prix.quantize(ARRONDI_FCFA, rounding=ROUND_HALF_UP)

    @property
    def sous_total(self) -> Decimal:
        return self.prix_unitaire * self.quantite


def calculer_commande(taux_reduction: Decimal,
                      plats: dict[int, tuple[str, Decimal]],
                      panier: dict[int, int]) -> tuple[list[LigneTarifee], Decimal]:
    """
    taux_reduction : taux de la catégorie du client (0.30 étudiant, 0.00 personnel)
    plats          : {id_plat: (nom, prix_base)} pour les plats disponibles
    panier         : {id_plat: quantite} saisi par le serveur
    Retourne (liste des lignes tarifées, total).
    """
    if not panier:
        raise ValueError("La commande doit contenir au moins un plat.")
    taux_reduction = Decimal(taux_reduction)
    if not (Decimal("0") <= taux_reduction <= Decimal("1")):
        raise ValueError("Taux de réduction invalide.")

    lignes = []
    for id_plat, quantite in panier.items():
        if quantite <= 0:
            raise ValueError(f"Quantité invalide pour le plat {id_plat}.")
        if id_plat not in plats:
            raise ValueError(f"Le plat {id_plat} n'existe pas ou n'est pas disponible.")
        nom, prix_base = plats[id_plat]
        lignes.append(LigneTarifee(id_plat, nom, quantite, Decimal(prix_base), taux_reduction))

    total = sum((ligne.sous_total for ligne in lignes), Decimal("0"))
    return lignes, total
