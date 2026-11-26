# UnfollowSpy

Comparez vos abonnés et vos abonnements Instagram dans le navigateur.

1. Lancez `Lancer_Projet.bat` sous Windows ou ouvrez `index.html` dans votre navigateur.
2. Décompressez votre export Instagram et ouvrez le dossier extrait avec **Ouvrir le dossier Instagram**. Les listes sont détectées automatiquement. Vous pouvez aussi choisir les fichiers dans les deux champs manuels.
3. Cliquez sur **Comparer les listes**. Vous pouvez rechercher un pseudo, ouvrir son profil, le copier, l’ignorer ou exporter la liste active en CSV.

Les fichiers sont lus dans le navigateur sans envoi vers un serveur. Les résultats décrivent l’état de l’export à sa date de création. Les pseudos ignorés sont mémorisés par le navigateur. Si vous avez conservé `whitelist.txt` de l’ancienne version, importez-le depuis **Pseudos ignorés**.

## Hébergement

Copiez `index.html`, `styles.css` et `app.js` sur un hébergement statique.

## Vérification

Avec Node.js 22, lancez `run_tests.bat` ou `node tests/core.mjs` pour vérifier la lecture des exports. Le test de bout en bout utilise Chrome en mode headless dans GitHub Actions :

```powershell
node tests/browser.mjs /usr/bin/google-chrome
```

Le script accepte également le chemin d’un exécutable Chrome ou Chromium.
