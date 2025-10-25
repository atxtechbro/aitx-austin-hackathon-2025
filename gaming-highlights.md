---
description: Extract gaming highlights using AI
---

# Gaming Highlight Extractor

AI-powered tool to automatically extract the best moments from gaming videos.

## Overview

**GAMING-FOCUSED ANALYSIS**:
- Detects high-intensity gameplay moments
- Recognizes action sequences and UI indicators
- Optimized for gaming content (kills, scores, achievements)
- Variable-duration clips based on natural scene boundaries

**SCENE DETECTION**:
- Automatically detects scene changes (rounds, deaths, map transitions)
- Configurable sensitivity for different game types
- Filters by duration (5-45 seconds for social media)

**AI RANKING**:
- Analyzes gameplay intensity and visual interest
- Considers UI elements (kill feed, scoreboard, achievements)
- Ranks scenes to find top N moments

## Invocation

- Primary command: `gaming-highlights <video_path> [--count N]`
- Preview mode: `gaming-highlights <video_path> --dry-run`
- Example: `gaming-highlights my_gameplay.mp4 --count 3`

## Step 0: Load Configuration

Load settings from config.yml:

!# Config parser
!CONFIG_FILE="./config.yml"
!
!# Function to extract nested YAML values
!get_config() {
!  local path="$1"
!  local default="$2"
!
!  if [ ! -f "$CONFIG_FILE" ]; then
!    echo "$default"
!    return
!  fi
!
!  if command -v python3 &>/dev/null; then
!    python3 -c "
!import sys
!try:
!    import yaml
!    with open('$CONFIG_FILE') as f:
!        config = yaml.safe_load(f) or {}
!
!    value = config
!    for key in '$path'.split('.'):
!        if isinstance(value, dict) and key in value:
!            value = value[key]
!        else:
!            print('$default')
!            sys.exit(0)
!    print(value)
!except Exception:
!    print('$default')
!" 2>/dev/null && return
!  fi
!
!  echo "$default"
!}
!
!# Load configuration
!SCENE_THRESHOLD=$(get_config "gaming_highlights.scene_detection.threshold" "0.3")
!MIN_DURATION=$(get_config "gaming_highlights.scene_detection.min_duration" "5.0")
!MAX_DURATION=$(get_config "gaming_highlights.scene_detection.max_duration" "45.0")
!OPTIMIZE_FOR=$(get_config "gaming_highlights.analysis.optimize_for" "action")
!CLIP_COUNT=$(get_config "gaming_highlights.output.default_count" "3")
!CLIPS_DIR=$(get_config "gaming_highlights.output.clips_dir" "./output/clips")
!METADATA_DIR=$(get_config "gaming_highlights.output.metadata_dir" "./output/metadata")
!
!echo "🎮 Gaming Highlight Extractor - AITX Hackathon 2025"
!echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!echo "Configuration:"
!echo "  Scene threshold: $SCENE_THRESHOLD"
!echo "  Clip duration: ${MIN_DURATION}s - ${MAX_DURATION}s"
!echo "  Optimize for: $OPTIMIZE_FOR"
!echo "  Extract top: $CLIP_COUNT clips"
!echo ""

## Step 1: Parse Arguments

!# Get video path from user input
!VIDEO_PATH="${1:?Error: Please provide a video path}"
!
!# Check if video exists
!if [ ! -f "$VIDEO_PATH" ]; then
!  echo "❌ Error: Video file not found: $VIDEO_PATH"
!  exit 1
!fi
!
!# Extract video name
!VIDEO_NAME=$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')
!VIDEO_CLIPS_DIR="${CLIPS_DIR}/${VIDEO_NAME}"
!VIDEO_METADATA_DIR="${METADATA_DIR}/${VIDEO_NAME}"
!
!# Display file size and warnings
!FILE_SIZE=$(du -h "$VIDEO_PATH" 2>/dev/null | cut -f1)
!SIZE_BYTES=$(du -b "$VIDEO_PATH" 2>/dev/null | cut -f1)
!
!echo "📹 Processing: $VIDEO_PATH ($FILE_SIZE)"
!echo "Output directory: $VIDEO_CLIPS_DIR"
!
!# Warn for large files
!if [ -n "$SIZE_BYTES" ]; then
!  if [ "$SIZE_BYTES" -gt 5368709120 ]; then  # > 5GB
!    echo "⚠️  Very large file detected (5GB+). Processing may take 10+ minutes."
!    echo "    Consider extracting a shorter segment first for testing."
!  elif [ "$SIZE_BYTES" -gt 1073741824 ]; then  # > 1GB
!    echo "⚠️  Large file detected (>1GB). Processing may take several minutes..."
!  fi
!fi
!
!echo ""

