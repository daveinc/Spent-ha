# Stage 1: build the Next.js standalone output
FROM node:20-alpine AS builder

RUN apk add --no-cache python3 make g++ libc6-compat

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: lean runtime image
FROM node:20-alpine AS runner

# Chromium and runtime deps for bank scrapers
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    nginx \
    bash \
    curl \
    tini

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV SPENT_DISABLE_CHROMIUM_SANDBOX=true

WORKDIR /app

# Copy standalone output + static assets
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

COPY nginx.conf /etc/nginx/http.d/spent.conf
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 41234

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/run.sh"]
