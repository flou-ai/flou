FROM node:22-alpine AS builder

WORKDIR /app

COPY studio/package*.json .

RUN npm ci

COPY studio .

RUN npm run build
RUN npm prune --production

FROM node:18-alpine
WORKDIR /app

COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/

COPY studio/package.json .

EXPOSE $PORT

ENV NODE_ENV=production

CMD [ "node", "build" ]
