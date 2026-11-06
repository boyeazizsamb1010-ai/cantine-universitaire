-- ============================================================
-- 01_roles_et_base.sql
-- PRÉREQUIS : créer d'abord la base vide cantine_db
--   pgAdmin : clic droit sur Databases > Create > Database... > nom : cantine_db
--   (ou en SQL, seul, sur la base postgres : CREATE DATABASE cantine_db;)
-- Puis exécuter CE script dans un Query Tool ouvert sur cantine_db.
-- Les rôles sont préfixés « cantine_ » pour ne pas entrer en conflit
-- avec les rôles d'autres projets sur le même serveur PostgreSQL.
-- ⚠️ Changez tous les mots de passe avant une utilisation réelle.
-- ============================================================

-- 1. RÔLES DE GROUPE (NOLOGIN) : ils portent les droits
CREATE ROLE cantine_owner NOLOGIN;   -- propriétaire du schéma (structure)
CREATE ROLE cantine_lecture  NOLOGIN;   -- consultation / statistiques
CREATE ROLE cantine_serveur  NOLOGIN;   -- prise de commande et encaissement
CREATE ROLE cantine_admin    NOLOGIN;   -- gestion complète des données

-- Le serveur hérite des droits de lecture
GRANT cantine_lecture TO cantine_serveur;

-- 2. COMPTES DE CONNEXION (LOGIN)
-- Les 3 membres du groupe : droits de développement (création / modification des tables)
CREATE ROLE cantine_dev1 LOGIN PASSWORD 'ChangeMoi_1!' IN ROLE cantine_owner;
CREATE ROLE cantine_dev2 LOGIN PASSWORD 'ChangeMoi_2!' IN ROLE cantine_owner;
CREATE ROLE cantine_dev3 LOGIN PASSWORD 'ChangeMoi_3!' IN ROLE cantine_owner;

-- Comptes utilisés par l'application
CREATE ROLE cantine_app_auth    LOGIN PASSWORD 'Auth_Cantine_2026!';                       -- écran de connexion
CREATE ROLE cantine_app_serveur LOGIN PASSWORD 'Serveur_Cantine_2026!' IN ROLE cantine_serveur;
CREATE ROLE cantine_app_admin   LOGIN PASSWORD 'Admin_Cantine_2026!'   IN ROLE cantine_admin;
CREATE ROLE cantine_app_rapport LOGIN PASSWORD 'Rapport_Cantine_2026!' IN ROLE cantine_lecture;

-- 3. PROPRIÉTAIRE DE LA BASE (créée au préalable, voir en-tête)
ALTER DATABASE cantine_db OWNER TO cantine_owner;
