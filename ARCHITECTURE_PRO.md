# Architecture

UnfollowSpy est un site statique. `index.html` contient l’interface, `styles.css` le rendu responsive et `app.js` l’import, la comparaison et le rendu des résultats.

Les listes sont lues avec l’API File et restent en mémoire le temps de la session. Les exclusions sont enregistrées dans le stockage local du navigateur. L’export CSV est généré à la demande à partir de la liste active.
