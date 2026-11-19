# Module 9, Session 15: the Clinic Desk in a container, in two stages.
#   docker build -t sunrise-web .        (in the web folder)
# Stage 1 has Node.js and every package, and builds dist. Stage 2 is a small
# web server with dist only: no Node.js, no node_modules, no source code.
FROM node:22-slim AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
# .env.production gives VITE_API_BASE_URL=/api/v1: the page asks its own server
RUN npm run build

FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /web/dist /usr/share/nginx/html
EXPOSE 80
