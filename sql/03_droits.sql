-- ============================================================
-- 03_droits.sql
-- psql -U postgres -d cantine_db -f sql/03_droits.sql
-- ============================================================

-- Personne n'a de droits par défaut
REVOKE ALL ON DATABASE cantine_db FROM PUBLIC;
GRANT CONNECT ON DATABASE cantine_db TO cantine_lecture, cantine_serveur, cantine_admin, cantine_app_auth;
GRANT USAGE   ON SCHEMA public       TO cantine_lecture, cantine_serveur, cantine_admin, cantine_app_auth;

-- ---------- APP_AUTH : uniquement pour vérifier un login ----------
GRANT SELECT (id_employe, login, mot_de_passe_hash, nom, prenom, role, actif)
      ON employe TO cantine_app_auth;

-- ---------- ROLE_LECTURE : consultation uniquement ----------
GRANT SELECT ON categorie_client, categorie_plat, plat, menu, menu_plat,
                commande, ligne_commande, encaissement
             TO cantine_lecture;

-- ---------- ROLE_SERVEUR : hérite de cantine_lecture + ----------
GRANT SELECT ON client TO cantine_serveur;                -- retrouver le client par matricule
GRANT SELECT (id_employe, nom, prenom, role)           -- PAS de mot_de_passe_hash !
      ON employe TO cantine_serveur;

GRANT INSERT ON commande, ligne_commande, encaissement TO cantine_serveur;
GRANT UPDATE (statut, montant_total) ON commande TO cantine_serveur;   -- seulement ces colonnes
GRANT DELETE ON ligne_commande TO cantine_serveur;        -- retirer un plat d'une commande en cours

GRANT USAGE, SELECT ON SEQUENCE commande_id_commande_seq,
                                encaissement_id_encaissement_seq
                    TO cantine_serveur;
-- Le serveur ne peut PAS : modifier un prix, créer un plat, supprimer une commande,
-- toucher aux stocks, ni lire les mots de passe.

-- ---------- ROLE_ADMIN : gestion complète des données ----------
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA public TO cantine_admin;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO cantine_admin;
-- L'admin gère les données mais ne peut pas modifier la STRUCTURE (DROP, ALTER) :
-- seul cantine_owner (les 3 développeurs) le peut.

-- Les futures tables créées par cantine_owner donneront aussi les droits à l'admin
ALTER DEFAULT PRIVILEGES FOR ROLE cantine_owner IN SCHEMA public
      GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cantine_admin;
ALTER DEFAULT PRIVILEGES FOR ROLE cantine_owner IN SCHEMA public
      GRANT USAGE, SELECT ON SEQUENCES TO cantine_admin;

-- ============================================================
-- Matrice des droits
-- Table                     | lecture | serveur                           | admin
-- plat, menu, catégories    | SELECT  | SELECT                            | CRUD
-- client                    | -       | SELECT                            | CRUD
-- employe                   | -       | SELECT (4 colonnes)               | CRUD
-- commande                  | SELECT  | SELECT, INSERT, UPDATE(statut,total) | CRUD
-- ligne_commande            | SELECT  | SELECT, INSERT, DELETE            | CRUD
-- encaissement              | SELECT  | SELECT, INSERT                    | CRUD
-- ingredient, plat_ingredient | -     | -                                 | CRUD
-- ============================================================
