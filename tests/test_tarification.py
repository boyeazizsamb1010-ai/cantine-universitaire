from decimal import Decimal

import pytest

from services.tarification import calculer_commande

PLATS = {
    1: ("Thiéboudienne", Decimal("1000")),
    3: ("Mafé", Decimal("900")),
    6: ("Jus de bissap", Decimal("300")),
}
ETUDIANT = Decimal("0.30")
PERSONNEL = Decimal("0.00")


def test_etudiant_beneficie_de_la_reduction():
    _, total = calculer_commande(ETUDIANT, PLATS, {1: 1, 6: 1})
    assert total == Decimal("910")          # 700 + 210


def test_personnel_paie_plein_tarif():
    _, total = calculer_commande(PERSONNEL, PLATS, {1: 2})
    assert total == Decimal("2000")


def test_prix_unitaire_et_quantites():
    lignes, total = calculer_commande(ETUDIANT, PLATS, {3: 3})
    assert lignes[0].prix_unitaire == Decimal("630")   # 900 × 0,70
    assert total == Decimal("1890")


def test_arrondi_au_franc():
    plats = {9: ("Café", Decimal("125"))}
    lignes, _ = calculer_commande(ETUDIANT, plats, {9: 1})
    assert lignes[0].prix_unitaire == Decimal("88")    # 87,5 arrondi à 88


def test_plat_inconnu_refuse():
    with pytest.raises(ValueError):
        calculer_commande(ETUDIANT, PLATS, {99: 1})


def test_panier_vide_refuse():
    with pytest.raises(ValueError):
        calculer_commande(ETUDIANT, PLATS, {})


def test_quantite_negative_refusee():
    with pytest.raises(ValueError):
        calculer_commande(ETUDIANT, PLATS, {1: -2})


def test_taux_invalide_refuse():
    with pytest.raises(ValueError):
        calculer_commande(Decimal("1.5"), PLATS, {1: 1})
