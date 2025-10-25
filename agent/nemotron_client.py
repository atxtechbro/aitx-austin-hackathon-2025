"""
Dual Nemotron agent:
- 340B Instruct for orchestration (most powerful!)
- VL 8B for vision analysis (scoring screenshots)
"""

import os
import json
import requests
from typing import Dict, List, Callable, Any


class NemotronAgent:
    """Autonomous agent powered by dual Nemotron models."""

    def __init__(self, api_key: str):
        """Initialize agent with NVIDIA API key."""
        self.api_key = api_key
        self.url = "https://integrate.api.nvidia.com/v1/chat/completions"
        # Use 340B for orchestration (most powerful Nemotron model!)
        self.orchestrator_model = "nvidia/nemotron-4-340b-instruct"
        # Use VL 8B for vision analysis
        self.vision_model = "nvidia/llama-3.1-nemotron-nano-vl-8b-v1"

    def run(
        self,
        goal: str,
        tools: Dict[str, Dict[str, Any]],
        max_iterations: int = 20
    ) -> List[Dict]:
        """Run agent to achieve goal using available tools."""
        state = {
            "goal": goal,
            "history": [],
            "iteration": 0
        }

        print(f"🤖 Nemotron Agent Started")
        print(f"   Goal: {goal}")
        print(f"   Available tools: {', '.join(tools.keys())}\n")

        for i in range(max_iterations):
            state["iteration"] = i + 1

            # Nemotron decides next action
            print(f"[Iteration {i+1}] Nemotron deciding next action...")
            action = self._decide_action(state, tools)

            print(f"   → Tool: {action['tool']}")
            print(f"   → Reasoning: {action['reasoning'][:100]}...")

            if action['done']:
                print(f"\n✅ Agent completed goal!\n")
                return state['history']

            # Execute tool
            try:
                tool_fn = tools[action['tool']]['function']
                result = tool_fn(**action['params'])

                state['history'].append({
                    "iteration": i + 1,
                    "action": action,
                    "result": result,
                    "success": True
                })

                print(f"   ✓ Tool executed successfully\n")

            except Exception as e:
                print(f"   ✗ Tool failed: {str(e)}\n")
                state['history'].append({
                    "iteration": i + 1,
                    "action": action,
                    "error": str(e),
                    "success": False
                })

        print("⚠️  Max iterations reached\n")
        return state['history']

    def _decide_action(self, state: Dict, tools: Dict[str, Dict]) -> Dict:
        """Ask Nemotron to decide next action."""
        # Format tools for Nemotron
        tools_desc = self._format_tools(tools)

        # Format history
        history_desc = self._format_history(state['history'])

        # Build prompt
        prompt = f"""You are an autonomous agent extracting gaming highlights from videos.

Goal: {state['goal']}

WORKFLOW RULES:
1. FIRST: Call detect_scenes once to find all scenes
2. THEN: Call analyze_scene for EACH scene (scene_index: 0, 1, 2, etc.)
3. AFTER analyzing ALL scenes: Extract the top N clips with extract_clip
4. Set done=true ONLY after extracting all required clips

Available Tools:
{tools_desc}

Execution History:
{history_desc}

IMPORTANT:
- Analyze DIFFERENT scenes each time (increment scene_index: 0, 1, 2, 3...)
- Don't analyze the same scene twice
- Don't extract clips until you've analyzed enough scenes
- Track which scenes you've already analyzed

Respond with ONLY valid JSON (no markdown, no explanations):
{{
    "tool": "tool_name",
    "params": {{"param": "value"}},
    "reasoning": "why you chose this action",
    "done": false
}}

Set "done": true ONLY when you've extracted all required clips.
"""

        # Call Nemotron with reasoning mode
        response = self._call_nemotron(prompt, use_reasoning=True)

        # Parse JSON response
        try:
            action = self._extract_json(response)
            return action
        except Exception as e:
            print(f"Failed to parse Nemotron response: {e}")
            print(f"Response was: {response}")
            # Fallback action
            return {
                "tool": "done",
                "params": {},
                "reasoning": "Failed to parse response",
                "done": True
            }

    def _call_nemotron(self, prompt: str, use_reasoning: bool = True) -> str:
        """Call NVIDIA Nemotron API."""

        messages = [
            {"role": "user", "content": prompt}
        ]

        if use_reasoning:
            messages.insert(0, {"role": "system", "content": "/think"})

        payload = {
            "model": self.orchestrator_model,  # Use 70B for orchestration
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content']

        except Exception as e:
            raise Exception(f"Nemotron API call failed: {str(e)}")

    def _format_tools(self, tools: Dict) -> str:
        """Format tools for prompt."""
        lines = []
        for name, tool in tools.items():
            params = json.dumps(tool['params'])
            lines.append(f"- {name}: {tool['description']}")
            lines.append(f"  Parameters: {params}")
        return "\n".join(lines)

    def _format_history(self, history: List[Dict]) -> str:
        """Format execution history for prompt."""
        if not history:
            return "(No actions taken yet)"

        # Track what's been done
        scenes_detected = False
        total_scenes = 0
        analyzed_scenes = []
        extracted_clips = []

        for entry in history:
            tool = entry['action']['tool']
            if tool == 'detect_scenes' and entry.get('success'):
                scenes_detected = True
                # Try to parse result for scene count
                try:
                    import json
                    result = json.loads(entry['result'])
                    total_scenes = result.get('count', 0)
                except:
                    pass
            elif tool == 'analyze_scene' and entry.get('success'):
                params = entry['action'].get('params', {})
                scene_idx = params.get('scene_index', -1)
                if scene_idx not in analyzed_scenes:
                    analyzed_scenes.append(scene_idx)
            elif tool == 'extract_clip' and entry.get('success'):
                extracted_clips.append(entry['action'])

        summary = []
        if scenes_detected:
            summary.append(f"✓ Scenes detected: {total_scenes}")
        summary.append(f"✓ Scenes analyzed: {len(analyzed_scenes)} {analyzed_scenes}")
        summary.append(f"✓ Clips extracted: {len(extracted_clips)}")

        # Recent actions
        summary.append("\nRecent actions:")
        for entry in history[-3:]:
            iter_num = entry['iteration']
            tool = entry['action']['tool']
            params = entry['action'].get('params', {})
            success = "✓" if entry.get('success') else "✗"
            summary.append(f"  {iter_num}. {success} {tool} {params}")

        return "\n".join(summary)

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from Nemotron's response."""
        # Try to find JSON in the response
        start = text.find('{')
        end = text.rfind('}') + 1

        if start >= 0 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)

        # If no JSON found, try parsing the whole thing
        return json.loads(text)


def analyze_scene_with_nemotron(api_key: str, frame_path: str, timestamp: float) -> Dict:
    """Analyze gaming screenshot with Nemotron VL 8B (vision specialist)."""
    import base64

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    # Read and encode the image
    with open(frame_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    prompt = f"""Analyze this gaming screenshot at {timestamp:.1f}s.

Rate the excitement level from 0-100 based on:
- 90-100: Epic plays (triple kills, clutch moments, rare achievements)
- 70-89: Good plays (double kills, skillful shots, winning plays)
- 50-69: Decent moments (average gameplay, some action)
- 0-49: Boring (low action, menus, loading screens)

Look for: kill feeds, score changes, special effects, intense action, multiple enemies, health bars.

Respond with ONLY valid JSON:
{{
    "score": 85,
    "reasoning": "why this score based on what you see",
    "description": "short catchy title for social media"
}}
"""

    payload = {
        "model": "nvidia/llama-3.1-nemotron-nano-vl-8b-v1",  # Vision specialist
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 512
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    result = response.json()
    content = result['choices'][0]['message']['content']

    # Extract JSON
    start = content.find('{')
    end = content.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(content[start:end])

    return json.loads(content)
