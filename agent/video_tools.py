"""
Video Processing Tools for Gaming Highlights Agent

Custom MCP tools that wrap FFmpeg functionality for the Claude agent.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import yaml


class VideoTools:
    """Collection of video processing tools for the agent."""

    def __init__(self, config_path: str = "./config.yml"):
        """Initialize video tools with configuration."""
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Default config
            return {
                'gaming_highlights': {
                    'scene_detection': {
                        'threshold': 0.3,
                        'min_duration': 2.0,
                        'max_duration': 60.0
                    },
                    'output': {
                        'clips_dir': './output/clips',
                        'metadata_dir': './output/metadata',
                        'default_count': 3
                    }
                }
            }

    def get_video_metadata(self, video_path: str) -> Dict:
        """
        Get video metadata using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with duration, resolution, codec info
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration:stream=width,height,codec_name',
                '-of', 'json',
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # Extract relevant info
            duration = float(data.get('format', {}).get('duration', 0))
            streams = data.get('streams', [])
            video_stream = next((s for s in streams if 'width' in s), {})

            return {
                'duration': duration,
                'width': video_stream.get('width', 0),
                'height': video_stream.get('height', 0),
                'codec': video_stream.get('codec_name', 'unknown'),
                'path': video_path,
                'exists': True
            }

        except subprocess.CalledProcessError as e:
            return {
                'error': f'FFprobe failed: {e.stderr}',
                'exists': False
            }
        except Exception as e:
            return {
                'error': str(e),
                'exists': False
            }

    def detect_scenes(self, video_path: str, max_scenes: int = 100) -> List[Dict]:
        """
        Detect scene changes in video using FFmpeg.

        Args:
            video_path: Path to video file
            max_scenes: Maximum number of scenes to return

        Returns:
            List of scene dictionaries with start/end timestamps
        """
        try:
            # Get video duration first
            metadata = self.get_video_metadata(video_path)
            duration = metadata.get('duration', 0)

            if not metadata.get('exists'):
                return []

            # Use FFprobe to detect keyframes (scene changes)
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'packet=pts_time,flags',
                '-of', 'csv',
                '-select_streams', 'v:0',
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse keyframe timestamps
            timestamps = []
            for line in result.stdout.strip().split('\n'):
                if 'K' in line:  # Keyframe flag
                    parts = line.split(',')
                    if len(parts) >= 2:
                        try:
                            pts_time = float(parts[1])
                            timestamps.append(pts_time)
                        except (ValueError, IndexError):
                            continue

            # Limit and add boundaries
            timestamps = sorted(set(timestamps))[:max_scenes]
            if not timestamps or timestamps[0] != 0:
                timestamps.insert(0, 0.0)
            if duration not in timestamps:
                timestamps.append(duration)

            # Build scene list
            scenes = []
            config = self.config.get('gaming_highlights', {}).get('scene_detection', {})
            min_dur = config.get('min_duration', 2.0)
            max_dur = config.get('max_duration', 60.0)

            for i in range(len(timestamps) - 1):
                start = timestamps[i]
                end = timestamps[i + 1]
                scene_duration = end - start

                # Filter by duration
                if min_dur <= scene_duration <= max_dur:
                    scenes.append({
                        'index': len(scenes),
                        'start': start,
                        'end': end,
                        'duration': scene_duration,
                        'mid_point': (start + end) / 2
                    })

            # Fallback: if no scenes detected, split video into equal chunks
            if not scenes and duration > 0:
                chunk_duration = min(15.0, duration / 5)  # 15s chunks or 5 equal parts
                num_chunks = max(3, int(duration / chunk_duration))

                for i in range(num_chunks):
                    start = i * chunk_duration
                    end = min((i + 1) * chunk_duration, duration)
                    scene_duration = end - start

                    if scene_duration >= 1.0:  # At least 1 second
                        scenes.append({
                            'index': i,
                            'start': start,
                            'end': end,
                            'duration': scene_duration,
                            'mid_point': (start + end) / 2
                        })

            return scenes

        except Exception as e:
            print(f"Error detecting scenes: {str(e)}")
            return []

    def extract_frame(self, video_path: str, timestamp: float, output_path: str) -> bool:
        """
        Extract a single frame from video at specified timestamp.

        Args:
            video_path: Path to video file
            timestamp: Time in seconds
            output_path: Where to save the frame

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                '-y',  # Overwrite
                output_path,
                '-loglevel', 'error'
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return os.path.exists(output_path)

        except Exception as e:
            print(f"Error extracting frame: {str(e)}")
            return False

    def extract_clip(
        self,
        video_path: str,
        start_time: float,
        duration: float,
        output_path: str,
        use_copy_codec: bool = True
    ) -> bool:
        """
        Extract a clip from video.

        Args:
            video_path: Path to source video
            start_time: Start time in seconds
            duration: Duration in seconds
            output_path: Where to save the clip
            use_copy_codec: If True, use fast stream copy (no re-encode)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if use_copy_codec:
                cmd = [
                    'ffmpeg',
                    '-ss', str(start_time),
                    '-i', video_path,
                    '-t', str(duration),
                    '-c', 'copy',
                    '-y',
                    output_path,
                    '-loglevel', 'error'
                ]
            else:
                # Re-encode for better accuracy
                cmd = [
                    'ffmpeg',
                    '-ss', str(start_time),
                    '-i', video_path,
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-y',
                    output_path,
                    '-loglevel', 'error'
                ]

            subprocess.run(cmd, check=True, capture_output=True)
            return os.path.exists(output_path)

        except Exception as e:
            print(f"Error extracting clip: {str(e)}")
            return False

    def save_metadata(self, metadata: Dict, output_path: str) -> bool:
        """
        Save processing metadata to JSON file.

        Args:
            metadata: Dictionary to save
            output_path: Path to JSON file

        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving metadata: {str(e)}")
            return False


# Simple test
if __name__ == "__main__":
    tools = VideoTools()

    # Test with a video if available
    test_video = "./videos/apex-legends.mp4"
    if os.path.exists(test_video):
        print(f"Testing with {test_video}")

        print("\n1. Getting metadata...")
        metadata = tools.get_video_metadata(test_video)
        print(json.dumps(metadata, indent=2))

        print("\n2. Detecting scenes...")
        scenes = tools.detect_scenes(test_video, max_scenes=10)
        print(f"Found {len(scenes)} scenes")
        for scene in scenes[:3]:
            print(f"  Scene {scene['index']}: {scene['start']:.1f}s - {scene['end']:.1f}s ({scene['duration']:.1f}s)")
    else:
        print(f"Test video not found: {test_video}")
        print("Skipping tests")
