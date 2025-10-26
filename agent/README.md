# Gaming Highlights Agent

Autonomous agent powered by **Cosmos Nemotron 34B VLM** that extracts gaming highlights.

## Setup

```bash
cd agent/

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install deps
uv pip install -r requirements.txt

# Add API key
cp .env.example .env
# Edit .env and add NVIDIA_API_KEY from https://build.nvidia.com/
```

## Run

```bash
uv run gaming_agent.py video.mp4 --count 3
```

Outputs clips to `output/clips/`

## How It Works

Nemotron decides which tools to use:
- `detect_scenes` - FFmpeg scene detection
- `analyze_scene` - VLM scores screenshot 0-100
- `extract_clip` - Extract top moments

Built for AITX Austin Hackathon 2025
