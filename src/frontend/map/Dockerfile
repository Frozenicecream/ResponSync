# Stage 1: Build the React application
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Create .env file with OSRM service URL
RUN echo "REACT_APP_OSRM_SERVICE_URL=${OSRM_SERVICE_URL}" > .env

RUN npm run build

# Stage 2: Serve the React application with Nginx
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]