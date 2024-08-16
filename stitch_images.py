import os
from PIL import Image
import numpy as np

def get_most_frequent_grayscale_value(image):
    """Calculate the most frequent grayscale value in the image, which we'll treat as the background color."""
    histogram = image.histogram()
    most_frequent_value = np.argmax(histogram)
    return most_frequent_value

def compute_overlap(img1_gray, img2_gray, bg_color):
    """Compute the best vertical overlap between two grayscale images, ignoring the background color."""
    width = img1_gray.width
    height1 = img1_gray.height
    height2 = img2_gray.height

    max_overlap = 0
    best_overlap = 0

    # Only need to compare overlapping pixels, so limit to min(height1, height2) comparisons
    for offset in range(0, min(height1, height2)):
        # img2 is directly below img1 with no overlap at offset 0
        # As offset increases, img2 moves upward into img1
        img1_part = np.array(img1_gray.crop((0, height1 - offset - min(height1, height2), width, height1)))
        img2_part = np.array(img2_gray.crop((0, 0, width, min(height1, height2) - offset)))

        # Ensure we are comparing only the overlapping parts
        min_height = min(img1_part.shape[0], img2_part.shape[0])

        # Mask background pixels
        img1_mask = img1_part[:min_height] != bg_color
        img2_mask = img2_part[:min_height] != bg_color

        # Calculate the number of overlapping non-background pixels
        overlap = np.sum(img1_mask & img2_mask & (img1_part[:min_height] == img2_part[:min_height]))

        # Update the maximum overlap if this is the best so far
        if overlap > max_overlap:
            max_overlap = overlap
            best_overlap = offset

    return best_overlap

def remove_non_matching_rows(img1, img2, best_overlap):
    """Remove non-matching rows from img1 (bottom-up) and img2 (top-down)."""
    img1_np = np.array(img1)
    img2_np = np.array(img2)
    width, height1 = img1.size
    _, height2 = img2.size

    for i in range(height1 - best_overlap, height1):
        img1_row = img1_np[i, :]
        img2_row = img2_np[i - (height1 - best_overlap), :]
        
        if not np.array_equal(img1_row, img2_row):
            img1_np = np.delete(img1_np, i, axis=0)
            best_overlap -= 1

    # Adjust img2 by removing the top rows equivalent to the updated overlap
    img2_np = img2_np[best_overlap:, :]

    # Convert back to PIL Images
    img1 = Image.fromarray(img1_np)
    img2 = Image.fromarray(img2_np)

    return img1, img2, best_overlap

def create_long_screenshot(folder_path, output_path):
    """Stitch together multiple images into a long screenshot."""
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')])
    images = [Image.open(os.path.join(folder_path, f)).convert('L') for f in image_files]  # Convert all images to grayscale
    
    # Get the background color (most frequent grayscale value) from the first image
    bg_color = get_most_frequent_grayscale_value(images[0])

    # Start with the first image
    final_image = images[0]

    for i in range(1, len(images)):
        img2_gray = images[i]

        # Compute the best overlap between the current final image and the next one
        best_overlap = compute_overlap(final_image, img2_gray, bg_color)

        # Remove non-matching rows from the bottom of img1 and top of img2
        final_image, next_img, best_overlap = remove_non_matching_rows(final_image, img2_gray, best_overlap)

        # Combine the final image with the adjusted next image
        final_image = np.vstack((np.array(final_image), np.array(next_img[best_overlap:])))
        final_image = Image.fromarray(final_image)

    final_image.save(output_path)
    print(f"Long screenshot saved as {output_path}")

if __name__ == "__main__":
    folder_path = '/home/gunnarhellmundlaier/Downloads/WoltScreenshots/WoltScreenshotsAugust1'  # Replace with your path
    output_path = 'stitched_screenshot.png'  # Replace with your desired output path
    create_long_screenshot(folder_path, output_path)
