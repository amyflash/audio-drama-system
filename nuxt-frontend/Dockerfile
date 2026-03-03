FROM node:22-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json* ./
RUN npm install

# 复制源码并构建 Nuxt 应用
COPY . .
RUN npm run build

# 生产运行镜像
FROM node:22-alpine AS runner

WORKDIR /app

# 仅复制运行所需文件，减小镜像体积
COPY --from=builder /app/.output ./.output

# Nuxt/Nitro 默认读取这些环境变量来确定监听端口
ENV NITRO_PORT=80
ENV NITRO_HOST=0.0.0.0

EXPOSE 80

CMD ["node", ".output/server/index.mjs"]

