# Gaming Highlights Autonomous Agent

**Autonomous AI agent powered by NVIDIA Cosmos Nemotron 34B (Vision-Language Model)**

Built for **AITX Austin AI Community Hackathon 2025** 🎮

## What Makes This Autonomous?

Nemotron makes ALL decisions:

- ✅ **Which tools to use** (detect scenes, analyze, extract clips)
- ✅ **When to analyze** each scene
- ✅ **How to rank** highlights
- ✅ **When task is complete**

### Architecture

```
Cosmos Nemotron 34B VLM Agent
├─ Sees available tools
├─ Decides which tool to use next
├─ Executes tool
└─ Repeats until goal achieved

Tools:
• get_video_info
• detect_scenes
• analyze_scene (VLM analyzes screenshots, scores 0-100)
• extract_clip
```

**Key Advantage:** Cosmos Nemotron 34B is a Vision-Language Model that can actually SEE and analyze the gaming screenshots, not just read text descriptions!

## Quick Start

```bash
cd agent/

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add NVIDIA_API_KEY from https://build.nvidia.com/

# Run
python gaming_agent.py video.mp4 --count 3
```

## How It Works

### Step 1: Scene Detection (FFmpeg Tools)
The agent uses FFmpeg to detect scene changes (keyframes) in the video, filtering for optimal clip lengths (5-45 seconds).

### Step 2: Frame Analysis (Nemotron Nano)
For each candidate scene:
- Extracts a representative frame
- Sends to **NVIDIA Nemotron Nano 9B v2** with reasoning enabled (`/think` mode)
- Nemotron scores the moment 0-100 based on:
  - Action intensity
  - Skill display
  - Visual interest
  - Game events (kills, scores, achievements)
  - Rarity and excitement

### Step 3: Autonomous Ranking (Claude Agent)
Claude orchestrates the workflow:
- Decides which scenes to analyze based on initial results
- Integrates Nemotron scores with temporal distribution
- Selects the most highlight-worthy moments
- Manages resource allocation (which scenes are worth the compute)

### Step 4: Clip Extraction
Automatically extracts top-ranked clips with metadata.

## Example Output

```
🎮 Gaming Highlights Agent Initialized
   Working directory: /path/to/project
   Max scenes to analyze: 20
   Top clips to extract: 3

============================================================
🎬 Processing: apex-legends.mp4
============================================================

📹 Video Info:
   Duration: 847.5s
   Resolution: 1920x1080
   Codec: h264

🔍 Detecting scenes...
   Found 18 candidate scenes

📸 Extracting frames and analyzing with Nemotron...
🤖 Loading Nemotron model: nvidia/NVIDIA-Nemotron-Nano-9B-v2
   Using device: cuda
✅ Nemotron model loaded successfully

   Scene  5 @   42.3s: Score  94/100 - Triple elimination with headshots
   Scene  8 @  156.7s: Score  88/100 - Clutch 1v3 defensive play
   Scene 12 @  334.2s: Score  91/100 - Squad wipe with ultimate ability
   ...

✅ Analyzed 18 scenes

🏆 Selecting top 3 highlights...

✂️  Extracting clips...

   ✓ Clip 1: 42.3s (8.2s) - Score 94/100
      Triple elimination with headshots
      → apex-legends_clip_001.mp4

   ✓ Clip 2: 334.2s (12.5s) - Score 91/100
      Squad wipe with ultimate ability
      → apex-legends_clip_002.mp4

   ✓ Clip 3: 156.7s (7.8s) - Score 88/100
      Clutch 1v3 defensive play
      → apex-legends_clip_003.mp4

============================================================
🎉 Complete! Extracted 3 gaming highlights
============================================================

📁 Clips saved to: output/clips/apex-legends
📊 Metadata saved to: output/metadata/apex-legends/metadata.json
```

## Output Structure

```
output/
├── clips/
│   └── apex-legends/
│       ├── apex-legends_clip_001.mp4
│       ├── apex-legends_clip_002.mp4
│       ├── apex-legends_clip_003.mp4
│       └── frames/
│           ├── scene_005.jpg
│           ├── scene_008.jpg
│           └── ...
└── metadata/
    └── apex-legends/
        └── metadata.json
```

### Metadata Format

```json
{
  "video": {
    "path": "apex-legends.mp4",
    "name": "apex-legends",
    "duration": 847.5,
    "resolution": "1920x1080"
  },
  "processing": {
    "total_scenes_detected": 47,
    "scenes_analyzed": 18,
    "clips_extracted": 3
  },
  "clips": [
    {
      "rank": 1,
      "timestamp": 42.3,
      "duration": 8.2,
      "score": 94,
      "description": "Triple elimination with headshots",
      "reasoning": "This scene shows exceptional aim...",
      "file": "apex-legends_clip_001.mp4"
    }
  ]
}
```

