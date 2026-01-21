# 🔧 SET WEBHOOK_URL Environment Variable

## 🚨 Current Error:
```
Failed to set webhook: 'Bad Request: invalid webhook URL specified'
```

**Cause:** The `WEBHOOK_URL` environment variable is empty!

---

## ✅ FIX: Set the Environment Variable

### Step 1: Get Your Render URL
Your service URL is something like:
```
https://telegram-bot-webhook-xxxx.onrender.com
```

Copy this URL from the top of your service page in Render dashboard.

### Step 2: Add Environment Variable
1. Go to service: **telegram-bot-webhook**
2. Click: **"Environment"** tab (left sidebar)
3. Click: **"Add Environment Variable"**
4. Fill in:
   - **Key:** `WEBHOOK_URL`
   - **Value:** `https://telegram-bot-webhook-xxxx.onrender.com` (YOUR actual URL)
5. Click: **"Save Changes"**
6. Service will auto-redeploy

---

## ✅ Expected Result:

After setting the variable, logs should show:
```
Webhook set to: https://telegram-bot-webhook-xxxx.onrender.com/webhook
```

Then the bot will work!

---

## 📋 What's Your Render URL?

Look at the top of the telegram-bot-webhook service page.
It should say something like:
```
https://telegram-bot-webhook-abcd.onrender.com
```

Copy that EXACT URL and add it as the `WEBHOOK_URL` environment variable!
