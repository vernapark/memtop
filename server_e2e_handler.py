"""
Server-side handler for E2E encrypted videos
Server remains blind to video content - only handles encrypted blobs
Uses aiohttp (async) framework
"""

import os
import json
import time
import hashlib
from aiohttp import web
import cloudinary
import cloudinary.uploader
from datetime import datetime

class E2EVideoHandler:
    """
    Handles encrypted video uploads and retrieval
    Server never sees unencrypted content
    """
    
    def __init__(self):
        self.allowed_extensions = {'enc', 'encrypted', 'mp4', 'webm', 'avi', 'mov'}
        
    def is_allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_video_id(self):
        """Generate unique video ID"""
        timestamp = str(time.time())
        random_data = os.urandom(16)
        unique_string = timestamp + random_data.hex()
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    async def handle_encrypted_upload(self, request):
        """
        Handle encrypted video upload
        Server stores encrypted blob without decryption
        """
        try:
            # Get multipart data
            reader = await request.multipart()
            
            video_file = None
            encrypted = False
            metadata = {}
            title = 'Encrypted Video'
            description = ''
            
            # Read form data
            async for field in reader:
                if field.name == 'video':
                    video_file = await field.read()
                    filename = field.filename
                elif field.name == 'encrypted':
                    encrypted = (await field.text()) == 'true'
                elif field.name == 'metadata':
                    try:
                        metadata = json.loads(await field.text())
                    except:
                        metadata = {}
                elif field.name == 'title':
                    title = await field.text()
                elif field.name == 'description':
                    description = await field.text()
            
            if not video_file:
                return web.json_response({'error': 'No video file provided'}, status=400)
            
            # Generate unique video ID
            video_id = self.generate_video_id()
            
            # Prepare filename (keep it anonymous)
            if encrypted:
                filename = f"encrypted_{video_id}.enc"
            
            # Upload to Cloudinary (still encrypted!)
            # Save to temp file first
            temp_path = f"/tmp/{filename}"
            with open(temp_path, 'wb') as f:
                f.write(video_file)
            
            cloudinary_response = cloudinary.uploader.upload(
                temp_path,
                resource_type="raw",  # Important: raw upload for encrypted files
                public_id=f"memtop/encrypted/{video_id}",
                folder="memtop/encrypted",
                format="enc",
                overwrite=True,
                tags=['encrypted', 'e2e', 'memtop']
            )
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Store video info in database
            video_info = {
                'video_id': video_id,
                'cloudinary_url': cloudinary_response.get('secure_url'),
                'cloudinary_public_id': cloudinary_response.get('public_id'),
                'title': title,
                'description': description,
                'encrypted': encrypted,
                'filename': filename,
                'upload_timestamp': datetime.now().isoformat(),
                'size': cloudinary_response.get('bytes', 0),
                'original_size': metadata.get('originalSize', 0),
                'algorithm': metadata.get('algorithm', 'AES-256-GCM'),
            }
            
            # Save to database
            self.save_video_to_db(video_info)
            
            return web.json_response({
                'success': True,
                'video_id': video_id,
                'message': 'Encrypted video uploaded successfully',
                'encrypted': encrypted,
                'size': video_info['size']
            })
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return web.json_response({
                'error': 'Upload failed',
                'message': str(e)
            }, status=500)
    
    async def handle_encrypted_download(self, request):
        """
        Serve encrypted video for client-side decryption
        Server just passes through the encrypted blob
        """
        try:
            video_id = request.match_info.get('video_id')
            
            # Get video info from database
            video_info = self.get_video_from_db(video_id)
            
            if not video_info:
                return web.json_response({'error': 'Video not found'}, status=404)
            
            # Get encrypted video URL from Cloudinary
            cloudinary_url = video_info.get('cloudinary_url')
            
            if not cloudinary_url:
                return web.json_response({'error': 'Video URL not found'}, status=404)
            
            # Return encrypted video info
            return web.json_response({
                'success': True,
                'video_id': video_id,
                'url': cloudinary_url,
                'encrypted': video_info.get('encrypted', True),
                'size': video_info.get('size', 0),
                'title': video_info.get('title', 'Encrypted Video')
            })
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return web.json_response({
                'error': 'Failed to retrieve video',
                'message': str(e)
            }, status=500)
    
    async def get_encrypted_videos_list(self, request):
        """
        Get list of encrypted videos
        Returns only non-sensitive metadata
        """
        try:
            videos = self.get_all_videos_from_db()
            
            # Filter to only return safe metadata
            safe_videos = []
            for video in videos:
                safe_videos.append({
                    'video_id': video.get('video_id'),
                    'title': video.get('title'),
                    'description': video.get('description'),
                    'encrypted': video.get('encrypted', False),
                    'upload_timestamp': video.get('upload_timestamp'),
                    'size': video.get('size', 0),
                    'thumbnail': video.get('thumbnail', '/static/encrypted_thumbnail.png')
                })
            
            return web.json_response({
                'success': True,
                'videos': safe_videos,
                'count': len(safe_videos)
            })
            
        except Exception as e:
            print(f"List error: {str(e)}")
            return web.json_response({
                'error': 'Failed to retrieve videos',
                'message': str(e)
            }, status=500)
    
    async def delete_encrypted_video(self, request):
        """
        Delete encrypted video from storage and database
        """
        try:
            video_id = request.match_info.get('video_id')
            
            # Get video info
            video_info = self.get_video_from_db(video_id)
            
            if not video_info:
                return web.json_response({'error': 'Video not found'}, status=404)
            
            # Delete from Cloudinary
            public_id = video_info.get('cloudinary_public_id')
            if public_id:
                cloudinary.uploader.destroy(public_id, resource_type="raw")
            
            # Delete from database
            self.delete_video_from_db(video_id)
            
            return web.json_response({
                'success': True,
                'message': 'Video deleted successfully'
            })
            
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return web.json_response({
                'error': 'Failed to delete video',
                'message': str(e)
            }, status=500)
    
    # Database methods
    def save_video_to_db(self, video_info):
        """Save video info to database"""
        db_file = 'memtop_encrypted_videos.json'
        
        try:
            if os.path.exists(db_file):
                with open(db_file, 'r') as f:
                    videos = json.load(f)
            else:
                videos = []
            
            videos.append(video_info)
            
            with open(db_file, 'w') as f:
                json.dump(videos, f, indent=2)
                
        except Exception as e:
            print(f"Database save error: {str(e)}")
    
    def get_video_from_db(self, video_id):
        """Get video info from database"""
        db_file = 'memtop_encrypted_videos.json'
        
        try:
            if not os.path.exists(db_file):
                return None
            
            with open(db_file, 'r') as f:
                videos = json.load(f)
            
            for video in videos:
                if video.get('video_id') == video_id:
                    return video
            
            return None
            
        except Exception as e:
            print(f"Database get error: {str(e)}")
            return None
    
    def get_all_videos_from_db(self):
        """Get all videos from database"""
        db_file = 'memtop_encrypted_videos.json'
        
        try:
            if not os.path.exists(db_file):
                return []
            
            with open(db_file, 'r') as f:
                videos = json.load(f)
            
            return videos
            
        except Exception as e:
            print(f"Database list error: {str(e)}")
            return []
    
    def delete_video_from_db(self, video_id):
        """Delete video from database"""
        db_file = 'memtop_encrypted_videos.json'
        
        try:
            if not os.path.exists(db_file):
                return
            
            with open(db_file, 'r') as f:
                videos = json.load(f)
            
            videos = [v for v in videos if v.get('video_id') != video_id]
            
            with open(db_file, 'w') as f:
                json.dump(videos, f, indent=2)
                
        except Exception as e:
            print(f"Database delete error: {str(e)}")


def register_e2e_routes(app, handler):
    """"""
    Register E2E encryption routes with aiohttp app
    """"""
    # Routes are registered in combined_server_e2e.py directly
    # This function exists for compatibility
    pass
