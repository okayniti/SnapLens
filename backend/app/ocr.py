"""
SnapLens — OCR Module

Extracts text from screenshot images using Tesseract OCR.

How OCR works (simplified):
1. Image is loaded and converted to a format Tesseract can read
2. Tesseract identifies character shapes in the image
3. It matches shapes to known letters/numbers using trained models
4. Returns the recognized text as a string

Tesseract is great for screenshots because they have clean, digital text.
For handwritten or messy text, you'd need a more advanced model like PaddleOCR.
"""

import pytesseract
from PIL import Image

# Tell pytesseract where Tesseract is installed on Windows
# This avoids needing to set the system PATH variable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(image_path: str) -> str:
    """
    Extract text from an image file using Tesseract OCR.

    Args:
        image_path: Path to the image file on disk

    Returns:
        Extracted text as a string (stripped of extra whitespace)

    Why we use Pillow (PIL) to open the image first:
    - Tesseract needs a proper image object, not just a file path on all systems
    - PIL handles format conversion automatically (webp, bmp, etc.)
    - It also lets us preprocess the image later if needed (resize, grayscale, etc.)
    """
    # Open image using Pillow
    image = Image.open(image_path)

    # Run Tesseract OCR on the image
    # pytesseract.image_to_string() is the core function
    # It sends the image to Tesseract and returns extracted text
    raw_text = pytesseract.image_to_string(image)

    # Clean up: remove leading/trailing whitespace and extra blank lines
    cleaned_text = raw_text.strip()

    return cleaned_text
