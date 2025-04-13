# Etapa 1: build
FROM node:18-slim AS builder

WORKDIR /app
COPY . .

RUN npm install
RUN npm run build

# Etapa 2: servir app optimizada
FROM node:18-slim

WORKDIR /app
RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]