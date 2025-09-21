# Minimal runtime image
FROM nginx:alpine
# COPY STATIC PAGES
COPY build/ /usr/share/nginx/html 
# COPY CONFIG
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80



