# Cloudinary Setup Guide

## Why Cloudinary?
Your videos were being deleted on every deployment because Render uses **ephemeral storage** - the filesystem resets on each deploy. Cloudinary provides persistent cloud storage so your videos will **never be deleted again**.

## Free Tier Benefits
- ✅ 25GB storage
- ✅ 25GB monthly bandwidth
- ✅ Unlimited video uploads
- ✅ Videos persist forever across all deployments
- ✅ Fast CDN delivery

## Setup Steps

### 1. Create Cloudinary Account (Free)
1. Go to: https://cloudinary.com/users/register_free
2. Sign up with your email
3. Verify your email
4. Login to your dashboard

### 2. Get Your Credentials
Once logged in, you'll see your dashboard with these credentials:

```
Cloud Name: [your_cloud_name]
API Key: [your_api_key]
API Secret: [your_api_secret]
```

### 3. Add to Render Environment Variables
1. Go to your Render dashboard: https://dashboard.render.com
2. Select your `memtop-video-streaming` service
3. Go to "Environment" tab
4. Add these 3 environment variables:

```
CLOUDINARY_CLOUD_NAME = your_cloud_name_here
CLOUDINARY_API_KEY = your_api_key_here
CLOUDINARY_API_SECRET = your_api_secret_here
```

4. Click "Save Changes"
5. Render will automatically redeploy

### 4. Re-upload Your Videos
After deployment completes:
1. Go to your admin panel: https://memtop-video-streaming.onrender.com/parking55009hvSweJimbs5hhinbd56y
2. Login with your admin key
3. Upload your videos again - they will now be stored in Cloudinary
4. Videos will NEVER be deleted on future deployments! ✅

## How It Works Now

### Before (IndexedDB - Browser Storage)
- ❌ Videos stored in user's browser only
- ❌ Lost when browser cache cleared
- ❌ Not shared across devices
- ❌ Limited storage (varies by browser)

### After (Cloudinary - Cloud Storage)
- ✅ Videos stored in cloud permanently
- ✅ Available on all devices
- ✅ Survives all deployments
- ✅ 25GB free storage
- ✅ Fast CDN delivery worldwide

## File Structure Changes

### New Files:
- `cloudinary_setup.py` - Handles video uploads to Cloudinary
- `videos.json` - Stores video metadata (persists with git repo)

### Modified Files:
- `combined_server.py` - Added API routes for video management
- `js/admin.js` - Updated to use API instead of IndexedDB
- `js/main.js` - Updated to load videos from API
- `requirements.txt` - Added cloudinary library
- `render.yaml` - Added Cloudinary env vars

## Testing

### Upload Test:
1. Upload a video through admin panel
2. Check Cloudinary dashboard - video should appear in "Media Library"
3. Video URL will be like: `https://res.cloudinary.com/[your-cloud-name]/video/upload/...`

### Persistence Test:
1. Upload a video
2. Trigger a manual deploy on Render
3. After deployment, video should still be visible ✅

## Troubleshooting

### "Upload failed" error
- Check if Cloudinary credentials are correct in Render
- Verify you haven't exceeded free tier limit (25GB)

### Videos not showing
- Check browser console for errors
- Verify `/api/videos` endpoint returns data
- Check `videos.json` file exists

### Old videos (from IndexedDB)
- Old videos were stored in browser only, not server
- You'll need to re-upload them to Cloudinary
- They'll now persist forever!

## Support
If you need help, check:
- Cloudinary docs: https://cloudinary.com/documentation
- Render logs: Dashboard > Logs tab
