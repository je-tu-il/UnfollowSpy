# 👻 UnfollowSpy (GhostTrack) — Instagram Analyzer

[![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux%20%7C%20macOS-blue.svg)](https://github.com/je-tu-il/UnfollowSpy/releases)
[![Release](https://img.shields.io/github/v/release/je-tu-il/UnfollowSpy?color=success&include_prereleases)](https://github.com/je-tu-il/UnfollowSpy/releases/latest)
[![Privacy 100%](https://img.shields.io/badge/Security-100%25%20Offline%20%26%20Private-brightgreen.svg)](README.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Analysez vos abonnements et abonnés Instagram **sans jamais renseigner votre mot de passe**.  
> Découvrez instantanément qui ne vous suit pas en retour et qui vous ne suivez pas, avec gestion de Whitelist (célébrités / marques), recherche en direct et export CSV.

---

## ⚡ Téléchargement 1-Clic (Sans Python)

Exécutables autonomes prêts à l'emploi :

👉 **[Télécharger la dernière version (Windows, Linux, macOS)](https://github.com/je-tu-il/UnfollowSpy/releases/latest)**

| Plateforme | Fichier à télécharger |
| :--- | :--- |
| **Windows (x64)** | `UnfollowSpy-windows-x64.exe` (exécutable direct) |
| **Linux (x64)** | `UnfollowSpy-linux-x64` |
| **macOS** | `UnfollowSpy-macos` |

---

## 🔒 100% Sécurisé & Sans Risque de Ban

Contrairement aux applications tierces douteuses :
- ❌ **Aucun identifiant ni mot de passe demandé.**
- ❌ **Aucune requête réseau vers Instagram (aucun risque de blocage ou shadowban).**
- ✅ **Traitement 100% local sur votre machine** à partir de votre archive officielle Instagram.

---

## 📖 Guide Débutant : Comment récupérer ses fichiers Instagram ?

1. Sur Instagram (application mobile ou web), allez dans **Paramètres** ⚙️.
2. Cliquez sur **Espace Comptes** > **Vos informations et autorisations**.
3. Sélectionnez **Télécharger vos informations** > **Télécharger ou transférer des informations**.
4. Choisissez votre compte, puis sélectionnez **Certaines de vos informations**.
5. Cochez uniquement **Abonnés et abonnements**.
6. Choisissez le format (**JSON** ou **HTML** — les deux sont supportés) et lancez la demande.
7. Une fois l'archive reçue et décompressée, ouvrez **UnfollowSpy** et sélectionnez :
   - Fichier Followers : `followers_1.json` (ou `.html`)
   - Fichier Following : `following.json` (ou `.html`)
8. Cliquez sur **🚀 LANCER L'ANALYSE COMPLÈTE** !

---

## ✨ Fonctionnalités Clés

- 🕵️ **Double Onglet d'Analyse** :
  - *Ils ne me suivent pas* : comptes que vous suivez mais qui ne vous suivent pas.
  - *Je ne suis pas en retour* : personnes abonnées à votre compte que vous ne suivez pas.
- 🛡️ **Système de Whitelist Intelligent** :
  - Ignorez vos créateurs, célébrités ou comptes d'actualité favoris pour ne pas polluer votre liste.
  - Sauvegarde automatique dans `whitelist.txt`.
- 🖱️ **Actions Clic Droit** :
  - Ouvrir directement le profil Instagram dans le navigateur.
  - Copier le pseudo en 1 clic.
  - Ajouter à la Whitelist instantanément.
- 🔍 **Recherche et Filtrage en Temps Réel** : Trouvez un compte en tapant les premières lettres.
- 💾 **Exportation CSV** : Exportez la liste filtrée pour archivage ou suivi tableur.
- 🌙 **Interface Sombre Moderne** : Thème sombre natif avec `sv-ttk`.

---

## 🛠️ Lancement pour Développeurs (Code Source)

```bash
git clone https://github.com/je-tu-il/UnfollowSpy.git
cd UnfollowSpy
pip install -r requirements.txt
python main.py
```

---

## 📄 Licence

Ce projet est distribué sous licence MIT. Libre d'utilisation et d'adaptation.
