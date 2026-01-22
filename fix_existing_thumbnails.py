"""
Fix thumbnails for existing videos
This script updates all existing video entries with proper Cloudinary thumbnail URLs
"""
import json
import os

VIDEOS_FILE = "videos.json"

def generate_cloudinary_thumbnail(public_id, cloud_name):
    """
    Generate Cloudinary thumbnail URL for video
    Uses Cloudinary's transformation API to create a thumbnail from the video
    """
    thumbnail_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/so_1.0,w_640,h_360,c_fill,q_auto,f_jpg/{public_id}.jpg"
    return thumbnail_url

def fix_thumbnails():
    """Fix thumbnails for all existing videos"""
    
    if not os.path.exists(VIDEOS_FILE):
        print("❌ videos.json not found!")
        print("This script should be run on the server where videos are stored.")
        return
    
    # Load existing videos
    with open(VIDEOS_FILE, 'r') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    
    if not videos:
        print("ℹ️ No videos found in videos.json")
        return
    
    print(f"🔍 Found {len(videos)} videos")
    print("=" * 60)
    
    fixed_count = 0
    
    # Fix each video's thumbnail
    for video in videos:
        video_id = video.get('id') or video.get('cloudinary_id')
        cloud_name = video.get('cloudinary_cloud_name')
        old_thumbnail = video.get('thumbnail', '')
        
        if not video_id:
            print(f"⚠️ Skipping video without ID: {video.get('title', 'Unknown')}")
            continue
        
        if not cloud_name:
            print(f"⚠️ Skipping video without cloud_name: {video.get('title', 'Unknown')}")
            continue
        
        # Generate new thumbnail URL
        new_thumbnail = generate_cloudinary_thumbnail(video_id, cloud_name)
        
        # Update the video
        video['thumbnail'] = new_thumbnail
        
        print(f"✅ Fixed: {video.get('title', 'Unknown')}")
        print(f"   Old: {old_thumbnail[:80]}...")
        print(f"   New: {new_thumbnail}")
        print()
        
        fixed_count += 1
    
    # Save the updated videos
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("=" * 60)
    print(f"🎉 SUCCESS! Fixed {fixed_count} video thumbnails")
    print(f"📝 Updated videos.json")
    print()
    print("Next steps:")
    print("1. Restart your server")
    print("2. Refresh the homepage to see the thumbnails")

if __name__ == '__main__':
    print("🔧 Thumbnail Fix Script")
    print("=" * 60)
    fix_thumbnails()
