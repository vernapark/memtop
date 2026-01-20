"""
Cloudinary Video Upload API for Video Streaming Site
Handles video uploads to Cloudinary for persistent storage
"""
import os
import json
import cloudinary
import cloudinary.uploader
import cloudinary.api
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Video metadata storage file
VIDEOS_FILE = "videos.json"

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

async def upload_video(request):
    """Handle video upload to Cloudinary"""
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
        
        # Upload to Cloudinary
        logger.info(f"Uploading video to Cloudinary: {video_data.get('videoTitle', 'Untitled')}")
        
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
        
        # Create video metadata
        video_metadata = {
            "id": upload_result['public_id'],
            "title": video_data.get('videoTitle', 'Untitled'),
            "description": video_data.get('videoDescription', ''),
            "category": video_data.get('videoCategory', 'General'),
            "videoUrl": upload_result['secure_url'],
            "thumbnail": upload_result.get('thumbnail_url', upload_result['secure_url'].replace('.mp4', '.jpg')),
            "uploadDate": upload_result['created_at'],
            "duration": upload_result.get('duration', 0),
            "cloudinary_id": upload_result['public_id']
        }
        
        # Save metadata
        videos_data = load_videos_metadata()
        videos_data['videos'].append(video_metadata)
        save_videos_metadata(videos_data)
        
        logger.info(f"✅ Video uploaded successfully: {video_metadata['id']}")
        
        return web.json_response({
            "success": True,
            "message": "Video uploaded successfully",
            "video": video_metadata
        })
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

async def get_videos(request):
    """Get all videos metadata"""
    try:
        videos_data = load_videos_metadata()
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
        
        # Delete from Cloudinary
        cloudinary.uploader.destroy(video_id, resource_type="video")
        
        # Remove from metadata
        videos_data = load_videos_metadata()
        videos_data['videos'] = [v for v in videos_data['videos'] if v['id'] != video_id]
        save_videos_metadata(videos_data)
        
        logger.info(f"✅ Video deleted: {video_id}")
        
        return web.json_response({"success": True, "message": "Video deleted"})
        
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        return web.json_response({"error": str(e)}, status=500)
