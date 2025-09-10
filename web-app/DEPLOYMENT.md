# Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from web-app directory**:
   ```bash
   cd web-app
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project? No
   - Project name: `ice-detention-heatmap`
   - Directory: `./`
   - Override settings? No

### Option 2: Deploy via GitHub Integration

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel-ready heatmap app"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set build settings:
     - Framework Preset: `Vite`
     - Build Command: `npm run build`
     - Output Directory: `dist`
     - Install Command: `npm install`

## 📊 What You Get

- **Free Vercel hosting** (100GB bandwidth/month)
- **Custom domain** (optional)
- **Automatic HTTPS**
- **Global CDN**
- **Zero database costs** (data is embedded)
- **Zero API costs** (self-contained app)

## 🔄 Updating Data

To update facility data:

1. **Export new data**:
   ```bash
   python export_facilities_for_frontend.py
   ```

2. **Commit and push**:
   ```bash
   git add src/data/facilities.json
   git commit -m "Update facility data"
   git push origin main
   ```

3. **Vercel auto-deploys** the changes!

## 📈 Performance

- **Bundle size**: ~1.8MB (gzipped: ~513KB)
- **Load time**: < 2 seconds
- **Data size**: 186 facilities (~50KB JSON)
- **No external API calls**

## 🛠️ Vercel Credentials Needed

You'll need:
- **Vercel account** (free)
- **GitHub account** (for integration)
- **Domain name** (optional, for custom domain)

No API keys or database credentials needed!

