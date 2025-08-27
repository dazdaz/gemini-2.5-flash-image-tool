#!/usr/bin/env python3

import os
import argparse
import mimetypes
from PIL import Image as PILImage

try:
    from google.genai import Client
    from google.genai.types import GenerateContentConfig, Part
    import google.auth
except ImportError:
    print("Error: Required Google libraries not found.")
    print("Please install dependencies using 'uv pip install -r requirements.txt'")
    print("requirements.txt should contain: google-genai, google-auth, Pillow")
    exit(1)

# --- Configuration ---
LOCATION = "global"  # Use global endpoint for Vertex AI
MODEL_ID = "gemini-2.5-flash-image-preview"
MAX_RESOLUTION = "1024x1024"

# --- Initialize Vertex AI Client ---
client = None
PROJECT_ID = ""

def initialize_client():
    global client
    global PROJECT_ID
    if client:
        return client

    try:
        PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
    except KeyError:
        print("Warning: GOOGLE_CLOUD_PROJECT environment variable not set.")
        PROJECT_ID = "your-project-id" # Placeholder

    try:
        credentials, project_id_auth = google.auth.default()
        if PROJECT_ID == "your-project-id" and project_id_auth:
            PROJECT_ID = project_id_auth

        client = Client(vertexai=True, project=PROJECT_ID, location=LOCATION, credentials=credentials)
        print(f"Client initialized for project {PROJECT_ID} in {LOCATION}")
    except Exception as e:
        print(f"Error initializing client: {e}")
        print("Please ensure you have authenticated with Google Cloud (e.g., 'gcloud auth application-default login') and the Vertex AI API is enabled.")
    return client

def load_image_part(image_path: str) -> Part | None:
    """Loads an image from a file path and returns a GenAI Part."""
    image_path = os.path.expanduser(image_path)
    if not os.path.exists(image_path):
        print(f"Error: Input image file not found at {image_path}")
        return None
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith("image/"):
            ext = os.path.splitext(image_path)[1].lower()
            if ext in {".jpg", ".jpeg"}: mime_type = "image/jpeg"
            elif ext == ".png": mime_type = "image/png"
            elif ext == ".webp": mime_type = "image/webp"
            elif ext == ".bmp": mime_type = "image/bmp"
            else:
                print(f"Warning: Could not determine MIME type for {image_path}. Attempting image/jpeg.")
                mime_type = "image/jpeg"

        print(f"Loaded image {os.path.basename(image_path)} as {mime_type}")
        return Part.from_bytes(data=image_bytes, mime_type=mime_type)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def call_gemini_api(contents: list, output_path: str):
    """Sends the content parts to Gemini API and saves the resulting image."""
    if not initialize_client():
        print("Client not initialized. Cannot proceed.")
        return

    if not contents:
        print("Error: No content provided for the API call.")
        return

    output_path = os.path.expanduser(output_path)

    try:
        print(f"Sending request to Gemini model: {MODEL_ID}...")
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                candidate_count=1,
            ),
        )

        print("Response received.")
        if response.candidates:
            has_image = False
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    print("---")
                    print("### Received Image Output:")
                    try:
                        with open(output_path, "wb") as f:
                            f.write(part.inline_data.data)
                        print(f"Output image saved to {output_path} (Max resolution: {MAX_RESOLUTION})")
                        has_image = True
                    except Exception as e:
                        print(f"Error saving image: {e}")
                elif part.text:
                    print(f"Model Text Response: {part.text}")
            if not has_image:
                print("No image data received in the response.")
        else:
            print("No candidates returned in the response.")
            if hasattr(response, 'prompt_feedback'):
                print(f"Prompt Feedback: {response.prompt_feedback}")

    except Exception as e:
        print(f"An error occurred during API call: {e}")

# --- Command Handlers ---
def handle_generate(args):
    print("Mode: Text-to-Image Generation")
    contents = [args.prompt]
    call_gemini_api(contents, args.output_file)

def handle_edit(args):
    print("Mode: Image Editing")
    image_part = load_image_part(args.input_file)
    if image_part:
        contents = [image_part, args.prompt]
        call_gemini_api(contents, args.output_file)

def handle_restore(args):
    print("Mode: Photo Restoration")
    image_part = load_image_part(args.input_file)
    if image_part:
        contents = [image_part, args.prompt]
        call_gemini_api(contents, args.output_file)

def handle_style_transfer(args):
    print("Mode: Style Transfer")
    input_image_part = load_image_part(args.input_file)
    if not input_image_part: return

    contents = [input_image_part]
    if args.style_ref_image:
        style_image_part = load_image_part(args.style_ref_image)
        if not style_image_part: return
        contents.append(style_image_part)
        print(f"Using style reference image: {os.path.basename(args.style_ref_image)}")

    contents.append(args.prompt)
    call_gemini_api(contents, args.output_file)

def handle_compose(args):
    print("Mode: Creative Composition")
    contents = []
    input_parts = {
        "input1": args.input_file1,
        "input2": args.input_file2,
        "input3": args.input_file3,
    }
    for key, path in input_parts.items():
        if path:
            image_part = load_image_part(path)
            if not image_part: return
            contents.append(image_part)
    if not contents:
        print("Error: At least one input image is required for compose mode.")
        return
    contents.append(args.prompt)
    call_gemini_api(contents, args.output_file)

