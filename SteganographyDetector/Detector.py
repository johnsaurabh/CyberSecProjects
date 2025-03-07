import cv2
import numpy as np
from PIL import Image, ImageDraw

def decode_lsb(image_path):
    """
    Decode a hidden message from an image using LSB steganography.
    """
    img = Image.open(image_path)
    pixels = img.load()
    binary_message = ""
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # Extract LSB from each color channel
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

    # Convert binary message to text
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        if byte:
            message += chr(int(byte, 2))
        else:
            break

    return message

def highlight_modified_pixels(image_path, output_path):
    """
    Highlight pixels modified by LSB steganography.
    """
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    mask = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            b, g, r = img[y, x]
            # Check if LSB is modified
            if (r & 1) or (g & 1) or (b & 1):
                mask[y, x] = 255  # Mark modified pixels

    # Highlight modified pixels
    highlighted_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    highlighted_img[mask == 255] = [255, 0, 0]  # Red color for modified pixels

    # Save the highlighted image
    highlighted_img = Image.fromarray(highlighted_img)
    highlighted_img.save(output_path)
    print(f"Highlighted image saved to {output_path}")

def main():
    image_path = "hidden_message.png"  # Replace with your image path
    output_path = "highlighted_image.png"

    # Decode the hidden message
    message = decode_lsb(image_path)
    print(f"Extracted Message: {message}")

    # Highlight modified pixels
    highlight_modified_pixels(image_path, output_path)

if __name__ == '__main__':
    main()