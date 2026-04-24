# ---- Build stage ----
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

# ----Production stage----
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -rf /usr/share/nginx/html/*

COPY --from=build /app/dist/*/browser/ /usr/share/nginx/html/

RUN if [ -f /usr/share/nginx/html/index.csr.html ]; then mv /usr/share/nginx/html/index.csr.html /usr/share/nginx/html/index.html; fi

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]