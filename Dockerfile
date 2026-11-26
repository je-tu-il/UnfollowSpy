FROM nginx:alpine
COPY index.html styles.css app.js app-icon.png /usr/share/nginx/html/
