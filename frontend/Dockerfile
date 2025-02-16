# Frontend Dockerfile (Next.js)
FROM node:22-alpine

# Set the working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Expose port 3000 for the Next.js app
EXPOSE 3000

# Command to run the Next.js app
CMD ["npm", "start"]
