# 🚀 Deploy Telegram Bot to Render (24/7 Operation)

## ✅ Prerequisites
- [x] render-bot.yaml created and pushed to GitHub
- [x] telegram_bot_clean.py ready
- [x] Web server already running on Render

---

## 📋 Step-by-Step Instructions

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Log in with your account

### Step 2: Create New Service
1. Click the **"New +"** button (top right)
2. Select **"Blueprint"** from the dropdown

### Step 3: Connect Repository
1. You'll see "Connect a repository"
2. If not connected yet, click **"Connect GitHub"**
3. Find and select your repository: **memtop**
4. Click **"Connect"**

### Step 4: Select Blueprint File
1. Render will detect both `render.yaml` and `render-bot.yaml`
2. **IMPORTANT:** Select **`render-bot.yaml`**
   - This is the bot worker configuration
   - render.yaml is for the web server (already deployed)

### Step 5: Review Configuration
You should see:
- **Service Type:** Worker
- **Name:** telegram-bot-worker
- **Runtime:** Python
- **Plan:** Free
- **Build Command:** pip install python-telegram-bot==20.7
- **Start Command:** python telegram_bot_clean.py

**Environment Variables:**
- BOT_TOKEN: 8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM
- AUTHORIZED_CHAT_ID: 2103408372

### Step 6: Deploy
1. Click **"Apply"** or **"Create Blueprint"**
2. Render will start building and deploying
3. Wait 2-3 minutes for deployment to complete

### Step 7: Monitor Deployment
1. Go to the service page for "telegram-bot-worker"
2. Click **"Logs"** tab
3. You should see:
   ```
   ======================================================================
   🤖 Starting Telegram Bot (POLLING MODE)
   ======================================================================
   Bot Token: 8567043675:AAHB7C...
   Authorized Chat ID: 2103408372
   ======================================================================
   ✅ Bot commands registered
   🚀 Starting polling...
   ```

### Step 8: Test the Bot
1. Open Telegram
2. Find your bot: **@pluseight_bot**
3. Send: `/start`
4. **Expected:** Bot responds with command menu immediately

---

## ✅ Success Indicators

### In Render Logs:
```
✅ Bot commands registered
🚀 Starting polling...
INFO:telegram.ext.Application:Application started
```

### In Telegram:
- Bot responds to `/start`
- All commands work:
  - `/createkey` - Generates admin key
  - `/currentkey` - Shows current key
  - `/generatecode` - Creates access code
  - `/listcodes` - Lists all codes
  - `/revokecode` - Removes a code
  - `/help` - Shows help

---

## 🎯 What You Should Have Running

After completing these steps, you'll have **TWO services** on Render:

### Service 1: Web Server (Already Running)
- **Name:** memtop-video-streaming
- **Type:** Web Service
- **File:** render.yaml
- **Runs:** web_server_only.py
- **URL:** https://memtop-video-streaming.onrender.com
- **Purpose:** Serves website and admin panel

### Service 2: Bot Worker (NEW)
- **Name:** telegram-bot-worker
- **Type:** Background Worker
- **File:** render-bot.yaml
- **Runs:** telegram_bot_clean.py
- **Purpose:** Handles Telegram bot commands 24/7

---

## 🔧 Troubleshooting

### Issue: "Blueprint not found"
**Solution:** 
- Make sure render-bot.yaml is in the root directory
- Verify it's pushed to GitHub
- Try refreshing the page

### Issue: Bot doesn't start
**Check Render logs for:**
- "Module not found" → Build command might have failed
- "Invalid token" → Check BOT_TOKEN is correct
- "Connection error" → Network issue, will auto-retry

### Issue: Bot responds but commands don't work
**Check:**
- AUTHORIZED_CHAT_ID matches your Telegram chat ID
- Storage files (key_storage.json, access_codes.json) exist

### Issue: Bot stops responding after a while
**Check:**
- Worker service status in Render dashboard
- Free tier limits (should be fine for bot)
- Logs for any crash messages

---

## 💰 Cost

**Totally FREE!**
- Render Free Tier includes background workers
- No credit card required
- Bot runs 24/7 at no cost

---

## 🎉 Final Testing Checklist

Once deployed, verify:

- [ ] Web server works: https://memtop-video-streaming.onrender.com/health
- [ ] Admin panel loads: /parking55009hvSweJimbs5hhinbd56y
- [ ] Bot responds to `/start`
- [ ] `/createkey` generates a key
- [ ] `/generatecode` creates access code
- [ ] `/listcodes` shows codes
- [ ] `/help` displays help message

**If ALL checks pass → Setup is COMPLETE! ✅**

---

## 📞 Alternative: If Render Blueprint Doesn't Work

If you have trouble with Blueprint deployment, use **Manual Setup**:

1. Click "New +" → "Background Worker"
2. Connect repository
3. Configure manually:
   - **Name:** telegram-bot-worker
   - **Build Command:** `pip install python-telegram-bot==20.7`
   - **Start Command:** `python telegram_bot_clean.py`
4. Add Environment Variables:
   - BOT_TOKEN: 8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM
   - AUTHORIZED_CHAT_ID: 2103408372
5. Deploy!

---

## 🚀 Ready to Deploy?

Go to: https://dashboard.render.com and follow the steps above!

Let me know when you've deployed and I'll help you verify everything is working.
