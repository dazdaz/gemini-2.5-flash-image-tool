# Vertex AI Gemini 2.5 Flash Image API CLI Tool

A command-line interface (CLI) tool for interacting with the **Vertex AI Gemini 2.5 Flash Image API**.

This script enables various image-based operations like **text-to-image generation**, **image editing**, and **creative composition** directly from your terminal.

---

## ⚡ Features

* **Text-to-Image Generation**: Create images from text descriptions.
* **Image Editing**: Modify images with a simple text prompt (add, remove, or change objects).
* **Photo Restoration**: Enhance old or damaged photos, remove scratches, and improve details.
* **Style Transfer**: Apply the style of one image to another, with or without a reference image.
* **Creative Composition**: Combine elements from multiple images (up to three) into a single new image.
* **Sketch to Image**: Turn a simple sketch into a detailed, fleshed-out image.
* **Add Text to Image**: Render text onto an image at a specified location.

---

## 🚀 Getting Started

### Quick Setup

The easiest way to get started is to run the setup script:

```bash
# Clone the repository
git clone https://github.com/dazdaz/gemini-2.5-flash-image-tool
cd gemini-2.5-flash-image-tool

# Run the setup script (creates virtual environment and installs dependencies)
chmod +x setup.sh
./setup.sh

# Set up IAM permissions (required for first-time setup)
chmod +x 01-setup-iam-permission.sh
./01-setup-iam-permission.sh
```

### Manual Setup

If you prefer to set up manually:

1. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Google Cloud**:
    - Authenticate: `gcloud auth login`
    - Set up application default credentials: `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform`
    - Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID`
    - Set up IAM permissions: `./01-setup-iam-permission.sh`

4. **Set environment variable**:
    ```bash
    export GOOGLE_CLOUD_PROJECT=your-project-id
    ```

### Prerequisites

* **Python 3.8+**
* **Google Cloud Project**: You need an active Google Cloud project with the Vertex AI API enabled.
* **Authentication**: Ensure you're authenticated with Google Cloud. The easiest way is to run:
    ```bash
    gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform
    ```

---

## 💡 Usage

### Using the Run Script (Recommended)

The easiest way to use the tool is with the provided run script, which handles the virtual environment automatically:

```bash
# Make the run script executable
chmod +x run.sh

# Use the run script (it will activate the virtual environment automatically)
./run.sh generate output.jpg -p "A sunset over mountains"
./run.sh edit input.jpg output.jpg -p "Remove the car"
```

### Manual Usage

If you prefer to run the tool manually:

1. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```

2. Set your project (if not already set):
    ```bash
    export GOOGLE_CLOUD_PROJECT=your-project-id
    ```

3. Run the tool:
    ```bash
    python aiphoto-tool.py <command> [options]
    ```

The tool uses a subcommand structure. The general syntax is:

```bash
python aiphoto-tool.py <command> [options]
```

---

## 💡 Usage

The tool uses a subcommand structure. The general syntax is:

```bash
python aiphoto-tool.py <command> [options]

# Example of text-to-image generation: creates a new image from a text prompt.
./aiphoto-tool.py generate -p "draw me a horse on the beach, gallopping into the sunset" horse.jpg

# Specify the aspect, else default to 16:19
./aiphoto-tool.py generate output.jpg -p "A sunset over mountains" --aspect-ratio 21:9
./aiphoto-tool.py edit input.jpg output.jpg -p "Remove the car" --aspect-ratio 1:1

# Example of image editing: modifies an input image based on a text prompt.
./aiphoto-tool.py edit 1.jpeg 1-myfile.jpeg -p "remove background"
./aiphoto-tool.py edit my_photo.jpeg my_photo_new_look.jpeg -p "change my clothes to a blue suit"

# Example of photo restoration: enhances an old or damaged photo.
./aiphoto-tool.py restore 1.jpeg 1-restored.jpeg -p "Fixing fading, tears, scratches but don't make any other changes"

# Example of sketch-to-image: transforms a sketch into a detailed image.
./aiphoto-tool.py sketch_to_image sketch.png -p "A photorealistic black sports car" detailed_car.png

# Example of adding text: renders text onto an image.
./aiphoto-tool.py add_text image.png -p "Add the words 'Happy Birthday!' in cursive at the top center of the image" new_image.png

# Example of creative composition: combines elements from multiple images.
./aiphoto-tool.py compose --input_file1 background.jpg --input_file2 person.png -p "Place the person from the second image in front of the background" final.png
./aiphoto-tool.py compose --input_file1 picofme.JPG --input_file2 cap.png -p "Place the cap from the second image onto the man's head in the first image but don't change any facial features" man_with_cap.jpeg

# Example of style transfer (text-based): applies a style described by a text prompt.
./aiphoto-tool.py style_transfer input.png stylized.png -p "In the style of a watercolor painting"

# Another example of style transfer (text-based): applies a style described by a text prompt.
./aiphoto-tool.py style_transfer input.png -p "In the style of a watercolor painting" stylized.png

# Example of style transfer (reference-based): uses a second image as a style reference.
./aiphoto-tool.py style_transfer input.png --style_ref_image my_style.png -p "Apply the style of the second image to the first" stylized.png
