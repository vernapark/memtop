# 🔄 Domain Update Guide

## New Domain Configuration
**Old:** `https://memtop-video-streaming-22xm.onrender.com`  
**New:** `https://04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming.onrender.com`

---

## 📋 Step-by-Step Instructions

### Step 1: Update Render Dashboard (MUST DO FIRST!)

1. Go to: https://dashboard.render.com
2. Click on your service: **memtop-video-streaming-22xm**
3. Click **Settings** tab
4. Scroll to **Service Details**
5. Click **Edit** next to Service Name
6. Change to: `04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming`
7. Click **Save Changes**
8. Wait for Render to update (takes 1-2 minutes)

### Step 2: Update Environment Variables in Render

1. Still in **Settings** tab
2. Scroll to **Environment Variables**
3. Find `WEBHOOK_URL`
4. Click **Edit**
5. Change value to: `https://04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming.onrender.com`
6. Click **Save Changes**

### Step 3: Update Configuration Files (Do After Render Changes)

Replace `render.yaml` with `render_new.yaml`:
```bash
cd memtop
rm render.yaml
mv render_new.yaml render.yaml
```

### Step 4: Update Telegram Webhook

After Render deploys, set the new webhook:
```bash
curl -X POST "https://api.telegram.org/bot8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming.onrender.com/telegram-webhook"}'
```

### Step 5: Verify Everything Works

1. **Check Health:**
   ```
   https://04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming.onrender.com/health
   ```

2. **Check Admin Panel:**
   ```
   https://04fj724hr3fwwi43fh4hwj78w4jrh7g4fo949we-streaming.onrender.com/parking55009hvSweJimbs5hhinbd56y
   ```

3. **Test Telegram Bot:**
   - Send a message to your bot
   - Upload a test video

---

## ⚠️ Important Notes

- **Do Render Dashboard changes FIRST** before updating files
- The service name change will trigger a redeploy
- Old URL will stop working after change
- Update any bookmarks or saved links
- Telegram webhook must be updated or bot won't work

---

## 🔍 Files That Need Manual Updates (Optional)

These files contain the old URL but are not critical:
- `enhanced_security_headers.py` (line 42)
- `robots.txt` (sitemap URL)
- `sitemap.xml` (all URLs)
- Various `.md` documentation files

You can update these after the main service is working.
