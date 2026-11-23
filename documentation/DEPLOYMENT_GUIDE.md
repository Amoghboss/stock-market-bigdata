# Production Deployment Guide
## Large-Scale Stock Market Data Processing and Trend Analysis using Hadoop HDFS

This guide provides step-by-step instructions for deploying the platform across 4 different deployment environments:
1. **[Method 1: 1-Click Free Cloud Deployment (Render.com / Railway)](#method-1-free-cloud-deployment-render--railway)** *(Recommended for sharing a live public HTTPS URL with evaluators/professors)*
2. **[Method 2: Instant Public URL via Cloudflare Tunnel / ngrok](#method-2-instant-public-access-via-cloudflare-tunnel--ngrok)** *(Share your currently running localhost:3000 in 60 seconds without cloud setup)*
3. **[Method 3: Docker & Docker Compose](#method-3-docker--docker-compose-containerization)** *(Single-command local or VPS containerization)*
4. **[Method 4: Production Linux Server (AWS EC2 / DigitalOcean / Ubuntu VPS)](#method-4-production-linux-vps-aws-ec2--ubuntu)** *(Enterprise setup with Gunicorn, Systemd, Nginx, and SSL)*

---

## Method 1: Free Cloud Deployment (Render / Railway)

Get a permanent public HTTPS URL (e.g., `https://stock-market-bigdata.onrender.com`) in under 3 minutes for free.

### Step 1: Push Project to GitHub
1. Create a new repository on [GitHub](https://github.com/new) named `stock-market-bigdata`.
2. Push your project code:
   ```bash
   cd c:\Users\amogh\Downloads\stock-market-bigdata
   git init
   git add .
   git commit -m "Initial commit of Stock Market Big Data platform"
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/stock-market-bigdata.git
   git push -u origin main
   ```

### Step 2: Deploy on Render.com (Free Tier)
1. Sign up / Log in to [Render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your `stock-market-bigdata` repo.
4. Render will automatically detect the settings from `render.yaml`, or configure manually:
   - **Name**: `stock-market-bigdata`
   - **Language**: `Python 3`
   - **Region**: Closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python run.py generate && python run.py preprocess && python run.py mapreduce-local && python run.py analytics
     ```
   - **Start Command**:
     ```bash
     gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 3 --timeout 120
     ```
   - **Instance Type**: `Free`
5. Click **Create Web Service**.
6. Render builds the container, executes the MapReduce suite, and provides a live HTTPS link!

---

## Method 2: Instant Public Access via Cloudflare Tunnel / ngrok

If your application is already running on `localhost:3000` on your machine, you can expose it securely to the public internet in 60 seconds without creating any server or pushing code.

### Option A: Cloudflare Tunnel (100% Free, No Account Needed)
1. Download `cloudflared` for Windows:
   - Run in PowerShell:
     ```powershell
     winget install --id Cloudflare.cloudflared
     ```
2. Start the tunnel to port 3000:
   ```powershell
   cloudflared tunnel --url http://localhost:3000
   ```
3. Cloudflare will print a public HTTPS link (e.g., `https://random-words.trycloudflare.com`). Anyone with this link can view your live dashboard from any device!

### Option B: ngrok
1. Run in PowerShell:
   ```powershell
   ngrok http 3000
   ```
2. Copy the forwarding URL (e.g., `https://abc123.ngrok-free.app`).

---

## Method 3: Docker & Docker Compose Containerization

The repository includes a production multi-stage `Dockerfile` and `docker-compose.yml`.

### Step 1: Build & Run with Docker Compose
From the project root:
```bash
docker-compose up --build -d
```

### Step 2: Verify Running Container
```bash
docker ps
# Open http://localhost:3000 in your browser
```

### Step 3: Inspect Logs & Stop
```bash
# View live logs
docker logs -f stock_bigdata_analytics

# Stop container
docker-compose down
```

---

## Method 4: Production Linux VPS (AWS EC2 / Ubuntu)

For deploying on an AWS EC2 instance, DigitalOcean Droplet, or Ubuntu Server with Nginx reverse proxy and Systemd.

### Step 1: System Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx git curl
```

### Step 2: Clone & Virtual Environment
```bash
cd /var/www
sudo git clone https://github.com/<YOUR_USERNAME>/stock-market-bigdata.git
sudo chown -R $USER:$USER stock-market-bigdata
cd stock-market-bigdata

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Run Data & MapReduce Initialization
```bash
python run.py generate
python run.py preprocess
python run.py mapreduce-local
python run.py analytics
```

### Step 4: Configure Systemd Service
Create service file `/etc/systemd/system/stock-analytics.service`:
```ini
[Unit]
Description=Stock Market Big Data Analytics Platform Gunicorn Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/stock-market-bigdata
Environment="PATH=/var/www/stock-market-bigdata/venv/bin"
ExecStart=/var/www/stock-market-bigdata/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:3000 --timeout 120 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-analytics
sudo systemctl start stock-analytics
sudo systemctl status stock-analytics
```

### Step 5: Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/stock-analytics`:
```nginx
server {
    listen 80;
    server_name your-domain.com your_server_ip;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/stock-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Install Free SSL Certificate (Certbot)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Deployment Architecture Checklist

- [x] `wsgi.py` production entrypoint configured with auto-initialization
- [x] `requirements.txt` with Gunicorn included
- [x] `Dockerfile` with multi-stage pre-computation of MapReduce jobs
- [x] `docker-compose.yml` with port mapping and volume persistence
- [x] `Procfile` and `render.yaml` for 1-click cloud platform builds
- [x] Relative API paths configured in frontend for port-independent deployment
- [x] Comprehensive test suite verified (27 Passed, 1 Skipped)
