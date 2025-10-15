# 🚀 Deployment Guide

Complete guide for deploying Parametric Yantra Generator to production.

## Table of Contents
1. [Free Tier Deployment (Recommended)](#free-tier-deployment)
2. [Self-Hosted Deployment](#self-hosted-deployment)
3. [Configuration](#configuration)
4. [SSL/TLS Setup](#ssltls-setup)
5. [Monitoring](#monitoring)
6. [Backup & Recovery](#backup--recovery)

---

## Free Tier Deployment

### Prerequisites
```bash
# Install CLI tools
npm install -g wrangler  # Cloudflare
curl -L https://fly.io/install.sh | sh  # Fly.io
```

### Step 1: Database (Supabase - Free)

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Enable PostGIS extension:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```
4. Copy connection string
5. Add to `.env`:
```bash
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

### Step 2: Redis (Upstash - Free)

1. Go to [upstash.com](https://upstash.com)
2. Create Redis database
3. Copy connection string
4. Add to `.env`:
```bash
REDIS_URL=rediss://default:[password]@[endpoint].upstash.io:6379
```

### Step 3: Storage (Cloudflare R2 - Free 10GB)

1. Go to Cloudflare Dashboard → R2
2. Create bucket `yantra-exports`
3. Create API token
4. Add to `.env`:
```bash
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_BUCKET_NAME=yantra-exports
```

### Step 4: Backend (Fly.io - Free 256MB)

```bash
cd backend

# Create fly.toml
cat > fly.toml << EOF
app = "yantra-api"
primary_region = "sin"  # Singapore (or your preferred region)

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "10s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
EOF

# Deploy
fly launch --no-deploy
fly secrets set DATABASE_URL="your-database-url"
fly secrets set REDIS_URL="your-redis-url"
fly secrets set JWT_SECRET="$(openssl rand -hex 32)"
fly secrets set R2_ACCESS_KEY="your-r2-key"
fly secrets set R2_SECRET_KEY="your-r2-secret"
fly deploy

# Get URL
fly info
# API will be at: https://yantra-api.fly.dev
```

### Step 5: Frontend (Cloudflare Pages - Free)

```bash
cd frontend

# Update API URL
echo "NEXT_PUBLIC_API_URL=https://yantra-api.fly.dev" > .env.production

# Build
npm run build

# Deploy
npx wrangler pages deploy out/ --project-name yantra-app

# Your site will be at: https://yantra-app.pages.dev
```

### Step 6: CDN (Cloudflare - Free)

1. Add custom domain in Cloudflare Pages
2. Enable:
   - Auto minify (JS, CSS, HTML)
   - Brotli compression
   - Always Use HTTPS
3. Set cache rules for static assets

**Total Monthly Cost: $0** ✅

---

## Self-Hosted Deployment

### Option A: Docker Compose (Single Server)

**Minimum Requirements:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 22.04 LTS

```bash
# 1. Setup server
ssh user@your-server

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Clone repository
git clone https://github.com/yourusername/parametric-yantra.git
cd parametric-yantra

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 5. Generate secrets
openssl rand -hex 32  # Use for JWT_SECRET

# 6. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 7. Setup SSL with Traefik (included in prod compose)
# Edit traefik.yml with your domain
docker-compose -f docker-compose.prod.yml restart traefik
```

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    labels:
      - "traefik.http.routers.api.rule=Host(`traefik.yourdomain.com`)"
      - "traefik.http.routers.api.service=api@internal"

  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: yantra
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/yantra
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET: ${JWT_SECRET}
      ENVIRONMENT: production
      DEBUG: "false"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Option B: Kubernetes (Production Scale)

```bash
# 1. Install kubectl & helm
curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 2. Deploy to cluster
kubectl create namespace yantra
kubectl apply -f k8s/ -n yantra

# 3. Setup ingress
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx -n yantra
```

---

## Configuration

### Production Environment Variables

```bash
# Security
JWT_SECRET=$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=false

# CORS (your domain only)
CORS_ORIGINS=https://yourdomain.com

# Database (use connection pooling)
DATABASE_URL=postgresql://user:pass@host:5432/yantra
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://host:6379/0

# Storage
R2_ACCOUNT_ID=xxx
R2_ACCESS_KEY=xxx
R2_SECRET_KEY=xxx
R2_BUCKET_NAME=yantra-exports
R2_PUBLIC_URL=https://cdn.yourdomain.com

# Rate Limiting (stricter in production)
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_BURST=5

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
SENTRY_TRACES_SAMPLE_RATE=0.1

# Features (disable beta features)
ENABLE_COLLABORATIVE_MODE=false
ENABLE_CITIZEN_SCIENCE=false
```

---

## SSL/TLS Setup

### With Traefik (Automated)
Already configured in docker-compose.prod.yml above.

### Manual with Certbot
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring

### Setup Sentry (Free Tier)

1. Create account at [sentry.io](https://sentry.io)
2. Add DSN to environment:
```bash
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Setup Grafana Cloud (Free Tier)

```bash
# 1. Create account at grafana.com
# 2. Get credentials
# 3. Add to docker-compose:

  grafana-agent:
    image: grafana/agent:latest
    volumes:
      - ./grafana-agent.yaml:/etc/agent/agent.yaml
    environment:
      GRAFANA_CLOUD_API_KEY: ${GRAFANA_API_KEY}
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Database health
curl https://api.yourdomain.com/health/ready

# Setup monitoring endpoint
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=xxx" \
  -d "url=https://api.yourdomain.com/health" \
  -d "type=1"
```

---

## Backup & Recovery

### Database Backups

**Automated Daily Backups:**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="yantra"

# Backup database
docker exec yantra-postgres pg_dump -U yantra $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup to S3/R2
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-backup-bucket/

# Keep only last 30 days locally
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

**Restore from Backup:**
```bash
# Stop services
docker-compose down

# Restore database
gunzip < backup.sql.gz | docker exec -i yantra-postgres psql -U yantra yantra

# Start services
docker-compose up -d
```

### File Storage Backups

```bash
# Sync R2/MinIO to backup location
rclone sync r2:yantra-exports /backup/exports --progress

# Or use R2 lifecycle rules (Cloudflare Dashboard)
# Automatically archive to R2 Infrequent Access after 90 days
```

### Disaster Recovery

**Recovery Time Objective (RTO):** < 1 hour  
**Recovery Point Objective (RPO):** < 24 hours

```bash
# 1. Provision new server
# 2. Install Docker
# 3. Clone repository
git clone https://github.com/yourusername/parametric-yantra.git

# 4. Restore environment
cp .env.backup .env

# 5. Restore database
docker-compose up -d postgres
gunzip < latest_backup.sql.gz | docker exec -i yantra-postgres psql -U yantra yantra

# 6. Start all services
docker-compose up -d

# 7. Verify
curl https://api.yourdomain.com/health
```

---

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_projects_yantra_type ON projects(yantra_type);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_exports_project_id ON exports(project_id);
CREATE INDEX idx_observations_site_id ON observations(site_id);

-- Enable query plan caching
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Optimize PostgreSQL settings (in postgresql.conf)
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 128MB
```

### Redis Caching Strategy

```python
# Cache ephemeris calculations (expensive)
cache_key = f"sun_position:{lat}:{lon}:{timestamp}"
ttl = 3600  # 1 hour

# Cache generated yantras (by parameters)
cache_key = f"yantra:{type}:{lat}:{lon}:{scale}"
ttl = 86400  # 24 hours
```

### CDN Configuration

```nginx
# Cloudflare Page Rules
# Cache everything on *.yourdomain.com
Cache Level: Standard
Edge Cache TTL: 1 month for static assets

# Browser Cache TTL
location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Security Hardening

### Firewall Rules (UFW)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (change port if needed)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny everything else
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### Fail2ban Setup

```bash
# Install fail2ban
sudo apt install fail2ban

# Configure for Traefik
cat > /etc/fail2ban/filter.d/traefik-auth.conf << EOF
[Definition]
failregex = ^<HOST> .* ".*" 401 .*$
            ^<HOST> .* ".*" 403 .*$
ignoreregex =
EOF

# Enable jail
cat > /etc/fail2ban/jail.d/traefik.conf << EOF
[traefik-auth]
enabled = true
port = http,https
filter = traefik-auth
logpath = /var/log/traefik/access.log
maxretry = 5
bantime = 3600
EOF

sudo systemctl restart fail2ban
```

### Regular Security Updates

```bash
# Auto-update system packages
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Update Docker images weekly
cat > /etc/cron.weekly/docker-update << 'EOF'
#!/bin/bash
cd /opt/parametric-yantra
docker-compose pull
docker-compose up -d
docker image prune -f
EOF

chmod +x /etc/cron.weekly/docker-update
```

---

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose with replicas
services:
  backend:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  # Add load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

### Caching Strategy

```
┌─────────┐
│ Browser │
└────┬────┘
     │
┌────▼─────────┐
│ Cloudflare   │ (Cache static assets)
└────┬─────────┘
     │
┌────▼─────────┐
│ Backend      │
└────┬─────────┘
     │
┌────▼─────────┐
│ Redis        │ (Cache ephemeris, generations)
└────┬─────────┘
     │
┌────▼─────────┐
│ PostgreSQL   │
└──────────────┘
```

---

## Troubleshooting

### Common Issues

**Issue: Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Database not ready
# 2. Missing environment variables
# 3. Port already in use

# Fix:
docker-compose down
docker-compose up -d postgres redis
sleep 10
docker-compose up -d backend
```

**Issue: High memory usage**
```bash
# Check container stats
docker stats

# Limit container memory
services:
  backend:
    mem_limit: 512m
    mem_reservation: 256m
```

**Issue: Slow generation**
```bash
# Check Redis cache hit rate
redis-cli INFO stats | grep keyspace

# Enable query logging
# In PostgreSQL: log_min_duration_statement = 1000

# Profile Python code
python -m cProfile -o profile.stats app/main.py
```

---

## Maintenance Schedule

**Daily:**
- ✅ Check error logs (Sentry)
- ✅ Monitor response times
- ✅ Review failed generation attempts

**Weekly:**
- ✅ Database backup verification
- ✅ Security updates
- ✅ Clean up old exports (> 30 days)
- ✅ Review rate limit violations

**Monthly:**
- ✅ Update dependencies (Renovate)
- ✅ Performance review
- ✅ Cost analysis
- ✅ User feedback review

**Quarterly:**
- ✅ Security audit
- ✅ Disaster recovery test
- ✅ Capacity planning
- ✅ Feature roadmap review

---

## Cost Estimates

### Free Tier (Recommended for < 1000 users/month)
- Supabase: Free (500MB DB, 2GB bandwidth)
- Upstash Redis: Free (10K commands/day)
- Cloudflare R2: Free (10GB storage)
- Fly.io: Free (256MB RAM)
- Cloudflare Pages: Free (unlimited bandwidth)
- **Total: $0/month** ✅

### Self-Hosted VPS (For > 1000 users/month)
- Hetzner VPS (CX21): €5.83/month (2 vCPU, 4GB RAM)
- Backups: €2/month
- Domain + SSL: €12/year (~€1/month)
- **Total: ~€9/month ($10/month)**

### Production Scale (Enterprise)
- Managed Kubernetes: $100-500/month
- Managed PostgreSQL: $50-200/month
- Redis Enterprise: $50-150/month
- CDN: $20-100/month
- Monitoring: $20-50/month
- **Total: $240-1000/month**

---

## Success Checklist

- [ ] All services running and healthy
- [ ] SSL certificates valid
- [ ] Backups running daily
- [ ] Monitoring configured (Sentry + Grafana)
- [ ] Error rates < 1%
- [ ] Response time < 500ms (p95)
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team has access to credentials
- [ ] Disaster recovery plan tested

---

**Need Help?**
- 📧 Email: devops@yantra-generator.org
- 💬 Discord: https://discord.gg/yantra
- 📚 Docs: https://docs.yantra-generator.org/deployment