FROM nginx:alpine

# Remover a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar arquivos do frontend
COPY index.html /usr/share/nginx/html/

# Copiar configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Expor porta 80
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]