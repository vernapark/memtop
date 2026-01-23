# APK Download Setup Guide

## Overview
The website now has a "Download App" button in the header that allows users to download the Android APK file.

## How it Works

### Frontend
- **Location**: `home.html` header, next to the search bar
- **Button**: Premium-styled button with download icon
- **Responsive**: Shows full text on desktop, abbreviated on mobile

### Backend
- **API Endpoint**: `/api/get-app-info` - Returns APK availability and info
- **Download Endpoint**: `/download-app` - Serves the APK file
- **File Location**: `app.apk` in the root directory

## Setup Instructions

### To Enable APK Downloads:

1. **Place your APK file** in the root directory of the project and name it `app.apk`
   ```bash
   # Example: Copy your APK to the project root
   cp /path/to/your/PremiumApp.apk memtop/app.apk
   ```

2. **The download will automatically work** once the file is present
   - Users will see the "Download App" button
   - Clicking it will download the APK as "PremiumApp.apk"

3. **If no APK is present**:
   - Users will see an alert: "App is not available for download at the moment"
   - No errors will occur - it degrades gracefully

## File Structure
```
memtop/
├── app.apk                          # Place your APK here (gitignored)
├── home.html                        # Contains download button
├── combined_server_bulletproof_multi.py  # Handles APK serving
└── APK_SETUP.md                     # This file
```

## Testing

1. Place an APK file at `memtop/app.apk`
2. Start the server: `python combined_server_bulletproof_multi.py`
3. Navigate to the home page
4. Click "Download App" button in the header
5. APK should download to your device

## Production Deployment

When deploying to Render.com:
- The `app.apk` file must be committed to the repository, OR
- Upload it directly to the Render server after deployment, OR
- Use Cloudinary/S3 to host the APK and modify the endpoint accordingly

## Notes
- APK file is in `.gitignore` by default for security
- Maximum file size depends on your hosting limits
- Consider using cloud storage (Cloudinary) for large APK files