## Key Technologies

| Technology | Purpose |
|------------|---------|
| **Claude Agent SDK** | Autonomous orchestration, decision-making, tool coordination |
| **NVIDIA Nemotron Nano 9B v2** | Gaming scene analysis, excitement scoring with reasoning |
| **FFmpeg** | Video processing, scene detection, clip extraction |
| **MCP (Model Context Protocol)** | Custom tool integration for Claude agent |
| **PyTorch + Transformers** | Nemotron model inference |

## Hackathon Judging Criteria

### 1. Impact & Clarity ⭐
- **Clear value proposition**: Automatically extract the best moments from hours of gameplay
- **Real-world impact**: Saves content creators hours of manual editing
- **Easy to understand**: Simple CLI interface with clear output

### 2. Technical Execution ⭐
- **Proper SDK usage**: Uses Claude Agent SDK for true autonomous behavior
- **Multi-agent architecture**: Claude and Nemotron collaborate with distinct roles
- **Production-ready patterns**: Error handling, logging, configurable parameters
- **MCP integration**: Custom tools properly integrated via Model Context Protocol

### 3. Innovation ⭐
- **Novel approach**: Two-AI-model collaboration (orchestrator + specialist)
- **Domain-specific reasoning**: Nemotron's reasoning mode for gameplay analysis
- **Autonomous decision-making**: Agent decides what to analyze, not just following a script
- **Evolution from slash command**: Shows clear upgrade path from simple to autonomous

### 4. UX ⭐
- **Simple CLI**: One command to extract highlights
- **Clear progress**: Shows agent "thinking" and decision-making process
- **Useful output**: Metadata includes Nemotron's reasoning for each clip
- **Helpful errors**: Clear messages when things go wrong

### 5. Track Fit ⭐
- **Agent Track**: Demonstrates autonomous agent using Claude Agent SDK with custom tools
- **Nemotron Track**: Non-trivial use of Nemotron for domain-specific analysis and reasoning

## Comparison: Slash Command vs. Autonomous Agent

| Aspect | Slash Command (old) | Autonomous Agent (new) |
|--------|---------------------|------------------------|
| **Execution** | Claude Code manually runs script | Agent runs independently |
| **Decision Making** | Human directs each step | Agent decides autonomously |
| **Tool Usage** | Bash commands in markdown | Custom MCP tools via SDK |
| **AI Models** | Single (Claude Code) | Multi-agent (Claude + Nemotron) |
| **Deployment** | Requires Claude Code UI | Standalone Python application |
| **Integration** | Manual trigger only | Can be automated, scheduled, API-wrapped |
| **Scalability** | One video at a time, manual | Batch processing, programmatic access |

## Development

### Project Structure

```
agent/
├── gaming_agent.py          # Main autonomous agent
├── nemotron_analyzer.py     # Nemotron wrapper for scene analysis
├── video_tools.py           # FFmpeg tools for video processing
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

### Testing

```bash
# Test Nemotron analyzer standalone
python nemotron_analyzer.py

# Test video tools
python video_tools.py

# Full agent test with sample video
python gaming_agent.py ../videos/apex-legends.mp4 --count 3
```

### Extending

Add new custom tools by decorating functions with `@tool`:

```python
@tool("analyze_audio", "Detect excitement in audio", {"video_path": str})
async def analyze_audio(args):
    # Your logic here
    return {"content": [{"type": "text", "text": result}]}
```

## Troubleshooting

### Nemotron Model Download Fails
- The model is ~18GB - ensure sufficient disk space and stable internet
- First run will download from HuggingFace

### Out of Memory (GPU)
- Nemotron requires ~9GB VRAM
- Fallback to CPU is automatic but slower
- Reduce `MAX_SCENES_TO_ANALYZE` in `.env`

### FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### No Scenes Detected
- Lower scene detection threshold in `config.yml`
- Check video is a supported format (mp4, mkv, avi, etc.)

## Future Enhancements

- [ ] Add vision model for true frame understanding (current uses heuristics)
- [ ] Implement audio analysis for crowd reactions / commentary
- [ ] Add game-specific profiles (FPS vs. MOBA vs. Racing)
- [ ] Web UI for easier access
- [ ] Batch processing for multiple videos
- [ ] Direct upload to TikTok/YouTube via APIs

## License

MIT License - See LICENSE file for details

## Credits

- **Team**: [@atxtechbro](https://github.com/atxtechbro), [@ionpetro](https://github.com/ionpetro)
- **Built for**: AITX Austin AI Community Hackathon 2025
- **Powered by**: Anthropic Claude, NVIDIA Nemotron, FFmpeg

---

**🎮 Happy Gaming! 🎯**
