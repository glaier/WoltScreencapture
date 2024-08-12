import pytesseract
from PIL import Image
import sys
import os

# Set up Tesseract command path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update with your actual path to tesseract executable

def extract_text_from_image(image_path):
    # Open the image and extract text using OCR
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='dan')
    return text

def save_raw_text(text, raw_text_file):
    with open(raw_text_file, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Raw OCR text saved to {raw_text_file}")

def process_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder {folder_path} does not exist.")
        sys.exit(1)

    # Process each PNG file in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            raw_text_file = os.path.splitext(image_path)[0] + '_ocr_output.txt'

            print(f"Processing {image_path}...")

            # Extract text from the image
            text = extract_text_from_image(image_path)
            
            # Save the raw OCR text to a file
            save_raw_text(text, raw_text_file)

def main():
    if len(sys.argv) != 2:
        print("Usage: python OCRtoTXT.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    process_folder(folder_path)

if __name__ == "__main__":
    main()
