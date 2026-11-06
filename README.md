# Gestion de cantine universitaire

Projet de groupe (3 étudiants) : modélisation MERISE, base PostgreSQL avec rôles sécurisés, application web Flask.

## Contenu du dossier

```
cantine/
├── docs/01_merise.md          # Dictionnaire des données, MCD, MLD
├── sql/
│   ├── 01_roles_et_base.sql   # Rôles SQL + création de la base (superutilisateur)
│   ├── 02_tables.sql          # Création des tables
│   ├── 03_droits.sql          # Privilèges par rôle
│   └── 04_donnees_test.sql    # Jeu de données de test
├── app.py                     # Point d'entrée Flask
├── config.py                  # Configuration (variables d'environnement)
├── db.py                      # Connexion PostgreSQL selon le rôle connecté
├── auth/                      # Connexion / déconnexion, décorateur de rôle
├── serveur/                   # Prise de commande, encaissement
├── admin/                     # Plats, clients, historique, stocks
├── services/
│   ├── tarification.py        # ★ Calcul du prix (étudiant / personnel)
│   └── commande_service.py    # Enregistrement transactionnel d'une commande
├── templates/                 # Pages HTML (Jinja)
├── static/                    # CSS et JavaScript
├── outils/definir_mot_de_passe.py  # Génère les hash des mots de passe employés
└── tests/test_tarification.py # Tests unitaires (pytest)
```

## Installation

### 1. Base de données (PostgreSQL 14+)

**Avec pgAdmin :**
1. Clic droit sur **Databases** → **Create** → **Database…** → nom : `cantine_db` → Save.
2. Clic droit sur **cantine_db** → **Query Tool**.
3. Dans ce Query Tool, ouvrir et exécuter (F5) dans l'ordre : `01_roles_et_base.sql`, `02_tables.sql`, `03_droits.sql`, `04_donnees_test.sql`.

**Avec psql (ligne de commande) :**

```bash
psql -U postgres -c "CREATE DATABASE cantine_db ENCODING 'UTF8'"
psql -U postgres -d cantine_db -f sql/01_roles_et_base.sql
psql -U postgres -d cantine_db -f sql/02_tables.sql
psql -U postgres -d cantine_db -f sql/03_droits.sql
psql -U postgres -d cantine_db -f sql/04_donnees_test.sql
```

Les rôles SQL sont tous préfixés `cantine_` pour ne pas entrer en conflit avec ceux d'autres projets sur le même serveur.

⚠️ Changez les mots de passe de `01_roles_et_base.sql` avant toute utilisation réelle.

### 2. Application

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # puis adaptez les mots de passe
```

### 3. Mots de passe des employés

Les employés de test ont un hash factice. Définissez un vrai mot de passe :

```bash
python outils/definir_mot_de_passe.py serveur1 MonMotDePasse
python outils/definir_mot_de_passe.py admin MonMotDePasseAdmin
```

### 4. Lancer

```bash
flask --app app run --debug
```

Ouvrez http://127.0.0.1:5000 et connectez-vous avec `serveur1` ou `admin`.

### 5. Tests

```bash
pytest
```

## Principe de sécurité

L'application se connecte à PostgreSQL avec le compte SQL qui correspond au rôle de l'employé connecté :

| Employé connecté | Compte SQL utilisé | Droits |
|---|---|---|
| (écran de connexion) | `cantine_app_auth` | Lecture des identifiants employés uniquement |
| Serveur | `cantine_app_serveur` | Lire le menu et les clients, créer des commandes et encaissements |
| Admin | `cantine_app_admin` | Gérer toutes les données (pas la structure) |

Même si le code Python avait une faille, la base refuserait qu'un serveur modifie un prix.

## Répartition du travail

| Membre | Responsabilité | Fichiers |
|---|---|---|
| Membre 1 — Base de données | MERISE, SQL, rôles, requêtes d'historique | `docs/`, `sql/`, `db.py` |
| Membre 2 — Backend métier | Tarification, commandes, authentification, tests | `services/`, `auth/`, `serveur/`, `tests/` |
| Membre 3 — Interface et admin | Pages HTML/CSS/JS, écrans admin | `templates/`, `static/`, `admin/` |

Travaillez avec Git : une branche par fonctionnalité, et une relecture par un autre membre avant chaque fusion.
