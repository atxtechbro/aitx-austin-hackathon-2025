#!/usr/bin/env python3
"""
Gaming Highlights Autonomous Agent

Nemotron-powered agent that decides which tools to use to extract highlights.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

from nemotron_client import NemotronAgent, analyze_scene_with_nemotron
from video_tools import VideoTools


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Gaming Highlights Agent")
    parser.add_argument("video_path", help="Path to video file")
    parser.add_argument("--count", type=int, default=3, help="Number of clips")
    args = parser.parse_args()

    # Load environment
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found in .env")
        print("   Get your key from: https://build.nvidia.com/")
        sys.exit(1)

    # Setup
    video_path = args.video_path
    video_name = Path(video_path).stem
    clips_dir = Path(f"./output/clips/{video_name}")
    clips_dir.mkdir(parents=True, exist_ok=True)

    video_tools = VideoTools()

    # Verify video exists
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🎬 Processing: {video_path}")
    print(f"{'='*60}\n")

    # Shared state for tools
    state = {
        "video_path": video_path,
        "video_name": video_name,
        "clips_dir": str(clips_dir),
        "api_key": api_key,
        "video_tools": video_tools,
        "scenes": None,
        "analyzed_scenes": [],
        "extracted_clips": []
    }

    # Define tools that Nemotron can use
    tools = {
        "get_video_info": {
            "description": "Get video metadata (duration, resolution, codec)",
            "params": {},
            "function": lambda: tool_get_video_info(state)
        },
        "detect_scenes": {
            "description": "Detect scene changes in the video",
            "params": {},
            "function": lambda: tool_detect_scenes(state)
        },
        "analyze_scene": {
            "description": "Analyze a specific scene for highlight worthiness",
            "params": {"scene_index": "int"},
            "function": lambda scene_index: tool_analyze_scene(state, scene_index)
        },
        "extract_clip": {
            "description": "Extract a video clip for a scene",
            "params": {"scene_index": "int", "rank": "int"},
            "function": lambda scene_index, rank: tool_extract_clip(state, scene_index, rank)
        }
    }

    # Run autonomous agent
    goal = f"Extract the top {args.count} gaming highlight clips from the video. Analyze scenes, score them, and extract the best ones."

    agent = NemotronAgent(api_key)
    history = agent.run(goal=goal, tools=tools, max_iterations=30)

    # Print summary
    print(f"\n{'='*60}")
    print(f"🎉 Agent completed!")
    print(f"{'='*60}\n")

    clips = state['extracted_clips']
    if clips:
        print(f"📁 Extracted {len(clips)} clips:")
        for clip in clips:
            print(f"   {clip['rank']}. {clip['file']} (score: {clip['score']}/100)")
        print(f"\n   Saved to: {clips_dir}")
    else:
        print("⚠️  No clips extracted")

    # Save metadata
    metadata_dir = Path(f"./output/metadata/{video_name}")
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_file = metadata_dir / "metadata.json"

    with open(metadata_file, 'w') as f:
        json.dump({
            "video": video_path,
            "clips": clips,
            "history": history
        }, f, indent=2)

    print(f"   Metadata: {metadata_file}\n")


# Tool implementations

def tool_get_video_info(state):
    """Get video metadata."""
    metadata = state['video_tools'].get_video_metadata(state['video_path'])
    print(f"   Duration: {metadata['duration']:.1f}s")
    print(f"   Resolution: {metadata['width']}x{metadata['height']}")
    return json.dumps(metadata)


def tool_detect_scenes(state):
    """Detect scenes in video."""
    scenes = state['video_tools'].detect_scenes(state['video_path'], max_scenes=20)
    state['scenes'] = scenes
    print(f"   Found {len(scenes)} scenes")
    return json.dumps({
        "count": len(scenes),
        "scenes": [{"index": i, "start": s['start'], "duration": s['duration']}
                   for i, s in enumerate(scenes)]
    })


def tool_analyze_scene(state, scene_index: int):
    """Analyze a scene with Nemotron."""
    if state['scenes'] is None:
        return json.dumps({"error": "Must detect scenes first"})

    if scene_index >= len(state['scenes']):
        return json.dumps({"error": f"Invalid scene index {scene_index}"})

    scene = state['scenes'][scene_index]

    # Extract frame
    frame_path = Path(state['clips_dir']) / f"frame_{scene_index}.jpg"
    frame_path.parent.mkdir(parents=True, exist_ok=True)

    success = state['video_tools'].extract_frame(
        state['video_path'],
        scene['mid_point'],
        str(frame_path)
    )

    if not success:
        return json.dumps({"error": "Failed to extract frame"})

    # Analyze with Cosmos Nemotron 34B (Vision-Language Model)
    analysis = analyze_scene_with_nemotron(
        state['api_key'],
        str(frame_path),
        scene['start']
    )

    state['analyzed_scenes'].append({
        "index": scene_index,
        "scene": scene,
        "analysis": analysis
    })

    print(f"   Scene {scene_index}: Score {analysis['score']}/100")
    print(f"   {analysis['description']}")

    return json.dumps({
        "scene_index": scene_index,
        "score": analysis['score'],
        "description": analysis['description'],
        "reasoning": analysis['reasoning']
    })


def tool_extract_clip(state, scene_index: int, rank: int):
    """Extract a video clip."""
    if state['scenes'] is None:
        return json.dumps({"error": "Must detect scenes first"})

    if scene_index >= len(state['scenes']):
        return json.dumps({"error": f"Invalid scene index {scene_index}"})

    scene = state['scenes'][scene_index]

    # Find analysis for this scene
    analysis = None
    for a in state['analyzed_scenes']:
        if a['index'] == scene_index:
            analysis = a['analysis']
            break

    if not analysis:
        analysis = {"score": 0, "description": "Unknown"}

    clip_file = f"{state['video_name']}_clip_{rank:03d}.mp4"
    clip_path = Path(state['clips_dir']) / clip_file

    success = state['video_tools'].extract_clip(
        state['video_path'],
        scene['start'],
        scene['duration'],
        str(clip_path)
    )

    if success:
        clip_info = {
            "rank": rank,
            "file": clip_file,
            "path": str(clip_path),
            "timestamp": scene['start'],
            "duration": scene['duration'],
            "score": analysis['score'],
            "description": analysis['description']
        }
        state['extracted_clips'].append(clip_info)
        print(f"   ✓ Extracted clip #{rank}: {clip_file}")
        return json.dumps({"success": True, "clip": clip_info})
    else:
        return json.dumps({"error": "Failed to extract clip"})


if __name__ == "__main__":
    main()
