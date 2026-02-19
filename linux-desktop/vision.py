#!/usr/bin/env python3
"""
vision.py — Use Claude's vision API to interpret screenshots and locate UI elements.

Usage:
    python3 vision.py --image /tmp/shot.png --find "the Save button"
    python3 vision.py --image /tmp/shot.png --describe
    python3 vision.py --image /tmp/shot.png --find "Firefox address bar" --json
"""

import argparse
import base64
import json
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "anthropic package not installed. Run: pip3 install anthropic"
    }))
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Pillow package not installed. Run: pip3 install pillow"
    }))
    sys.exit(1)


def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get image width and height using Pillow."""
    with Image.open(image_path) as img:
        return img.size  # (width, height)


def encode_image(image_path: str) -> str:
    """Read and base64-encode an image file."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_media_type(image_path: str) -> str:
    """Determine media type from file extension."""
    ext = Path(image_path).suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/png")


def find_element(client: anthropic.Anthropic, image_path: str, element_description: str) -> dict:
    """Find a UI element in a screenshot by description."""
    width, height = get_image_dimensions(image_path)
    image_data = encode_image(image_path)
    media_type = get_media_type(image_path)

    prompt = (
        f"Look at this screenshot. Find the UI element described as: '{element_description}'.\n"
        f"Return JSON with these fields:\n"
        f"  - found (bool): whether you can see the element\n"
        f"  - x (int): pixel X coordinate of the element's center\n"
        f"  - y (int): pixel Y coordinate of the element's center\n"
        f"  - confidence (string): 'high', 'medium', or 'low'\n"
        f"  - description (string): brief description of what you see at that location\n"
        f"\n"
        f"The image is {width}x{height} pixels. Coordinates should be within these bounds.\n"
        f"Return ONLY valid JSON, no other text."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    response_text = response.content[0].text.strip()

    # Try to parse JSON from the response (handle markdown code blocks)
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (``` markers)
        json_lines = []
        inside = False
        for line in lines:
            if line.startswith("```") and not inside:
                inside = True
                continue
            elif line.startswith("```") and inside:
                break
            elif inside:
                json_lines.append(line)
        response_text = "\n".join(json_lines)

    result = json.loads(response_text)

    # Ensure element field is present
    if "element" not in result:
        result["element"] = element_description

    return result


def describe_screen(client: anthropic.Anthropic, image_path: str) -> str:
    """Describe what's visible on the screenshot."""
    image_data = encode_image(image_path)
    media_type = get_media_type(image_path)

    prompt = (
        "Describe what you see on this Linux desktop screenshot in 2-4 sentences. "
        "Include: what applications are open, what content is visible, any notable UI state."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    return response.content[0].text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Use Claude vision to interpret screenshots and find UI elements"
    )
    parser.add_argument("--image", required=True, help="Path to screenshot image file")
    parser.add_argument("--find", help="Description of the UI element to find")
    parser.add_argument("--describe", action="store_true", help="Describe the screen contents")
    parser.add_argument("--json", action="store_true", help="Force JSON output")

    args = parser.parse_args()

    # Validate image path
    if not Path(args.image).exists():
        error = {"success": False, "error": f"Image file not found: {args.image}"}
        print(json.dumps(error))
        sys.exit(1)

    # Validate mode
    if not args.find and not args.describe:
        error = {"success": False, "error": "Specify --find 'element' or --describe"}
        print(json.dumps(error))
        sys.exit(1)

    try:
        client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY from env
    except anthropic.AuthenticationError:
        error = {"success": False, "error": "ANTHROPIC_API_KEY not set or invalid"}
        print(json.dumps(error))
        sys.exit(1)

    try:
        if args.find:
            result = find_element(client, args.image, args.find)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result.get("found", False):
                    print(f"Found: {result.get('description', args.find)}")
                    print(f"Coordinates: ({result.get('x', '?')}, {result.get('y', '?')})")
                    print(f"Confidence: {result.get('confidence', 'unknown')}")
                    # Print JSON on the last line for easy parsing
                    print(json.dumps(result))
                else:
                    print(f"Not found: {args.find}")
                    print(json.dumps(result))

        elif args.describe:
            description = describe_screen(client, args.image)
            if args.json:
                print(json.dumps({
                    "success": True,
                    "description": description,
                    "error": None
                }, indent=2))
            else:
                print(description)

    except anthropic.APIError as e:
        error = {"found": False, "error": f"Anthropic API error: {str(e)}"}
        print(json.dumps(error))
        sys.exit(1)
    except json.JSONDecodeError as e:
        error = {"found": False, "error": f"Failed to parse vision response as JSON: {str(e)}"}
        print(json.dumps(error))
        sys.exit(1)
    except Exception as e:
        error = {"found": False, "error": f"Unexpected error: {str(e)}"}
        print(json.dumps(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
