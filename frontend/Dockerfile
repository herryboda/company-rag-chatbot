# Build
FROM node:20-alpine AS build
WORKDIR /app

# Copy config and source files
COPY package.json vite.config.js tailwind.config.js postcss.config.js index.html ./
COPY src ./src

RUN npm install
RUN npm run build

# Serve static files
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
