from PIL import Image

def convert_to_vga_format(image_path, output_size=(320, 240)):
    """
    Convert an image to ESP32 VGA-compatible format
    Args:
        image_path: Path to source image
        output_size: Target size (width, height)
    Returns:
        bytes: Image data in ESP32-compatible format
    """
    try:
        # Open and resize image
        img = Image.open(image_path).convert('RGB')
        img = img.resize(output_size)
        
        # Convert to 14-bit RGB format (5-6-5)
        pixels = []
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = img.getpixel((x, y))
                # Convert to 5-6-5 format
                pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixels.append(pixel)
        
        # Convert to bytes
        return bytes(pixels)
    except Exception as e:
        print(f"Error converting image: {e}")
        return None
