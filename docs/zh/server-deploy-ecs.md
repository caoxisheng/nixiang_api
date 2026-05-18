# 阿里云 ECS 部署方案

本文档面向你当前这台马来西亚阿里云 ECS，目标是把本仓库以 Docker Compose 方式部署为长期可用的 Kiro Gateway 服务。

## 方案结论

- 首选方案：`Docker Compose + Kiro Gateway + Caddy(可选)`
- 服务器区域：马来西亚，可直接访问 AWS，上游通常不需要额外代理
- 推荐暴露方式：
  - 无域名：先用 `http://服务器IP:8000`
  - 有域名：再加 Caddy，切到 `https://你的域名`

## 目录结构

服务器上建议把仓库放到：

```text
/opt/kiro-gateway
```

部署时会用到这些文件：

- `deploy/ecs/.env.server.example`
- `deploy/ecs/credentials.server.json.example`
- `deploy/ecs/docker-compose.ecs.yml`
- `deploy/ecs/Caddyfile.example`

你真正运行时要准备的是：

- `deploy/ecs/.env.server`
- `deploy/ecs/runtime/credentials.json`
- `deploy/ecs/runtime/state.json`
- `deploy/ecs/secrets/kiro-auth-token.json`

## 一次性准备

### 1. 服务器安装 Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 拉代码

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/caoxisheng/nixiang_api.git kiro-gateway
sudo chown -R $USER:$USER /opt/kiro-gateway
cd /opt/kiro-gateway
```

## 运行前配置

### 1. 复制服务器环境模板

```bash
cd /opt/kiro-gateway
mkdir -p deploy/ecs/runtime deploy/ecs/secrets deploy/ecs/debug_logs
cp deploy/ecs/.env.server.example deploy/ecs/.env.server
cp deploy/ecs/credentials.server.json.example deploy/ecs/runtime/credentials.json
touch deploy/ecs/runtime/state.json
```

### 2. 修改 `.env.server`

至少改这几项：

```env
PROXY_API_KEY="换成你自己的长随机密钥"
SERVER_HOST="0.0.0.0"
SERVER_PORT="8000"
ACCOUNT_SYSTEM=true
ACCOUNTS_CONFIG_FILE="/app/runtime/credentials.json"
ACCOUNTS_STATE_FILE="/app/runtime/state.json"
DEBUG_MODE="errors"
LOG_LEVEL="INFO"
VPN_PROXY_URL=""
```

### 3. 上传真实 Kiro 凭据

把你本机的：

```text
C:\Users\Xi\.aws\sso\cache\kiro-auth-token.json
```

上传到服务器：

```text
/opt/kiro-gateway/deploy/ecs/secrets/kiro-auth-token.json
```

你可以在 Windows 上执行：

```powershell
scp C:\Users\Xi\.aws\sso\cache\kiro-auth-token.json root@47.250.173.67:/opt/kiro-gateway/deploy/ecs/secrets/kiro-auth-token.json
```

### 4. 确认运行时账号配置

`deploy/ecs/runtime/credentials.json` 默认内容应该是：

```json
[
  {
    "type": "json",
    "path": "/app/secrets/kiro-auth-token.json"
  }
]
```

这里填的是容器内路径，不是服务器宿主机路径。

## 启动

```bash
cd /opt/kiro-gateway
docker compose -f deploy/ecs/docker-compose.ecs.yml --env-file deploy/ecs/.env.server up -d --build
```

查看日志：

```bash
docker compose -f deploy/ecs/docker-compose.ecs.yml logs -f
```

查看健康检查：

```bash
curl http://127.0.0.1:8000/health
```

## 阿里云安全组

至少放行：

- TCP `8000`

如果你后面加 Caddy，则改成放行：

- TCP `80`
- TCP `443`

并把 `8000` 限制为服务器本机使用即可。

## 客户端接入

### OpenAI 兼容

- Base URL: `http://47.250.173.67:8000/v1`
- API Key: 你在 `deploy/ecs/.env.server` 里设置的 `PROXY_API_KEY`

### Anthropic 兼容 / Claude Code / cc-switch

- Base URL: `http://47.250.173.67:8000`
- API Key: 同一个 `PROXY_API_KEY`

## 可选：加域名和 HTTPS

如果你有域名，推荐再加 Caddy：

```bash
sudo apt install -y caddy
sudo cp deploy/ecs/Caddyfile.example /etc/caddy/Caddyfile
sudoedit /etc/caddy/Caddyfile
sudo systemctl restart caddy
```

把 `your-domain.example.com` 改成你的真实域名。

## 更新流程

```bash
cd /opt/kiro-gateway
git pull
docker compose -f deploy/ecs/docker-compose.ecs.yml --env-file deploy/ecs/.env.server up -d --build
```

## 风险与注意事项

- 不要把 `deploy/ecs/.env.server`、`deploy/ecs/runtime/credentials.json`、`deploy/ecs/secrets/kiro-auth-token.json` 提交到 GitHub
- 服务器对外开放后，`PROXY_API_KEY` 一定要足够长、足够随机
- 如果你未来要给外部用户长期使用，建议尽快切到域名 + HTTPS
- 如果 Kiro 账号在本机重新登录后令牌变化，需要重新把 `kiro-auth-token.json` 上传到服务器
