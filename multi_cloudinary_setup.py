"""
Multi-Cloudinary Account Manager
Supports multiple Cloudinary accounts for increased storage and load balancing
"""
import os
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
from aiohttp import web
import logging
import random

logger = logging.getLogger(__name__)

# Video metadata storage file
VIDEOS_FILE = "videos.json"
CLOUDINARY_ACCOUNTS_FILE = "cloudinary_accounts.json"

# ============================================================================
# MULTI-ACCOUNT CONFIGURATION
# ============================================================================

def load_cloudinary_accounts():
    """Load all configured Cloudinary accounts"""
    # First, try to load from JSON file (for multiple accounts)
    if os.path.exists(CLOUDINARY_ACCOUNTS_FILE):
        try:
            with open(CLOUDINARY_ACCOUNTS_FILE, 'r') as f:
                data = json.load(f)
                accounts = data.get('accounts', [])
                if accounts:
                    logger.info(f"âœ… Loaded {len(accounts)} Cloudinary accounts from file")
                    return accounts
        except Exception as e:
            logger.warning(f"Could not load accounts file: {e}")
    
    # Fallback: Load from environment variables (single account)
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if cloud_name and api_key and api_secret:
        logger.info("âœ… Using single Cloudinary account from environment variables")
        return [{
            "name": "Primary Account",
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
            "active": True
        }]
    
    logger.warning("âš ï¸ No Cloudinary accounts configured!")
    return []

def save_cloudinary_accounts(accounts):
    """Save Cloudinary accounts to file"""
    with open(CLOUDINARY_ACCOUNTS_FILE, 'w') as f:
        json.dump({"accounts": accounts}, f, indent=2)
    logger.info(f"ðŸ’¾ Saved {len(accounts)} Cloudinary accounts")

def get_active_accounts():
    """Get only active Cloudinary accounts"""
    accounts = load_cloudinary_accounts()
    active = [acc for acc in accounts if acc.get('active', True)]
    return active

def select_account_for_upload():
    """
    Select a Cloudinary account for upload
    Uses round-robin or random selection for load balancing
    """
    accounts = get_active_accounts()
    
    if not accounts:
        raise Exception("No active Cloudinary accounts available")
    
    # Random selection for load balancing
    selected = random.choice(accounts)
    logger.info(f"ðŸ“¤ Selected account: {selected.get('name', 'Unnamed')} for upload")
    return selected

def configure_cloudinary(account):
    """Configure Cloudinary with specific account credentials"""
    cloudinary.config(
        cloud_name=account['cloud_name'],
        api_key=account['api_key'],
        api_secret=account['api_secret']
    )

def generate_cloudinary_thumbnail(public_id, cloud_name):
    """
    Generate Cloudinary thumbnail URL for video
    Uses Cloudinary's transformation API to create a thumbnail from the video
    """
    # Generate thumbnail URL using Cloudinary transformation API
    # This creates a thumbnail at 1 second into the video, scaled to fit
    thumbnail_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/so_1.0,w_640,h_360,c_fill,q_auto,f_jpg/{public_id}.jpg"
    
    logger.info(f"🖼️ Generated thumbnail URL: {thumbnail_url}")
    return thumbnail_url

# ============================================================================
# VIDEO METADATA MANAGEMENT
# ============================================================================

def load_videos_metadata():
    """Load video metadata from JSON file"""
    if os.path.exists(VIDEOS_FILE):
        try:
            with open(VIDEOS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"videos": []}
    return {"videos": []}

def save_videos_metadata(data):
    """Save video metadata to JSON file"""
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================================================
# VIDEO UPLOAD/DELETE HANDLERS
# ============================================================================

