# Multi-Cloudinary Account Setup Guide

## Overview
This setup allows you to use **multiple Cloudinary accounts** to increase your total storage capacity and distribute load across accounts.

## Benefits
✅ **Increased Storage**: Combine free tier storage from multiple accounts  
✅ **Load Balancing**: Automatically distributes videos across accounts  
✅ **Redundancy**: If one account has issues, others continue working  
✅ **Easy Management**: Enable/disable accounts without deleting videos  

---

## Setup Instructions

### Method 1: Using JSON File (Recommended for Multiple Accounts)

1. **Edit `cloudinary_accounts.json`**:
```json
{
  "accounts": [
    {
      "name": "Primary Account",
      "cloud_name": "your_cloud_name_1",
      "api_key": "your_api_key_1",
      "api_secret": "your_api_secret_1",
      "active": true
    },
    {
      "name": "Secondary Account",
      "cloud_name": "your_cloud_name_2",
      "api_key": "your_api_key_2",
      "api_secret": "your_api_secret_2",
      "active": true
    }
  ]
}
```

2. **Add your Cloudinary credentials** for each account
3. **Upload to Render.com** or your hosting platform
4. The system will automatically use all active accounts

### Method 2: Environment Variables (Single Account Fallback)

If `cloudinary_accounts.json` doesn't exist, the system falls back to environment variables:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## How to Get Multiple Cloudinary Accounts

### Option 1: Free Accounts (Recommended)
1. Sign up for Cloudinary free tier: https://cloudinary.com/users/register/free
2. Each free account gets **25GB storage + 25GB bandwidth/month**
3. Create multiple accounts with different emails
4. Copy credentials (Cloud Name, API Key, API Secret) for each

### Option 2: Paid Accounts
- Upgrade accounts for more storage as needed
- Mix free and paid accounts

---

## Integration with Your Project

### Update `combined_server.py`

Replace the cloudinary import line:
```python
# OLD
from cloudinary_setup import upload_video, get_videos, delete_video

# NEW
from multi_cloudinary_setup import upload_video, get_videos, delete_video
```

### Or Use the Enhanced Combined Server

I'll create an updated version that includes account management features.

---

## How It Works

### Upload Process
1. User uploads a video through admin panel
2. System randomly selects an **active** Cloudinary account
3. Video uploads to that account
4. Metadata saved includes which account was used
5. Video is accessible from any account

### Delete Process
1. System checks which account the video is stored in
2. Configures correct account credentials
3. Deletes video from the correct account

### Load Balancing
- **Random selection**: Each upload picks a random active account
- This naturally distributes videos across all accounts
- You can manually manage distribution if needed

---

## API Endpoints (New)

### Get Account Information
```
GET /api/cloudinary-accounts
```
Returns information about all configured accounts and usage statistics

**Response:**
```json
{
  "accounts": [
    {
      "name": "Primary Account",
      "cloud_name": "xxxxx",
      "active": true,
      "api_key": "1234****5678"
    }
  ],
  "total_accounts": 3,
  "active_accounts": 2,
  "videos_per_account": {
    "Primary Account": 15,
    "Secondary Account": 12
  }
}
```

### Add New Account
```
POST /api/cloudinary-accounts/add
Content-Type: application/json

{
  "name": "New Account",
  "cloud_name": "your_cloud_name",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret",
  "active": true
}
```

### Enable/Disable Account
```
POST /api/cloudinary-accounts/toggle
Content-Type: application/json

{
  "cloud_name": "your_cloud_name"
}
```

---

## Storage Calculation

### Example: 3 Free Cloudinary Accounts
- Account 1: 25GB
- Account 2: 25GB  
- Account 3: 25GB
- **Total: 75GB storage**

### With Mixed Accounts
- 2 Free accounts: 50GB
- 1 Paid (100GB): 100GB
- **Total: 150GB storage**

---

## Important Notes

⚠️ **Account Credentials Security**
- Keep `cloudinary_accounts.json` secure
- Don't commit it to public repositories
- Use environment variables on Render.com for production

⚠️ **Deletion**
- Videos track which account they're stored in
- Deleting a video requires access to that specific account
- Don't delete accounts that still have videos

⚠️ **Bandwidth Limits**
- Each Cloudinary account has bandwidth limits
- Free tier: 25GB/month per account
- Monitor usage in Cloudinary dashboard

---

## Testing

1. **Add test accounts** to `cloudinary_accounts.json`
2. **Upload a few videos** - check which accounts they go to
3. **View statistics** at `/api/cloudinary-accounts`
4. **Try disabling** an account and upload again
5. **Delete videos** - ensure they delete from correct account

---

## Migration from Single Account

If you're already using a single account:

1. **Keep existing account** as "Primary Account" in JSON
2. **Add new accounts** for additional storage
3. **Existing videos** continue working on the original account
4. **New uploads** distribute across all accounts

Your existing `videos.json` will work fine - new videos will include the account name.

---

## Troubleshooting

### "No active Cloudinary accounts available"
- Check that at least one account is set to `"active": true`
- Verify credentials are correct in `cloudinary_accounts.json`

### Videos not uploading
- Check Cloudinary credentials for all accounts
- Verify API keys are valid
- Check storage limits on each account

### Can't delete video
- Ensure the account that video was uploaded to still exists
- Check account credentials are still valid

---

## Need Help?

Would you like me to:
1. Create an admin UI to manage accounts?
2. Add automatic failover if one account is full?
3. Implement smart distribution based on storage usage?
4. Create a migration script for existing videos?
