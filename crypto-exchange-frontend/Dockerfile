# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Set the API URL environment variable
ARG VITE_API_URL=http://api:8000
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Add configuration for SPA routing
RUN echo "server { \
  listen 80; \
  location / { \
  root /usr/share/nginx/html; \
  index index.html; \
  try_files \$uri \$uri/ /index.html; \
  } \
  }" > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 