## Step 2: Setup Output Directories

!mkdir -p "$VIDEO_CLIPS_DIR" "$VIDEO_METADATA_DIR"

## Step 3: Detect Scenes

!echo "🔍 Detecting scenes..."
!DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_PATH")
!echo "Video duration: ${DURATION}s"
!
!# Detect scene changes using FFmpeg
!SCENE_TIMES=$(ffprobe -v error -show_entries packet=pts_time,flags -of csv "$VIDEO_PATH" -select_streams v:0 | \
!  awk -F',' '$2 ~ /K/ {print $1}' | head -100)
!
!# Convert to array
!mapfile -t SCENE_TIMESTAMPS < <(echo "$SCENE_TIMES")
!
!# Add start and end markers
!SCENE_TIMESTAMPS=("0.0" "${SCENE_TIMESTAMPS[@]}" "$DURATION")
!
!SCENE_COUNT=$((${#SCENE_TIMESTAMPS[@]} - 1))
!echo "Detected $SCENE_COUNT potential scenes"
!
!# Build scene metadata
!declare -a SCENE_STARTS
!declare -a SCENE_ENDS
!declare -a SCENE_DURATIONS
!declare -a VALID_SCENES
!
!for ((i=0; i<SCENE_COUNT; i++)); do
!  START=${SCENE_TIMESTAMPS[$i]}
!  END=${SCENE_TIMESTAMPS[$((i+1))]}
!
!  # Calculate duration
!  if command -v bc >/dev/null 2>&1; then
!    DUR=$(echo "$END - $START" | bc)
!  else
!    DUR=$(awk "BEGIN {printf \"%.2f\", $END - $START}")
!  fi
!
!  # Filter by duration
!  VALID=false
!  if command -v bc >/dev/null 2>&1; then
!    if (( $(echo "$DUR >= $MIN_DURATION" | bc -l) )) && (( $(echo "$DUR <= $MAX_DURATION" | bc -l) )); then
!      VALID=true
!    fi
!  else
!    if [ "$(awk "BEGIN {print ($DUR >= $MIN_DURATION && $DUR <= $MAX_DURATION)}")" = "1" ]; then
!      VALID=true
!    fi
!  fi
!
!  if [ "$VALID" = "true" ]; then
!    SCENE_STARTS+=("$START")
!    SCENE_ENDS+=("$END")
!    SCENE_DURATIONS+=("$DUR")
!    VALID_SCENES+=("$i")
!  fi
!done
!
!VALID_SCENE_COUNT=${#VALID_SCENES[@]}
!echo "✓ Found $VALID_SCENE_COUNT valid scenes (${MIN_DURATION}s - ${MAX_DURATION}s)"
!
!if [ "$VALID_SCENE_COUNT" -eq 0 ]; then
!  echo "❌ No valid scenes found. Try adjusting scene_detection.threshold in config.yml"
!  exit 1
!fi

## Step 4: Extract Representative Frames

!echo ""
!echo "📸 Extracting representative frames from each scene..."
!for ((i=0; i<VALID_SCENE_COUNT; i++)); do
!  SCENE_NUM=${VALID_SCENES[$i]}
!  START=${SCENE_STARTS[$i]}
!  END=${SCENE_ENDS[$i]}
!
!  # Calculate middle timestamp
!  if command -v bc >/dev/null 2>&1; then
!    MID_TIME=$(echo "scale=2; ($START + $END) / 2" | bc)
!  else
!    MID_TIME=$(awk "BEGIN {printf \"%.2f\", ($START + $END) / 2}")
!  fi
!
!  # Extract frame
!  FRAME_PATH="$VIDEO_CLIPS_DIR/scene_$(printf '%03d' $SCENE_NUM)_frame.jpg"
!  ffmpeg -ss "$MID_TIME" -i "$VIDEO_PATH" -vframes 1 -q:v 2 "$FRAME_PATH" -loglevel error
!
!  echo "  Scene $SCENE_NUM: ${START}s - ${END}s (${SCENE_DURATIONS[$i]}s) → frame extracted"
!done
!
!echo "✓ Extracted $VALID_SCENE_COUNT frames for analysis"

## Step 5: AI Scene Ranking

Now I'll analyze all scenes and rank them based on **${OPTIMIZE_FOR}** criteria for gaming content.

Let me examine the scene frames to identify the best gaming moments:

!echo ""
!echo "🤖 Starting AI analysis..."
!echo "Analyzing ${VALID_SCENE_COUNT} scenes for gaming highlights..."
!echo "Criteria: ${OPTIMIZE_FOR} gameplay"

[Claude will now analyze each scene frame, considering:
- **Gameplay intensity**: Fast-paced action, combat, quick movements
- **Visual interest**: Explosions, effects, dynamic camera
- **UI indicators**: Kill feed, scoreboard, achievements, notifications
- **Scene quality**: Clarity, composition, no loading screens
]

After analyzing all scenes, I'll rank them and select the top ${CLIP_COUNT} moments.

**Analysis complete!** Here are my findings:

[Claude outputs scene rankings with justification for each choice]

## Step 6: Extract Top Clips

Based on the AI analysis, extract the top clips:

!echo ""
!echo "✂️ Extracting top $CLIP_COUNT clips..."
!
!# RANKED_SCENES array should be set by AI analysis above
!# Example: RANKED_SCENES=(5 12 3) for top 3 scenes
!
!for ((clip_idx=0; clip_idx<CLIP_COUNT && clip_idx<VALID_SCENE_COUNT; clip_idx++)); do
!  SCENE_IDX=${RANKED_SCENES[$clip_idx]}
!  START=${SCENE_STARTS[$SCENE_IDX]}
!  DUR=${SCENE_DURATIONS[$SCENE_IDX]}
!
!  CLIP_NUM=$(printf '%03d' $((clip_idx + 1)))
!  CLIP_PATH="$VIDEO_CLIPS_DIR/${VIDEO_NAME}_clip_${CLIP_NUM}.mp4"
!
!  # Extract clip (using copy codec for speed)
!  ffmpeg -ss "$START" -i "$VIDEO_PATH" -t "$DUR" -c copy "$CLIP_PATH" -loglevel error
!
!  echo "  ✓ Clip $CLIP_NUM: ${START}s (${DUR}s) → ${VIDEO_NAME}_clip_${CLIP_NUM}.mp4"
!done

## Step 7: Generate Metadata

!echo ""
!echo "📊 Generating metadata..."
!METADATA_FILE="$VIDEO_METADATA_DIR/metadata.json"
!
!cat > "$METADATA_FILE" <<EOF
!{
!  "video": {
!    "path": "$VIDEO_PATH",
!    "name": "$VIDEO_NAME",
!    "duration": $DURATION
!  },
!  "config": {
!    "optimize_for": "$OPTIMIZE_FOR",
!    "scene_threshold": $SCENE_THRESHOLD,
!    "min_duration": $MIN_DURATION,
!    "max_duration": $MAX_DURATION,
!    "clip_count": $CLIP_COUNT
!  },
!  "extraction": {
!    "total_scenes": $SCENE_COUNT,
!    "valid_scenes": $VALID_SCENE_COUNT,
!    "clips_extracted": $CLIP_COUNT
!  },
!  "clips": [
!EOF
!
!for ((clip_idx=0; clip_idx<CLIP_COUNT && clip_idx<VALID_SCENE_COUNT; clip_idx++)); do
!  SCENE_IDX=${RANKED_SCENES[$clip_idx]}
!  START=${SCENE_STARTS[$SCENE_IDX]}
!  DUR=${SCENE_DURATIONS[$SCENE_IDX]}
!  CLIP_NUM=$(printf '%03d' $((clip_idx + 1)))
!
!  [ $clip_idx -gt 0 ] && echo "," >> "$METADATA_FILE"
!
!  cat >> "$METADATA_FILE" <<CLIP_EOF
!    {
!      "rank": $((clip_idx + 1)),
!      "scene_index": $SCENE_IDX,
!      "start_time": $START,
!      "duration": $DUR,
!      "file": "${VIDEO_NAME}_clip_${CLIP_NUM}.mp4"
!    }
!CLIP_EOF
!done
!
!cat >> "$METADATA_FILE" <<EOF
!
!  ]
!}
!EOF
!
!echo "✓ Metadata saved: $METADATA_FILE"

## Summary

!echo ""
!echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!echo "🎉 Complete! Extracted $CLIP_COUNT gaming highlights"
!echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
!echo ""
!echo "📁 Clips saved to:"
!echo "   $VIDEO_CLIPS_DIR/"
!for ((i=1; i<=CLIP_COUNT; i++)); do
!  echo "   └─ ${VIDEO_NAME}_clip_$(printf '%03d' $i).mp4"
!done
!echo ""
!echo "📊 Metadata saved to:"
!echo "   $METADATA_FILE"
!echo ""
!echo "🎮 Ready to share your best plays!"

## Next Steps

Your gaming highlights are ready! You can now:
- Share clips directly to TikTok, YouTube Shorts, Twitter
- Edit clips further with video editing software
- Create a montage from multiple clips
- Adjust config.yml and rerun for different results
