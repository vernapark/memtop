# 🚀 Render.com Deployment Guide

## Video Streaming Website with Telegram Bot Authentication

---

## 📋 Pre-Deployment Checklist

✅ Telegram Bot Token: `8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM`  
✅ Your Chat ID: `2103408372`  
✅ Bot Username: `@pluseight_bot`  
✅ All files ready for deployment

---

## 🌐 Step-by-Step Deployment on Render.com

### Step 1: Prepare Your Repository

1. **Create a GitHub repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Video Streaming Website"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy to Render.com

1. **Go to [Render.com](https://render.com)** and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the Web Service:

   **Web Service Settings:**
   - **Name:** `video-streaming-site`
   - **Region:** Oregon (Free)
   - **Branch:** `main`
   - **Root Directory:** Leave empty
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python init_storage.py`
   - **Start Command:** `python web_server.py`
   - **Plan:** Free

5. **Environment Variables** (Add these in the Environment tab):
   ```
   PYTHON_VERSION = 3.11.0
   ```

6. Click **"Create Web Service"**

### Step 3: Deploy Telegram Bot (Background Worker)

1. In Render Dashboard, click **"New +"** → **"Background Worker"**
2. Connect the same repository
3. Configure the Worker:

   **Worker Settings:**
   - **Name:** `telegram-bot-worker`
   - **Region:** Oregon (Free)
   - **Branch:** `main`
   - **Root Directory:** Leave empty
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python init_storage.py`
   - **Start Command:** `python telegram_bot.py`
   - **Plan:** Free

4. **Environment Variables** (Add these):
   ```
   BOT_TOKEN = 8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM
   AUTHORIZED_CHAT_ID = 2103408372
   PYTHON_VERSION = 3.11.0
   ```

5. Click **"Create Background Worker"**

---

## 🔐 Post-Deployment Setup

### Step 1: Get Your Website URL

After deployment, Render will give you a URL like:
```
https://video-streaming-site-xxxx.onrender.com
```

### Step 2: Update Bot Welcome Message (Optional)

Edit `telegram_bot.py` line with your actual URL:
```python
# Update this line with your Render URL
"Go to: `https://video-streaming-site-xxxx.onrender.com/parking55009hvSweJimbs5hhinbd56y`\n"
```

### Step 3: Test Your Bot

1. Open Telegram
2. Search: `@pluseight_bot`
3. Send: `/start`
4. Send: `/createkey`
5. Copy the key
6. Visit: `https://your-site.onrender.com/parking55009hvSweJimbs5hhinbd56y`
7. Paste the key and login ✅

---

## 📁 Important Files for Render.com

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `runtime.txt` | Python version specification |
| `Procfile` | Process definitions (web + bot) |
| `render.yaml` | Render configuration (optional) |
| `web_server.py` | Production web server |
| `telegram_bot.py` | Telegram bot (runs 24/7) |
| `init_storage.py` | Initializes key_storage.json |
| `key_storage.json` | Shared key storage (auto-created) |
| `.env.example` | Environment variables template |
| `.gitignore` | Files to exclude from git |

---

## ⚙️ Environment Variables Reference

### Web Service
```
PYTHON_VERSION = 3.11.0
PORT = 10000 (auto-set by Render)
```

### Telegram Bot Worker
```
BOT_TOKEN = 8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM
AUTHORIZED_CHAT_ID = 2103408372
PYTHON_VERSION = 3.11.0
```

---

## 🔄 Key Storage Synchronization

**Important:** Both web service and bot worker share `key_storage.json`

- When bot creates a new key → saves to `key_storage.json`
- When you login → website reads from `key_storage.json`
- Old keys are automatically invalidated

**Note:** On Render's free tier, the file system is ephemeral. For production, consider:
1. Using Render's Persistent Disk (paid feature)
2. Using external storage (AWS S3, Redis, etc.)
3. For now, the bot and web service should access the same file system

---

## 🐛 Troubleshooting

### Bot not responding?
1. Check Background Worker logs in Render dashboard
2. Verify `BOT_TOKEN` is correct
3. Restart the worker

### Can't login to admin panel?
1. Generate a new key: `/createkey` in Telegram
2. Check if key_storage.json exists
3. Verify web service is running

### Website not loading?
1. Check Web Service logs
2. Verify deployment succeeded
3. Check custom domain/URL is correct

---

## 🎯 Admin Panel Access

**Public URL:** `https://your-site.onrender.com`  
**Admin URL:** `https://your-site.onrender.com/parking55009hvSweJimbs5hhinbd56y`

- No link to admin panel on public site
- Only accessible via direct URL
- Requires key from Telegram bot
- Only your Chat ID (2103408372) can generate keys

---

## 🔒 Security Features

✅ **Key-only authentication** (no username/password)  
✅ **Keys generated only via Telegram bot**  
✅ **Only authorized Chat ID can create keys**  
✅ **Old keys auto-invalidate on new key creation**  
✅ **32-character cryptographically secure keys**  
✅ **Hidden admin panel (not linked publicly)**  
✅ **No way to reset/create keys from website**

---

## 📱 Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help guide
- `/createkey` - Generate new access key (invalidates old)
- `/currentkey` - View current active key

---

## ⚡ Performance Notes

**Render.com Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request may take 30-50 seconds (cold start)
- Background worker (bot) runs 24/7 but may restart

**For Better Performance:**
- Upgrade to paid plan ($7/month) for always-on
- Use Render's persistent disk for key storage
- Enable auto-scaling if needed

---

## 🎉 You're All Set!

Your video streaming website with Telegram bot authentication is now deployed and running 24/7 on Render.com!

**Next Steps:**
1. Test the complete flow
2. Upload some videos via admin panel
3. Share your public URL (but keep admin URL secret!)

**Need Help?**
- Check Render logs for errors
- Test bot with `/start` command
- Verify environment variables are set correctly

---

## 📞 Quick Reference

- **Bot:** @pluseight_bot
- **Your Chat ID:** 2103408372
- **Admin Path:** `/parking55009hvSweJimbs5hhinbd56y`
- **Repository:** (Add your GitHub repo URL here)
- **Render Dashboard:** https://dashboard.render.com

---

**Last Updated:** January 2026  
**Deployment Ready:** ✅ 100%
