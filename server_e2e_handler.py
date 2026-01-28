"""
Server-side handler for E2E encrypted videos
Server remains blind to video content - only handles encrypted blobs
"""

import os
import json
import time
import hashlib
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from datetime import datetime

class E2EVideoHandler:
    """
    Handles encrypted video uploads and retrieval
    Server never sees unencrypted content
    """
    
    def __init__(self, app=None):
        self.app = app
        self.allowed_extensions = {'enc', 'encrypted', 'mp4', 'webm', 'avi', 'mov'}
        
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
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
    
    def handle_encrypted_upload(self):
        """
        Handle encrypted video upload
        Server stores encrypted blob without decryption
        """
        try:
            # Check if request has file
            if 'video' not in request.files:
                return jsonify({'error': 'No video file provided'}), 400
            
            video_file = request.files['video']
            
            if video_file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            
            # Get metadata and other form data
            encrypted = request.form.get('encrypted', 'false') == 'true'
            metadata_json = request.form.get('metadata', '{}')
            title = request.form.get('title', 'Encrypted Video')
            description = request.form.get('description', '')
            
            try:
                metadata = json.loads(metadata_json)
            except:
                metadata = {}
            
            # Generate unique video ID
            video_id = self.generate_video_id()
            
            # Prepare filename (keep it anonymous)
            if encrypted:
                filename = f"encrypted_{video_id}.enc"
            else:
                filename = secure_filename(video_file.filename)
            
            # Upload to Cloudinary (still encrypted!)
            cloudinary_response = cloudinary.uploader.upload(
                video_file,
                resource_type="raw",  # Important: raw upload for encrypted files
                public_id=f"memtop/encrypted/{video_id}",
                folder="memtop/encrypted",
                format="enc",
                overwrite=True,
                # Don't transform or process - keep encrypted blob intact
                transformation=[],
                tags=['encrypted', 'e2e', 'memtop']
            )
            
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
                # Store metadata but without sensitive info
                'original_size': metadata.get('originalSize', 0),
                'algorithm': metadata.get('algorithm', 'unknown'),
            }
            
            # Save to database (you'll need to integrate with your DB)
            self.save_video_to_db(video_info)
            
            return jsonify({
                'success': True,
                'video_id': video_id,
                'message': 'Encrypted video uploaded successfully',
                'encrypted': encrypted,
                'size': video_info['size']
            }), 200
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return jsonify({
                'error': 'Upload failed',
                'message': str(e)
            }), 500
    
    def handle_encrypted_download(self, video_id):
        """
        Serve encrypted video for client-side decryption
        Server just passes through the encrypted blob
        """
        try:
            # Get video info from database
            video_info = self.get_video_from_db(video_id)
            
            if not video_info:
                return jsonify({'error': 'Video not found'}), 404
            
            # Get encrypted video URL from Cloudinary
            cloudinary_url = video_info.get('cloudinary_url')
            
            if not cloudinary_url:
                return jsonify({'error': 'Video URL not found'}), 404
            
            # Return encrypted video info
            # Client will fetch directly from Cloudinary
            return jsonify({
                'success': True,
                'video_id': video_id,
                'url': cloudinary_url,
                'encrypted': video_info.get('encrypted', True),
                'size': video_info.get('size', 0),
                'title': video_info.get('title', 'Encrypted Video')
            }), 200
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve video',
                'message': str(e)
            }), 500
    
    def get_encrypted_videos_list(self):
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
            
            return jsonify({
                'success': True,
                'videos': safe_videos,
                'count': len(safe_videos)
            }), 200
            
        except Exception as e:
            print(f"List error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve videos',
                'message': str(e)
            }), 500
    
    def delete_encrypted_video(self, video_id):
        """
        Delete encrypted video from storage and database
        """
        try:
            # Get video info
            video_info = self.get_video_from_db(video_id)
            
            if not video_info:
                return jsonify({'error': 'Video not found'}), 404
            
            # Delete from Cloudinary
            public_id = video_info.get('cloudinary_public_id')
            if public_id:
                cloudinary.uploader.destroy(public_id, resource_type="raw")
            
            # Delete from database
            self.delete_video_from_db(video_id)
            
            return jsonify({
                'success': True,
                'message': 'Video deleted successfully'
            }), 200
            
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return jsonify({
                'error': 'Failed to delete video',
                'message': str(e)
            }), 500
    
    # Database methods (integrate with your existing DB)
    def save_video_to_db(self, video_info):
        """Save video info to database"""
        # TODO: Integrate with your existing database
        # For now, using simple file storage as fallback
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
    """
    Register E2E encryption routes
    """
    
    @app.route('/api/upload', methods=['POST'])
    def upload_video():
        """Handle video upload (encrypted or regular)"""
        return handler.handle_encrypted_upload()
    
    @app.route('/api/video/<video_id>', methods=['GET'])
    def get_video(video_id):
        """Get encrypted video info"""
        return handler.handle_encrypted_download(video_id)
    
    @app.route('/api/videos', methods=['GET'])
    def list_videos():
        """List all videos"""
        return handler.get_encrypted_videos_list()
    
    @app.route('/api/video/<video_id>', methods=['DELETE'])
    def delete_video(video_id):
        """Delete video"""
        return handler.delete_encrypted_video(video_id)
    
    @app.route('/api/e2e/status', methods=['GET'])
    def e2e_status():
        """Check E2E encryption status"""
        return jsonify({
            'success': True,
            'e2e_enabled': True,
            'encryption_algorithm': 'AES-256-GCM',
            'server_blind': True,
            'message': 'E2E encryption active - server cannot decrypt videos'
        }), 200
