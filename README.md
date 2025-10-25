# Gaming Highlight Extractor

AI-powered tool to automatically extract the best moments from gaming videos using scene detection and intelligent analysis.

Built for **AITX Austin AI Community Hackathon 2025** 🎮

## Quick Start

Get your gaming highlights in 4 easy steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/atxtechbro/aitx-austin-hackathon-2025.git
   cd aitx-austin-hackathon-2025
   ```

2. **Copy the config** (optional - defaults work great):
   ```bash
   cp config.example.yml config.yml
   ```

3. **Drop your video in the project** (won't be committed - see `.gitignore`):
   ```bash
   # Just copy your video file here
   cp ~/Desktop/my_gameplay.mp4 .
   ```

4. **Open in Claude Code and run**:
   ```
   gaming-highlights my_gameplay.mp4
   ```

**That's it!** Your top 3 highlights will be extracted to `./output/clips/` 🎉

> **Note**: Video files are automatically gitignored and stay local. They're never committed to the repository. To share test videos with contributors, post a cloud link (Google Drive, YouTube) in the issue comments.

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

**Option 1: Slash Command** (recommended - discoverable in autocomplete):
```
/gaming-highlights my_gameplay.mp4
```

**Option 2: Natural Language**:
```
gaming-highlights my_gameplay.mp4
```

Or simply say: `"Run gaming-highlights.md on my_gameplay.mp4"`

Both methods work identically - use whichever feels more natural!

### Command Examples

**Basic usage** - video in project root:
```
gaming-highlights my_apex_gameplay.mp4
```

**Extract more clips** - get top 5 instead of default 3:
```
gaming-highlights my_gameplay.mp4 --count 5
```

**Video in subdirectory** (also gitignored):
```
gaming-highlights videos/valorant_match.mp4
```

**Full absolute path** - video outside project:
```
gaming-highlights /Users/gamer/Desktop/cod_highlights.mp4
```

**Preview mode** - see what would happen without processing:
```
gaming-highlights my_gameplay.mp4 --dry-run
```

> **All video formats supported**: `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.flv`, `.wmv` - they're all gitignored automatically!

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