async def upload_video(request):
    """Handle video upload to Cloudinary (with multi-account support)"""
    try:
        reader = await request.multipart()
        video_file = None
        video_data = {}
        
        # Read multipart form data
        async for field in reader:
            if field.name == 'videoFile':
                # Read video file
                video_file = await field.read()
            else:
                # Read other form fields
                value = await field.text()
                video_data[field.name] = value
        
        if not video_file:
            return web.json_response({"error": "No video file provided"}, status=400)
        
        # Select account for upload
        account = select_account_for_upload()
        configure_cloudinary(account)
        
        # Upload to Cloudinary
        logger.info(f"ðŸ“¤ Uploading video to Cloudinary ({account.get('name')}): {video_data.get('videoTitle', 'Untitled')}")
        
        # Save to temp file first (Cloudinary needs a file path)
        temp_file = f"/tmp/temp_video_{os.urandom(8).hex()}.mp4"
        with open(temp_file, 'wb') as f:
            f.write(video_file)
        
        # Upload to Cloudinary with video settings
        upload_result = cloudinary.uploader.upload(
            temp_file,
            resource_type="video",
            folder="video_streaming_site",
            overwrite=True,
            notification_url=None,
            eager=[{"streaming_profile": "full_hd", "format": "m3u8"}],
            eager_async=True
        )
        
        # Clean up temp file
        os.remove(temp_file)
        
        # Create video metadata (include which account was used)
        video_metadata = {
            "id": upload_result['public_id'],
            "title": video_data.get('videoTitle', 'Untitled'),
            "description": video_data.get('videoDescription', ''),
            "category": video_data.get('videoCategory', 'General'),
            "videoUrl": upload_result['secure_url'],
            "thumbnail": generate_cloudinary_thumbnail(upload_result['public_id'], account['cloud_name']),
            "uploadDate": upload_result['created_at'],
            "duration": upload_result.get('duration', 0),
            "cloudinary_id": upload_result['public_id'],
            "cloudinary_account": account.get('name', 'Unknown'),
            "cloudinary_cloud_name": account['cloud_name']
        }
        
        # Save metadata
        videos_data = load_videos_metadata()
        videos_data['videos'].append(video_metadata)
        save_videos_metadata(videos_data)
        
        logger.info(f"âœ… Video uploaded successfully to {account.get('name')}: {video_metadata['id']}")
        
        return web.json_response({
            "success": True,
            "message": f"Video uploaded successfully to {account.get('name')}",
            "video": video_metadata
        })
        
    except Exception as e:
        logger.error(f"âŒ Upload error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

async def get_videos(request):
    """Get all videos metadata"""
    try:
        videos_data = load_videos_metadata()
        
        # Add statistics about account usage
        accounts = load_cloudinary_accounts()
        account_stats = {}
        
        for video in videos_data.get('videos', []):
            acc_name = video.get('cloudinary_account', 'Unknown')
            account_stats[acc_name] = account_stats.get(acc_name, 0) + 1
        
        videos_data['statistics'] = {
            "total_videos": len(videos_data.get('videos', [])),
            "total_accounts": len(accounts),
            "active_accounts": len(get_active_accounts()),
            "videos_per_account": account_stats
        }
        
        return web.json_response(videos_data)
    except Exception as e:
        logger.error(f"Error getting videos: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def delete_video(request):
    """Delete video from Cloudinary and metadata"""
    try:
        data = await request.json()
        video_id = data.get('id')
        
        if not video_id:
            return web.json_response({"error": "No video ID provided"}, status=400)
        
        # Find the video to get its account info
        videos_data = load_videos_metadata()
        video_to_delete = None
        
        for video in videos_data['videos']:
            if video['id'] == video_id:
                video_to_delete = video
                break
        
        if not video_to_delete:
            return web.json_response({"error": "Video not found"}, status=404)
        
        # Configure the correct Cloudinary account
        cloud_name = video_to_delete.get('cloudinary_cloud_name')
        if cloud_name:
            # Find the account with this cloud_name
            accounts = load_cloudinary_accounts()
            account = next((acc for acc in accounts if acc['cloud_name'] == cloud_name), None)
            
            if account:
                configure_cloudinary(account)
                logger.info(f"ðŸ—‘ï¸ Deleting from account: {account.get('name')}")
            else:
                logger.warning(f"âš ï¸ Account not found for cloud_name: {cloud_name}, using first available")
                accounts = get_active_accounts()
                if accounts:
                    configure_cloudinary(accounts[0])
        
        # Delete from Cloudinary
        cloudinary.uploader.destroy(video_id, resource_type="video")
        
        # Remove from metadata
        videos_data['videos'] = [v for v in videos_data['videos'] if v['id'] != video_id]
        save_videos_metadata(videos_data)
        
        logger.info(f"âœ… Video deleted: {video_id}")
        
        return web.json_response({"success": True, "message": "Video deleted"})
        
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        return web.json_response({"error": str(e)}, status=500)

# ============================================================================
# ACCOUNT MANAGEMENT API
# ============================================================================

async def get_accounts_info(request):
    """Get information about all configured accounts"""
    try:
        accounts = load_cloudinary_accounts()
        
        # Don't expose API secrets in response
        safe_accounts = []
        for acc in accounts:
            safe_accounts.append({
                "name": acc.get('name', 'Unnamed'),
                "cloud_name": acc['cloud_name'],
                "active": acc.get('active', True),
                "api_key": acc['api_key'][:4] + "****" + acc['api_key'][-4:] if len(acc.get('api_key', '')) > 8 else "****"
            })
        
        videos_data = load_videos_metadata()
        account_stats = {}
        
        for video in videos_data.get('videos', []):
            acc_name = video.get('cloudinary_account', 'Unknown')
            account_stats[acc_name] = account_stats.get(acc_name, 0) + 1
        
        return web.json_response({
            "accounts": safe_accounts,
            "total_accounts": len(accounts),
            "active_accounts": len(get_active_accounts()),
            "videos_per_account": account_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting accounts info: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def add_account(request):
    """Add a new Cloudinary account"""
    try:
        data = await request.json()
        
        required_fields = ['cloud_name', 'api_key', 'api_secret']
        for field in required_fields:
            if field not in data:
                return web.json_response({"error": f"Missing field: {field}"}, status=400)
        
        accounts = load_cloudinary_accounts()
        
        # Check for duplicate cloud_name
        if any(acc['cloud_name'] == data['cloud_name'] for acc in accounts):
            return web.json_response({"error": "Account with this cloud_name already exists"}, status=400)
        
        new_account = {
            "name": data.get('name', f"Account {len(accounts) + 1}"),
            "cloud_name": data['cloud_name'],
            "api_key": data['api_key'],
            "api_secret": data['api_secret'],
            "active": data.get('active', True)
        }
        
        accounts.append(new_account)
        save_cloudinary_accounts(accounts)
        
        logger.info(f"âœ… Added new Cloudinary account: {new_account['name']}")
        
        return web.json_response({
            "success": True,
            "message": f"Account '{new_account['name']}' added successfully",
            "total_accounts": len(accounts)
        })
        
    except Exception as e:
        logger.error(f"Error adding account: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def toggle_account(request):
    """Enable/disable a Cloudinary account"""
    try:
        data = await request.json()
        cloud_name = data.get('cloud_name')
        
        if not cloud_name:
            return web.json_response({"error": "cloud_name is required"}, status=400)
        
        accounts = load_cloudinary_accounts()
        account_found = False
        
        for acc in accounts:
            if acc['cloud_name'] == cloud_name:
                acc['active'] = not acc.get('active', True)
                account_found = True
                logger.info(f"ðŸ”„ Account '{acc.get('name')}' is now {'active' if acc['active'] else 'inactive'}")
                break
        
        if not account_found:
            return web.json_response({"error": "Account not found"}, status=404)
        
        save_cloudinary_accounts(accounts)
        
        return web.json_response({
            "success": True,
            "message": "Account status updated"
        })
        
    except Exception as e:
        logger.error(f"Error toggling account: {e}")
        return web.json_response({"error": str(e)}, status=500)


