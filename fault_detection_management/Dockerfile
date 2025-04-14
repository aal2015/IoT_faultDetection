# Dockerfile for React frontend (Vite app)
FROM node:23-alpine3.19

WORKDIR /src/app

# Copy package files first (helps with Docker layer caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Now copy the rest of the app
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host"]