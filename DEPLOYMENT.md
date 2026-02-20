# Ravion Website Deployment Guide

This guide covers how to deploy the Ravion Digital website to a live server (like a VPS using DigitalOcean, Linode, AWS EC2, or a platform like Heroku/Render).

## 1. Environment Preparation
Before deploying, make sure your `.env` file is set up on the server. **Do not push `.env` to GitHub**.

Example `.env` on your server:
```env
SECRET_KEY=your_production_secret_key_here
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_super_secure_password
```

## 2. Pushing to GitHub
Your secrets are now protected by `.gitignore`. You can safely push:
```bash
git init
git add .
git commit -m "Initial commit for production"
git branch -M main
git remote add origin https://github.com/your-username/ravion-website.git
git push -u origin main
```

## 3. Server Setup (Example: Ubuntu Linux VPS)

### Install Dependencies
SSH into your server and run:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### Clone and Setup
```bash
git clone https://github.com/your-username/ravion-website.git
cd ravion-website
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create the `.env` File
Create your `.env` file directly on the server:
```bash
nano .env
# Paste your secrets as shown in Step 1, then save (Ctrl+O, Enter, Ctrl+X)
```

## 4. Running the App with Gunicorn
We use `gunicorn` to run the production server.
```bash
# Test it runs:
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```
*Press Ctrl+C to stop the test.*

To keep it running in the background, set up a Systemd service:
```bash
sudo nano /etc/systemd/system/ravion.service
```
Add the following content (update the paths to match your actual server directory):
```ini
[Unit]
Description=Gunicorn daemon for Ravion Website
After=network.target

[Service]
User=your_linux_user
Group=www-data
WorkingDirectory=/path/to/ravion-website
Environment="PATH=/path/to/ravion-website/venv/bin"
ExecStart=/path/to/ravion-website/venv/bin/gunicorn --workers 3 --bind unix:ravion.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start ravion
sudo systemctl enable ravion
```

## 5. Exposing with Nginx (Reverse Proxy)
Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/ravion
```
Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/ravion /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. Securing with SSL (HTTPS)
Use Certbot to get a free SSL certificate:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Your site is now live and secure!
