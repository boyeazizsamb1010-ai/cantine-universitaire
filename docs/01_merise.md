# Modélisation MERISE — Gestion de cantine universitaire

## Règles de gestion

- RG1 : Un client est soit étudiant, soit membre du personnel. Il appartient à une seule catégorie.
- RG2 : Chaque catégorie de client a un taux de réduction (Étudiant : 30 %, Personnel : 0 %).
- RG3 : Une commande concerne un seul client et est saisie par un seul serveur.
- RG4 : Une commande contient au moins un plat, en une ou plusieurs quantités.
- RG5 : Le prix payé est figé au moment de la commande (prix de base et taux recopiés).
- RG6 : Une commande est réglée par au plus un encaissement.
- RG7 : Un menu (date + type de repas) propose au moins un plat.
- RG8 : Un plat est composé d'ingrédients, suivis en stock.
- RG9 : Seuls les administrateurs gèrent les plats, menus, clients, employés et stocks.

## 1. Dictionnaire des données

AN = alphanumérique, N = numérique.

| Code | Libellé | Type | Taille | Règle / Contrainte |
|---|---|---|---|---|
| code_categorie | Code catégorie client | AN | 10 | Identifiant (ETU, PERS) |
| libelle_categorie | Libellé catégorie client | AN | 50 | Unique, obligatoire |
| taux_reduction | Taux de réduction | N | 4,2 | Entre 0 et 1 (0.30 = 30 %) |
| id_client | Identifiant client | N | — | Auto-incrément |
| matricule | Matricule (carte étudiant / agent) | AN | 20 | Unique, obligatoire |
| nom_client, prenom_client | Nom, prénom du client | AN | 50 | Obligatoires |
| email_client | Email | AN | 100 | Unique |
| telephone_client | Téléphone | AN | 20 | — |
| actif_client | Client actif | Booléen | — | Défaut : vrai |
| date_inscription | Date d'inscription | Date | — | Défaut : date du jour |
| id_employe | Identifiant employé | N | — | Auto-incrément |
| login | Identifiant de connexion | AN | 30 | Unique, obligatoire |
| mot_de_passe_hash | Mot de passe chiffré | AN | 255 | Jamais en clair |
| nom_employe, prenom_employe | Nom, prénom de l'employé | AN | 50 | Obligatoires |
| role_employe | Rôle applicatif | AN | 10 | SERVEUR ou ADMIN |
| actif_employe | Employé actif | Booléen | — | Défaut : vrai |
| id_categorie_plat | Identifiant catégorie de plat | N | — | Auto-incrément |
| libelle_categorie_plat | Libellé (Entrée, Plat, Boisson…) | AN | 50 | Unique |
| id_plat | Identifiant plat | N | — | Auto-incrément |
| nom_plat | Nom du plat | AN | 100 | Unique |
| description_plat | Description | Texte | — | — |
| prix_base | Prix de base (tarif normal) | N | 10,2 | > 0, en FCFA |
| disponible | Plat disponible | Booléen | — | Défaut : vrai |
| id_menu | Identifiant menu | N | — | Auto-incrément |
| date_menu | Date du menu | Date | — | Obligatoire |
| type_repas | Type de repas | AN | 15 | PETIT_DEJEUNER, DEJEUNER, DINER |
| quantite_prevue | Portions prévues au menu | N | — | ≥ 0 |
| id_ingredient | Identifiant ingrédient | N | — | Auto-incrément |
| libelle_ingredient | Nom de l'ingrédient | AN | 100 | Unique |
| unite | Unité (kg, L, pièce) | AN | 10 | — |
| quantite_stock | Quantité en stock | N | 10,3 | ≥ 0 |
| seuil_alerte | Seuil de réapprovisionnement | N | 10,3 | ≥ 0 |
| quantite_necessaire | Quantité d'ingrédient par portion | N | 10,3 | > 0 |
| id_commande | Identifiant commande | N | — | Auto-incrément |
| date_commande | Date et heure de la commande | Date/heure | — | Défaut : maintenant |
| statut | Statut de la commande | AN | 10 | EN_COURS, PAYEE, ANNULEE |
| montant_total | Montant total de la commande | N | 10,2 | ≥ 0 |
| quantite | Quantité commandée d'un plat | N | — | > 0 |
| prix_base_applique | Prix de base au moment de la commande | N | 10,2 | Copie figée |
| taux_reduction_applique | Taux appliqué au moment de la commande | N | 4,2 | Copie figée |
| prix_unitaire_applique | Prix unitaire payé | N | 10,2 | Calculé |
| id_encaissement | Identifiant encaissement | N | — | Auto-incrément |
| montant_encaisse | Montant encaissé | N | 10,2 | > 0 |
| mode_paiement | Mode de paiement | AN | 15 | ESPECES, WAVE, ORANGE_MONEY, CARTE |
| date_encaissement | Date et heure de l'encaissement | Date/heure | — | Défaut : maintenant |

> **Pourquoi copier le prix dans la ligne de commande ?**
> Si on stockait seulement `id_plat`, l'historique deviendrait faux dès qu'un prix change. On fige donc le prix et le taux au moment de la vente : une facture ne change jamais après coup.