def handle_add_text(args):
    print("Mode: Add Text to Image")
    image_part = load_image_part(args.input_file)
    if image_part:
        contents = [image_part, args.prompt]
        call_gemini_api(contents, args.output_file)

def handle_sketch_to_image(args):
    print("Mode: Sketch to Image")
    image_part = load_image_part(args.input_file)
    if image_part:
        contents = [image_part, args.prompt]
        call_gemini_api(contents, args.output_file)

# --- Main Execution & Argument Parsing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "CLI tool for Gemini 2.5 Flash Image API features on Vertex AI.\n"
            f"Model ID: {MODEL_ID}\n"
            f"Max Output Resolution: {MAX_RESOLUTION}\n"
            "Installation: uv pip install -r requirements.txt\n\n"
            "General Usage:\n"
            "  ./multi-photo.py <command> -p \"Your text prompt...\" [options] [INPUT_FILE(s)] [OUTPUT_FILE]\n\n"
            "Most commands require:\n"
            "  1. A text prompt: Use -p or --prompt.\n"
            "  2. Input and/or output file paths.\n\n"
            "Use './multi-photo.py <command> -h' for details on each command's specific arguments."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True, help="Available image operations")

    # --- Generate ---
    parse_generate = subparsers.add_parser("generate", help="Text-to-image generation.")
    parse_generate.add_argument("output_file", help="OUTPUT_FILE path to save the generated image.")
    parse_generate.add_argument("-p", "--prompt", required=True, help="Text prompt for image generation.")
    parse_generate.set_defaults(func=handle_generate)

    # --- Edit ---
    parse_edit = subparsers.add_parser("edit", help="General mask-free image editing (add/remove/move objects, change backgrounds).")
    parse_edit.add_argument("input_file", help="INPUT_FILE path to the image to edit.")
    parse_edit.add_argument("output_file", help="OUTPUT_FILE path to save the edited image.")
    parse_edit.add_argument("-p", "--prompt", required=True, help="Text prompt describing the edit (e.g., 'Remove the car', 'Make the sky blue').")
    parse_edit.set_defaults(func=handle_edit)

    # --- Restore ---
    parse_restore = subparsers.add_parser("restore", help="Restore and enhance old or damaged photos.")
    parse_restore.add_argument("input_file", help="INPUT_FILE path to the old image to restore.")
    parse_restore.add_argument("output_file", help="OUTPUT_FILE path to save the restored image.")
    parse_restore.add_argument(
        "-p", "--prompt",
        default="Restore this photograph: enhance colors, improve details and sharpness, and remove defects like scratches or fading.",
        help="Prompt for restoration guidance."
    )
    parse_restore.set_defaults(func=handle_restore)

    # --- Style Transfer ---
    parse_style = subparsers.add_parser("style_transfer", help="Apply a new style to an image.")
    parse_style.add_argument("input_file", help="INPUT_FILE path to the content image.")
    parse_style.add_argument("output_file", help="OUTPUT_FILE path to save the stylized image.")
    parse_style.add_argument("-p", "--prompt", required=True, help="Prompt describing the desired style (e.g., 'In the style of Van Gogh') or how to use the reference.")
    parse_style.add_argument("--style_ref_image", help="(Optional) STYLE_REF_IMAGE path to an image to use as style reference.", required=False)
    parse_style.set_defaults(func=handle_style_transfer)

    # --- Compose ---
    parse_compose = subparsers.add_parser("compose", help="Combine elements from up to 3 reference images and text.")
    parse_compose.add_argument("output_file", help="OUTPUT_FILE path to save the composed image.")
    parse_compose.add_argument("-p", "--prompt", required=True, help="Prompt describing how to combine the images.")
    parse_compose.add_argument("--input_file1", required=True, help="INPUT_FILE1 path to the first input image.")
    parse_compose.add_argument("--input_file2", help="(Optional) INPUT_FILE2 path to the second input image.")
    parse_compose.add_argument("--input_file3", help="(Optional) INPUT_FILE3 path to the third input image.")
    parse_compose.set_defaults(func=handle_compose)

    # --- Add Text ---
    parse_add_text = subparsers.add_parser("add_text", help="Render text on an image.")
    parse_add_text.add_argument("input_file", help="INPUT_FILE path to the image.")
    parse_add_text.add_argument("output_file", help="OUTPUT_FILE path to save the image with text.")
    parse_add_text.add_argument("-p", "--prompt", required=True, help="Prompt describing the text and its placement (e.g., 'Add title \"Summer Fest\" at the top').")
    parse_add_text.set_defaults(func=handle_add_text)

    # --- Sketch to Image ---
    parse_sketch = subparsers.add_parser("sketch_to_image", help="Generate a detailed image from a sketch.")
    parse_sketch.add_argument("input_file", help="INPUT_FILE path to the sketch image.")
    parse_sketch.add_argument("output_file", help="OUTPUT_FILE path to save the generated image.")
    parse_sketch.add_argument("-p", "--prompt", default="Flesh out this sketch into a detailed color image.", help="Optional prompt to guide generation.")
    parse_sketch.set_defaults(func=handle_sketch_to_image)

    args = parser.parse_args()
    args.func(args)

