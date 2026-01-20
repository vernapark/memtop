# 🚀 Deploy to Render.com - Complete Guide

This guide will help you deploy your Video Streaming Website to Render.com for FREE!

## 📋 Prerequisites

- GitHub account with your repository: https://github.com/vernapark/memtop.git
- Render.com account (sign up at https://render.com - FREE!)

---

## 🎯 Step-by-Step Deployment

### Step 1: Sign Up / Login to Render

1. Go to https://render.com
2. Click **"Get Started for Free"** or **"Sign In"**
3. Sign up with your GitHub account (recommended)

---

### Step 2: Connect Your GitHub Repository

1. Once logged in, click **"New +"** button (top right)
2. Select **"Static Site"**
3. Click **"Connect account"** to connect GitHub (if not already connected)
4. Grant Render access to your repositories
5. Find and select your repository: **vernapark/memtop**

---

### Step 3: Configure Your Static Site

Fill in the following settings:

#### **Basic Settings:**
- **Name:** `memtop-video-site` (or any name you prefer)
- **Branch:** `main`
- **Root Directory:** Leave empty (or `.` if required)

#### **Build Settings:**
- **Build Command:** Leave empty or use: `echo "Static site - no build needed"`
- **Publish Directory:** `.` (dot means root directory)

#### **Advanced Settings (Optional):**
Click "Advanced" and you can add:
- **Auto-Deploy:** Yes (recommended - auto-deploys on git push)

---

### Step 4: Deploy!

1. Click **"Create Static Site"** button
2. Render will start deploying your site
3. Wait 1-2 minutes for deployment to complete
4. You'll see a green "Live" badge when ready

---

### Step 5: Get Your Live URL

Once deployed, you'll get a URL like:
```
https://memtop-video-site.onrender.com
```

You can also add a **custom domain** for free!

---

## 🎨 Your Website Features

### ✅ What Works on Render:

1. **Access Gate System** - 18+ restriction with access codes
2. **Video Upload & Storage** - Uses browser IndexedDB (client-side)
3. **Circular Category Badges** - Beautiful category icons on each video
4. **Paste Thumbnail Support** - Easy thumbnail upload in admin
5. **Admin Panel** - Secret admin dashboard
6. **Responsive Design** - Works on mobile, tablet, desktop

---

## 🔑 Important Information

### **Access Codes:**
Default access codes are stored in `access_codes.json`:
```json
{
  "access_codes": [
    "DEMO2024",
    "TEST123",
    "PREVIEW456"
  ]
}
```

### **Admin Access:**
- Admin URL: `https://your-site.onrender.com/parking55009hvSweJimbs5hhinbd56y.html`
- Default admin key is in `key_storage.json`

### **Storage:**
- Videos are stored in browser's IndexedDB (client-side)
- Each user has their own local storage
- No server-side storage needed!

---

## 🔄 Updating Your Site

### Method 1: Push to GitHub (Automatic)
```bash
cd Downloads/VideoStreamingSite
git add .
git commit -m "Update website"
git push origin main
```
Render will automatically redeploy!

### Method 2: Manual Deploy
1. Go to your Render dashboard
2. Click on your site
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🌐 Custom Domain (Optional)

Want to use your own domain like `memtop.com`?

1. Go to your site's Render dashboard
2. Click **"Settings"**
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain name
6. Follow DNS configuration instructions

---

## 📊 Monitoring & Logs

### View Logs:
1. Go to Render dashboard
2. Click your site name
3. Click **"Logs"** tab
4. See real-time deployment and error logs

### Metrics:
- View bandwidth usage
- See number of requests
- Monitor uptime

---

## ⚡ Performance Tips

1. **Enable Caching:**
   - Already configured in `render.yaml`
   - Caches CSS/JS for 1 year
   - HTML cached for 1 hour

2. **Optimize Images:**
   - Compress video thumbnails before pasting
   - Use appropriate image sizes

3. **IndexedDB Limits:**
   - Browser storage is limited (typically 50-100MB)
   - Compress videos before uploading
   - Clear old videos if needed

---

## 🐛 Troubleshooting

### Issue: Site not loading
**Solution:** 
- Check Render logs for errors
- Verify `index.html` exists in root
- Check browser console for JavaScript errors

### Issue: Videos not saving
**Solution:**
- Videos are stored in browser's IndexedDB
- Clear browser cache and try again
- Check browser storage settings

### Issue: Admin panel not working
**Solution:**
- Make sure you're using the correct URL with the secret path
- Check `key_storage.json` for correct admin key
- Clear sessionStorage and try again

### Issue: Access codes not working
**Solution:**
- Edit `access_codes.json` in GitHub
- Push changes to trigger redeploy
- Or use admin panel to manage codes

---

## 💰 Pricing (FREE Plan)

### What's Included (Free Forever):
- ✅ 100 GB bandwidth/month
- ✅ Automatic SSL certificate (HTTPS)
- ✅ Custom domains
- ✅ Automatic deploys from GitHub
- ✅ Unlimited static sites
- ✅ CDN included

### When to Upgrade:
- If you exceed 100 GB bandwidth
- If you need faster CDN
- If you need DDoS protection

---

## 🔒 Security Best Practices

1. **Change Admin Key:**
   - Edit `key_storage.json`
   - Use a strong, unique key
   - Don't share publicly

2. **Update Access Codes:**
   - Change codes regularly
   - Use complex codes (e.g., `A7xK9mP2qW4e`)
   - Distribute codes securely

3. **Secret Admin URL:**
   - Keep the `parking55009hvSweJimbs5hhinbd56y.html` URL private
   - Consider changing the filename to something more unique

4. **HTTPS:**
   - Always use HTTPS (automatic on Render)
   - Never use HTTP for sensitive data

---

## 📱 Mobile Optimization

Your site is already mobile-optimized:
- ✅ Responsive design
- ✅ Touch-friendly controls
- ✅ Mobile video player
- ✅ Adaptive layouts

---

## 🎉 You're All Set!

Your video streaming website is now live on Render!

### Next Steps:
1. ✅ Test your live site
2. ✅ Share access codes with users
3. ✅ Upload your first videos
4. ✅ Customize categories and content
5. ✅ Add custom domain (optional)

### Support:
- Render Docs: https://render.com/docs
- GitHub Issues: https://github.com/vernapark/memtop/issues

---

## 📝 Quick Reference

### URLs:
- **Main Site:** `https://memtop-video-site.onrender.com`
- **Admin Panel:** `https://memtop-video-site.onrender.com/parking55009hvSweJimbs5hhinbd56y.html`
- **GitHub Repo:** `https://github.com/vernapark/memtop`

### Files to Edit:
- `access_codes.json` - Manage access codes
- `key_storage.json` - Admin authentication
- `css/style.css` - Styling
- `js/main.js` - Video display logic
- `js/admin.js` - Admin panel logic

---

## 🚀 Happy Streaming!

Your professional video streaming platform is now live and ready to use!

Need help? Open an issue on GitHub or check Render's documentation.

---

**Last Updated:** January 2026  
**Version:** 1.0.0  
**Author:** Rovo Dev
