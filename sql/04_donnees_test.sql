-- ============================================================
-- 04_donnees_test.sql
-- psql -U postgres -d cantine_db -f sql/04_donnees_test.sql
-- ============================================================

INSERT INTO categorie_client (code_categorie, libelle, taux_reduction) VALUES
    ('ETU',  'Étudiant',                   0.30),
    ('PERS', 'Personnel de l''université', 0.00);

INSERT INTO categorie_plat (libelle) VALUES
    ('Entrée'), ('Plat principal'), ('Dessert'), ('Boisson');

INSERT INTO plat (nom, description, prix_base, id_categorie_plat) VALUES
    ('Thiéboudienne',   'Riz au poisson et légumes',     1000, 2),
    ('Yassa poulet',    'Poulet mariné aux oignons',     1000, 2),
    ('Mafé',            'Sauce arachide, viande, riz',    900, 2),
    ('Salade composée', 'Salade, tomate, œuf',            500, 1),
    ('Thiakry',         'Dessert au mil et lait caillé',  400, 3),
    ('Jus de bissap',   'Jus d''hibiscus maison',         300, 4),
    ('Eau minérale',    'Bouteille 50 cl',                200, 4);

INSERT INTO client (matricule, nom, prenom, email, telephone, code_categorie) VALUES
    ('ETU2026001', 'Diop',   'Awa',     'awa.diop@etu.univ.sn',   '770000001', 'ETU'),
    ('PERS0042',   'Ndiaye', 'Mamadou', 'mamadou.ndiaye@univ.sn', '770000002', 'PERS');

-- Hash factices : définissez les vrais avec
--   python outils/definir_mot_de_passe.py <login> <mot_de_passe>
INSERT INTO employe (login, mot_de_passe_hash, nom, prenom, role) VALUES
    ('admin',    'HASH_A_GENERER', 'Sarr', 'Fatou',    'ADMIN'),
    ('serveur1', 'HASH_A_GENERER', 'Fall', 'Ibrahima', 'SERVEUR'),
    ('serveur2', 'HASH_A_GENERER', 'Ba',   'Khady',    'SERVEUR');

INSERT INTO menu (date_menu, type_repas) VALUES (CURRENT_DATE, 'DEJEUNER');
INSERT INTO menu_plat (id_menu, id_plat, quantite_prevue) VALUES
    (1, 1, 150), (1, 2, 100), (1, 4, 50), (1, 5, 80), (1, 6, 200), (1, 7, 200);

INSERT INTO ingredient (libelle, unite, quantite_stock, seuil_alerte) VALUES
    ('Riz brisé', 'kg', 250, 50),
    ('Poisson',   'kg',  80, 20),
    ('Poulet',    'kg',  60, 15),
    ('Oignon',    'kg',  40, 10);

INSERT INTO plat_ingredient (id_plat, id_ingredient, quantite_necessaire) VALUES
    (1, 1, 0.150), (1, 2, 0.120),                  -- Thiéboudienne
    (2, 1, 0.150), (2, 3, 0.150), (2, 4, 0.080);   -- Yassa poulet

-- Commande test : l'étudiante Awa prend 1 Thiéboudienne + 1 bissap, saisie par serveur1
-- 1000 × 0,70 = 700 ; 300 × 0,70 = 210 → total 910 FCFA
INSERT INTO commande (id_client, id_employe, montant_total, statut) VALUES (1, 2, 910, 'PAYEE');
INSERT INTO ligne_commande
    (id_commande, id_plat, quantite, prix_base_applique, taux_reduction_applique, prix_unitaire_applique)
VALUES
    (1, 1, 1, 1000, 0.30, 700),
    (1, 6, 1,  300, 0.30, 210);
INSERT INTO encaissement (id_commande, montant, mode_paiement, id_employe)
       VALUES (1, 910, 'WAVE', 2);

-- ---------- Requête de vérification de l'historique ----------
SELECT c.id_commande, c.date_commande,
       cl.prenom || ' ' || cl.nom AS client,
       cc.libelle                 AS categorie,
       e.prenom                   AS serveur,
       c.montant_total, c.statut
FROM commande c
JOIN client cl           USING (id_client)
JOIN categorie_client cc USING (code_categorie)
JOIN employe e           USING (id_employe)
ORDER BY c.date_commande DESC;
