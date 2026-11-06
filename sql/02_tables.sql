-- ============================================================
-- 02_tables.sql
-- psql -U postgres -d cantine_db -f sql/02_tables.sql
-- ============================================================

-- Depuis PostgreSQL 15, le schéma public n'est plus ouvert à tous
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO cantine_owner;
SET ROLE cantine_owner;   -- les tables appartiendront à cantine_owner

-- ---------- Clients et tarification ----------
CREATE TABLE categorie_client (
    code_categorie  VARCHAR(10)  PRIMARY KEY,
    libelle         VARCHAR(50)  NOT NULL UNIQUE,
    taux_reduction  NUMERIC(4,2) NOT NULL DEFAULT 0
                    CHECK (taux_reduction >= 0 AND taux_reduction <= 1)
);

CREATE TABLE client (
    id_client        SERIAL       PRIMARY KEY,
    matricule        VARCHAR(20)  NOT NULL UNIQUE,
    nom              VARCHAR(50)  NOT NULL,
    prenom           VARCHAR(50)  NOT NULL,
    email            VARCHAR(100) UNIQUE,
    telephone        VARCHAR(20),
    actif            BOOLEAN      NOT NULL DEFAULT TRUE,
    date_inscription DATE         NOT NULL DEFAULT CURRENT_DATE,
    code_categorie   VARCHAR(10)  NOT NULL
                     REFERENCES categorie_client(code_categorie)
                     ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- Employés (serveurs, admins) ----------
CREATE TABLE employe (
    id_employe        SERIAL       PRIMARY KEY,
    login             VARCHAR(30)  NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    nom               VARCHAR(50)  NOT NULL,
    prenom            VARCHAR(50)  NOT NULL,
    role              VARCHAR(10)  NOT NULL CHECK (role IN ('SERVEUR', 'ADMIN')),
    actif             BOOLEAN      NOT NULL DEFAULT TRUE
);

-- ---------- Menu et plats ----------
CREATE TABLE categorie_plat (
    id_categorie_plat SERIAL      PRIMARY KEY,
    libelle           VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE plat (
    id_plat           SERIAL        PRIMARY KEY,
    nom               VARCHAR(100)  NOT NULL UNIQUE,
    description       TEXT,
    prix_base         NUMERIC(10,2) NOT NULL CHECK (prix_base > 0),
    disponible        BOOLEAN       NOT NULL DEFAULT TRUE,
    id_categorie_plat INT           NOT NULL
                      REFERENCES categorie_plat(id_categorie_plat) ON DELETE RESTRICT
);

CREATE TABLE menu (
    id_menu    SERIAL      PRIMARY KEY,
    date_menu  DATE        NOT NULL,
    type_repas VARCHAR(15) NOT NULL
               CHECK (type_repas IN ('PETIT_DEJEUNER', 'DEJEUNER', 'DINER')),
    UNIQUE (date_menu, type_repas)
);

CREATE TABLE menu_plat (
    id_menu         INT NOT NULL REFERENCES menu(id_menu) ON DELETE CASCADE,
    id_plat         INT NOT NULL REFERENCES plat(id_plat) ON DELETE RESTRICT,
    quantite_prevue INT NOT NULL DEFAULT 0 CHECK (quantite_prevue >= 0),
    PRIMARY KEY (id_menu, id_plat)
);

-- ---------- Stocks ----------
CREATE TABLE ingredient (
    id_ingredient  SERIAL        PRIMARY KEY,
    libelle        VARCHAR(100)  NOT NULL UNIQUE,
    unite          VARCHAR(10)   NOT NULL,
    quantite_stock NUMERIC(10,3) NOT NULL DEFAULT 0 CHECK (quantite_stock >= 0),
    seuil_alerte   NUMERIC(10,3) NOT NULL DEFAULT 0 CHECK (seuil_alerte >= 0)
);

CREATE TABLE plat_ingredient (
    id_plat             INT           NOT NULL REFERENCES plat(id_plat) ON DELETE CASCADE,
    id_ingredient       INT           NOT NULL REFERENCES ingredient(id_ingredient) ON DELETE RESTRICT,
    quantite_necessaire NUMERIC(10,3) NOT NULL CHECK (quantite_necessaire > 0),
    PRIMARY KEY (id_plat, id_ingredient)
);

-- ---------- Commandes et encaissements ----------
CREATE TABLE commande (
    id_commande   SERIAL        PRIMARY KEY,
    date_commande TIMESTAMP     NOT NULL DEFAULT NOW(),
    statut        VARCHAR(10)   NOT NULL DEFAULT 'EN_COURS'
                  CHECK (statut IN ('EN_COURS', 'PAYEE', 'ANNULEE')),
    montant_total NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (montant_total >= 0),
    id_client     INT NOT NULL REFERENCES client(id_client)   ON DELETE RESTRICT,
    id_employe    INT NOT NULL REFERENCES employe(id_employe) ON DELETE RESTRICT
);

CREATE TABLE ligne_commande (
    id_commande             INT           NOT NULL REFERENCES commande(id_commande) ON DELETE CASCADE,
    id_plat                 INT           NOT NULL REFERENCES plat(id_plat) ON DELETE RESTRICT,
    quantite                INT           NOT NULL CHECK (quantite > 0),
    prix_base_applique      NUMERIC(10,2) NOT NULL CHECK (prix_base_applique > 0),
    taux_reduction_applique NUMERIC(4,2)  NOT NULL CHECK (taux_reduction_applique BETWEEN 0 AND 1),
    prix_unitaire_applique  NUMERIC(10,2) NOT NULL CHECK (prix_unitaire_applique >= 0),
    PRIMARY KEY (id_commande, id_plat)
);

CREATE TABLE encaissement (
    id_encaissement   SERIAL        PRIMARY KEY,
    id_commande       INT           NOT NULL UNIQUE      -- (0,1) : un seul encaissement par commande
                      REFERENCES commande(id_commande) ON DELETE RESTRICT,
    montant           NUMERIC(10,2) NOT NULL CHECK (montant > 0),
    mode_paiement     VARCHAR(15)   NOT NULL
                      CHECK (mode_paiement IN ('ESPECES', 'WAVE', 'ORANGE_MONEY', 'CARTE')),
    date_encaissement TIMESTAMP     NOT NULL DEFAULT NOW(),
    id_employe        INT           NOT NULL REFERENCES employe(id_employe) ON DELETE RESTRICT
);

-- Index pour l'historique et les recherches fréquentes
CREATE INDEX idx_commande_date   ON commande(date_commande);
CREATE INDEX idx_commande_client ON commande(id_client);
CREATE INDEX idx_client_nom      ON client(nom, prenom);

RESET ROLE;
