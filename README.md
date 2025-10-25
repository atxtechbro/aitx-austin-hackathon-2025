# Gaming Highlight Extractor

AI-powered tool to automatically extract the best moments from gaming videos using scene detection and intelligent analysis.

Built for **AITX Austin AI Community Hackathon 2025** 🎮

## Features

- 🎮 **Gaming-Focused**: Optimized for detecting action-packed gameplay moments
- 🤖 **AI-Powered**: Uses Claude to intelligently rank and select the best clips
- ⚡ **Fast Processing**: Leverages FFmpeg for efficient video processing
- 📊 **Detailed Metadata**: Outputs timestamps, rankings, and scene information
- 🎬 **Social Media Ready**: Generates clips perfect for TikTok/Shorts (5-45 seconds)
- 🎯 **Top Plays**: Automatically extracts your best 3 moments

## How It Works

1. **Scene Detection**: Uses FFmpeg's scenecut filter to detect scene changes (round transitions, kills, respawns)
2. **Frame Analysis**: Extracts representative frames from each scene
3. **AI Ranking**: Claude analyzes frames for action intensity, visual interest, and gameplay quality
4. **Clip Extraction**: Outputs top N clips as separate video files with metadata

## Prerequisites

- **FFmpeg**: For video processing
  ```bash
  # macOS
  brew install ffmpeg

  # Ubuntu/Debian
  sudo apt-get install ffmpeg

  # Windows
  # Download from https://ffmpeg.org/download.html
  ```

- **Claude Code**: This tool is designed to run in Claude Code
  - Download: https://docs.anthropic.com/en/docs/claude-code

- **Configuration**: Copy `config.example.yml` to `config.yml` and customize

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/atxtechbro/aitx-austin-hackathon-2025.git
   cd aitx-austin-hackathon-2025
   ```

2. Copy and customize the config:
   ```bash
   cp config.example.yml config.yml
   ```

3. Place your gaming video in the repo directory

## Usage

### In Claude Code

1. Open this repository in Claude Code
2. Say: `"Run gaming-highlights.md on my_gameplay.mp4"`
3. Claude will execute the procedure and extract your best clips

### Command Examples

- Extract top 3 clips (default):
  ```
  gaming-highlights my_gameplay.mp4
  ```

- Extract top 5 clips:
  ```
  gaming-highlights my_gameplay.mp4 --count 5
  ```

- Preview what would happen (dry-run):
  ```
  gaming-highlights my_gameplay.mp4 --dry-run
  ```

## Output

Results are saved to `./output/`:
- `clips/` - Video files (clip_001.mp4, clip_002.mp4, etc.)
- `metadata/` - JSON files with timestamps, rankings, and scene info

Example output structure:
```
output/
├── clips/
│   ├── my_gameplay_clip_001.mp4  # Top play
│   ├── my_gameplay_clip_002.mp4  # 2nd best
│   └── my_gameplay_clip_003.mp4  # 3rd best
└── metadata/
    └── my_gameplay_metadata.json
```

## Configuration

Edit `config.yml` to customize:

```yaml
gaming_highlights:
  scene_detection:
    threshold: 0.3        # Scene sensitivity (0.1-0.5)
    min_duration: 5.0     # Min clip length
    max_duration: 45.0    # Max clip length

  analysis:
    optimize_for: "action"  # Or "highlights", "story"
    factors:
      - "gameplay_intensity"
      - "visual_interest"
      - "ui_indicators"   # Scoreboard, kills, etc.

  output:
    clips_dir: "./output/clips"
    metadata_dir: "./output/metadata"
    default_count: 3      # Top N clips
```

## Tech Stack

- **FFmpeg**: Video processing and scene detection
- **Bash**: Script orchestration
- **PyYAML**: Configuration parsing
- **Anthropic Claude**: AI-powered scene analysis and ranking
- **Claude Code**: Execution environment

## Examples

_Add demo videos/GIFs here during hackathon_

## Hackathon Team

- [@atxtechbro](https://github.com/atxtechbro)
- [@ionpetro](https://github.com/ionpetro)

## License

MIT License - See LICENSE file for details

## Contributing

This is a hackathon project, but we welcome feedback and contributions!

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

## Troubleshooting

**Issue: FFmpeg not found**
- Solution: Install FFmpeg using instructions in Prerequisites

**Issue: No scenes detected**
- Solution: Lower the `scene_detection.threshold` in config.yml

**Issue: Clips too short/long**
- Solution: Adjust `min_duration` and `max_duration` in config.yml

## Resources

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [AITX Austin AI Community](https://www.meetup.com/austin-langchain-ai-group/)

---

Built with 💜 for AITX Austin Hackathon 2025