## 2. Modèle Conceptuel de Données (MCD)

### Entités

- **CATEGORIE_CLIENT** (<u>code_categorie</u>, libelle_categorie, taux_reduction)
- **CLIENT** (<u>id_client</u>, matricule, nom_client, prenom_client, email_client, telephone_client, actif_client, date_inscription)
- **EMPLOYE** (<u>id_employe</u>, login, mot_de_passe_hash, nom_employe, prenom_employe, role_employe, actif_employe)
- **CATEGORIE_PLAT** (<u>id_categorie_plat</u>, libelle_categorie_plat)
- **PLAT** (<u>id_plat</u>, nom_plat, description_plat, prix_base, disponible)
- **MENU** (<u>id_menu</u>, date_menu, type_repas)
- **INGREDIENT** (<u>id_ingredient</u>, libelle_ingredient, unite, quantite_stock, seuil_alerte)
- **COMMANDE** (<u>id_commande</u>, date_commande, statut, montant_total)
- **ENCAISSEMENT** (<u>id_encaissement</u>, montant_encaisse, mode_paiement, date_encaissement)

### Associations et cardinalités

| Association | Entité A | Card. A | Card. B | Entité B | Lecture |
|---|---|---|---|---|---|
| APPARTENIR | CLIENT | (1,1) | (0,n) | CATEGORIE_CLIENT | Un client appartient à une seule catégorie ; une catégorie regroupe 0 à n clients |
| CLASSER | PLAT | (1,1) | (0,n) | CATEGORIE_PLAT | Un plat est classé dans une seule catégorie |
| PASSER | COMMANDE | (1,1) | (0,n) | CLIENT | Une commande concerne un seul client ; un client passe 0 à n commandes |
| ENREGISTRER | COMMANDE | (1,1) | (0,n) | EMPLOYE | Une commande est saisie par un seul serveur |
| CONTENIR *(quantite, prix_base_applique, taux_reduction_applique, prix_unitaire_applique)* | COMMANDE | (1,n) | (0,n) | PLAT | Une commande contient au moins un plat ; un plat apparaît dans 0 à n commandes |
| REGLER | ENCAISSEMENT | (1,1) | (0,1) | COMMANDE | Un encaissement règle une seule commande ; une commande a 0 ou 1 encaissement |
| ENCAISSER | ENCAISSEMENT | (1,1) | (0,n) | EMPLOYE | Un encaissement est effectué par un seul employé |
| PROPOSER *(quantite_prevue)* | MENU | (1,n) | (0,n) | PLAT | Un menu propose au moins un plat |
| COMPOSER *(quantite_necessaire)* | PLAT | (0,n) | (0,n) | INGREDIENT | Un plat utilise 0 à n ingrédients |

> **Pourquoi pas un héritage ETUDIANT / PERSONNEL ?**
> Les deux sous-types ont exactement les mêmes attributs ; seul le tarif change. Une entité `CATEGORIE_CLIENT` est plus simple et plus évolutive : ajouter une catégorie « Invité » ne demande qu'un `INSERT`, sans toucher au code.
>
> Clients et employés sont séparés : les employés se connectent à l'application, les clients sont seulement identifiés par leur matricule.

## 3. Modèle Logique de Données (MLD)

Règles de passage appliquées :

- **Règle 1** : association (1,1)–(0,n) → la clé de l'entité côté (0,n) migre en clé étrangère dans l'entité côté (1,1).
- **Règle 2** : association (x,n)–(x,n) → nouvelle table ; clé primaire composée des deux clés étrangères ; elle porte les attributs de l'association.
- **Règle 3** : association (1,1)–(0,1) → clé étrangère **unique** côté (1,1).

Clé primaire soulignée, clé étrangère précédée de `#`.

- CATEGORIE_CLIENT (<u>code_categorie</u>, libelle, taux_reduction)
- CLIENT (<u>id_client</u>, matricule, nom, prenom, email, telephone, actif, date_inscription, #code_categorie)
- EMPLOYE (<u>id_employe</u>, login, mot_de_passe_hash, nom, prenom, role, actif)
- CATEGORIE_PLAT (<u>id_categorie_plat</u>, libelle)
- PLAT (<u>id_plat</u>, nom, description, prix_base, disponible, #id_categorie_plat)
- MENU (<u>id_menu</u>, date_menu, type_repas)
- MENU_PLAT (<u>#id_menu, #id_plat</u>, quantite_prevue)
- INGREDIENT (<u>id_ingredient</u>, libelle, unite, quantite_stock, seuil_alerte)
- PLAT_INGREDIENT (<u>#id_plat, #id_ingredient</u>, quantite_necessaire)
- COMMANDE (<u>id_commande</u>, date_commande, statut, montant_total, #id_client, #id_employe)
- LIGNE_COMMANDE (<u>#id_commande, #id_plat</u>, quantite, prix_base_applique, taux_reduction_applique, prix_unitaire_applique)
- ENCAISSEMENT (<u>id_encaissement</u>, #id_commande (unique), montant, mode_paiement, date_encaissement, #id_employe)
