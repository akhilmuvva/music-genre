# Dockerfile for Node backend in server/
FROM node:18-alpine
WORKDIR /app

# Copy package manifest and install deps
COPY package.json package-lock.json* ./
RUN npm install --production --silent

# Copy server files
COPY . .

EXPOSE 5000
CMD ["npm", "start"]
