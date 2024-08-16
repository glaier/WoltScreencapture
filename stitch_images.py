from PIL import Image
import os
import numpy as np

def image_to_grayscale(image):
    """Convert an image to grayscale."""
    return image.convert('L')

def compute_overlap(img1, img2):
    """Compute the maximum overlap between two images."""
    img1_gray = image_to_grayscale(img1)
    img2_gray = image_to_grayscale(img2)

    width, height1 = img1_gray.size
    _, height2 = img2_gray.size

    max_overlap = 0
    best_overlap = 0

    # Check for overlapping region
    for offset in range(-height2 + 1, height1):
        if offset < 0:
            img1_part = np.array(img1_gray.crop((0, -offset, width, height1)))
            img2_part = np.array(img2_gray.crop((0, 0, width, height2 + offset)))
        else:
            img1_part = np.array(img1_gray.crop((0, 0, width, height1 - offset)))
            img2_part = np.array(img2_gray.crop((0, offset, width, height2)))

        overlap = np.sum(img1_part == img2_part)
        if overlap > max_overlap:
            max_overlap = overlap
            best_overlap = offset

    return best_overlap

def adjust_images(img1, img2, overlap):
    """Adjust the images by cropping based on the overlap value."""
    width, height1 = img1.size
    _, height2 = img2.size

    if overlap > 0:
        img1 = img1.crop((0, 0, width, height1 - overlap))
        img2 = img2.crop((0, overlap, width, height2))
    elif overlap < 0:
        img1 = img1.crop((0, -overlap, width, height1))
        img2 = img2.crop((0, 0, width, height2 + overlap))

    return img1, img2

def create_long_screenshot(folder_path, output_path):
    """Create a long screenshot by stitching together images."""
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])

    if not image_files:
        raise ValueError("No PNG files found in the directory.")

    images = [Image.open(os.path.join(folder_path, file)) for file in image_files]

    final_width = images[0].width
    total_height = 0

    adjusted_images = [images[0]]
    for i in range(1, len(images)):
        overlap = compute_overlap(adjusted_images[-1], images[i])
        img1, img2 = adjust_images(adjusted_images[-1], images[i], overlap)
        adjusted_images[-1] = img1
        adjusted_images.append(img2)

    for img in adjusted_images:
        total_height += img.height

    long_screenshot = Image.new('RGB', (final_width, total_height))
    y_offset = 0
    for img in adjusted_images:
        long_screenshot.paste(img, (0, y_offset))
        y_offset += img.height

    long_screenshot.save(output_path)
    print(f"Long screenshot saved as {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python stitch_images.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_path = os.path.join(folder_path, 'long_screenshot.png')

    create_long_screenshot(folder_path, output_path)
