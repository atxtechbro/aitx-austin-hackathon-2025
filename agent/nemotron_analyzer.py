"""
Nemotron Nano Gaming Scene Analyzer

Uses NVIDIA Nemotron-Nano-9B-v2 to analyze gaming screenshots
and score them based on highlight-worthiness.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from PIL import Image
import base64
import io
import os
from typing import Dict, Optional


class NemotronAnalyzer:
    """
    Wrapper for NVIDIA Nemotron-Nano-9B-v2 model.
    Specializes in analyzing gaming screenshots for highlight detection.
    """

    def __init__(self, model_name: str = "nvidia/NVIDIA-Nemotron-Nano-9B-v2"):
        """
        Initialize the Nemotron analyzer.

        Args:
            model_name: HuggingFace model identifier
        """
        print(f"🤖 Loading Nemotron model: {model_name}")
        print("   This may take a minute on first run...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Using device: {self.device}")

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        )

        if self.device == "cpu":
            self.model = self.model.to(self.device)

        self.model.eval()
        print("✅ Nemotron model loaded successfully")

    def analyze_gaming_moment(
        self,
        image_path: str,
        timestamp: float,
        context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze a gaming screenshot to determine if it's highlight-worthy.

        Args:
            image_path: Path to the screenshot
            timestamp: Timestamp in video where this frame occurs
            context: Optional context about the game or video

        Returns:
            Dictionary with:
            - score: 0-100 excitement score
            - reasoning: Explanation of the score
            - is_highlight: Boolean recommendation
            - description: Brief description of the moment
        """

        # Build the analysis prompt
        prompt = self._build_gaming_prompt(timestamp, context)

        # Note: Nemotron-Nano-9B-v2 is text-only, not multimodal
        # For a real implementation, you would:
        # 1. Use a vision model to describe the image, OR
        # 2. Use OCR to extract UI elements (kill feed, score), OR
        # 3. Use CLIP embeddings for scene understanding
        #
        # For this hackathon demo, we'll simulate vision analysis
        # In production, integrate with a vision model or use Nemotron's
        # reasoning on extracted text/metadata

        image_description = self._describe_image_simple(image_path)
        full_prompt = f"{prompt}\n\nScene Description:\n{image_description}"

        # Run inference with reasoning enabled
        response = self._generate_with_reasoning(full_prompt)

        # Parse the response to extract score and reasoning
        result = self._parse_analysis_response(response, timestamp)

        return result

    def _build_gaming_prompt(self, timestamp: float, context: Optional[str]) -> str:
        """Build the analysis prompt for gaming highlights."""

        base_prompt = """/think

You are an expert gaming content analyst. Your job is to evaluate gaming moments and determine if they are highlight-worthy for social media (TikTok, YouTube Shorts, Twitter).

Analyze the gaming scene and provide:
1. An excitement score from 0-100 (where 100 is the most highlight-worthy)
2. Clear reasoning for your score
3. A brief, catchy description suitable for a clip title

Consider these factors:
- **Action Intensity**: Combat, fast movements, quick reactions
- **Skill Display**: Difficult plays, clutch moments, impressive accuracy
- **Visual Interest**: Explosions, special effects, dramatic moments
- **Game Events**: Kills, deaths, round wins, achievements, score changes
- **Rarity**: Unusual plays, lucky shots, funny moments

Be critical - only truly exciting moments should score above 80.
"""

        if context:
            base_prompt += f"\n\nGame Context: {context}"

        base_prompt += f"\n\nTimestamp: {timestamp:.1f}s"

        return base_prompt

    def _describe_image_simple(self, image_path: str) -> str:
        """
        Simple image analysis using basic CV techniques.
        In production, replace with actual vision model.
        """
        try:
            img = Image.open(image_path)
            width, height = img.size

            # Calculate basic statistics
            img_array = torch.tensor(list(img.getdata()))
            brightness = img_array.float().mean().item()

            # Simple heuristics (would be replaced with vision model)
            description = f"Frame resolution: {width}x{height}\n"
            description += f"Average brightness: {brightness:.1f}/255\n"
            description += "Note: Using basic image analysis. "
            description += "In production, integrate vision model for detailed scene understanding."

            return description

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def _generate_with_reasoning(self, prompt: str) -> str:
        """
        Generate response using Nemotron with reasoning enabled.
        The /think prefix enables the model's reasoning mode.
        """

        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate with reasoning parameters
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.6,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the model's response (after the prompt)
        response = response[len(prompt):].strip()

        return response

    def _parse_analysis_response(self, response: str, timestamp: float) -> Dict:
        """
        Parse the Nemotron response to extract structured data.
        """

        # Simple parsing - look for score, reasoning, description
        # In production, you'd use more robust parsing or structured output

        score = 50  # Default
        reasoning = response
        description = "Gaming moment"

        # Try to extract score from response
        lines = response.lower().split('\n')
        for line in lines:
            if 'score' in line or 'excitement' in line:
                # Look for numbers
                import re
                numbers = re.findall(r'\b(\d{1,3})\b', line)
                if numbers:
                    potential_score = int(numbers[0])
                    if 0 <= potential_score <= 100:
                        score = potential_score
                        break

        # Extract description (usually first sentence or line)
        if response:
            first_line = response.split('\n')[0].strip()
            if len(first_line) > 10 and len(first_line) < 100:
                description = first_line

        return {
            "score": score,
            "reasoning": reasoning[:500],  # Limit length
            "is_highlight": score >= 70,
            "description": description[:100],
            "timestamp": timestamp,
            "raw_response": response
        }

    def cleanup(self):
        """Free up GPU memory."""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Simple test function
if __name__ == "__main__":
    print("Testing Nemotron Analyzer...")

    analyzer = NemotronAnalyzer()

    # Create a dummy test
    test_prompt = "/think\n\nEvaluate this gaming moment: Player gets a triple kill with headshots in a clutch 1v3 situation. Rate from 0-100."

    result = analyzer._generate_with_reasoning(test_prompt)
    print("\nTest response:")
    print(result)

    analyzer.cleanup()
