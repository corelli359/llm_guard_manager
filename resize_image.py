from PIL import Image
import os

def resize_image(input_path, output_path, scale_factor=0.5):
    try:
        if not os.path.exists(input_path):
            print(f"Error: File '{input_path}' not found.")
            return

        with Image.open(input_path) as img:
            original_width, original_height = img.size
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            print(f"Original size: {original_width}x{original_height}")
            print(f"New size: {new_width}x{new_height}")

            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized_img.save(output_path)
            print(f"Successfully saved resized image to '{output_path}'")

    except ImportError:
        print("Error: Pillow library is not installed. Please install it using 'pip install Pillow'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    resize_image("new.png", "new_resized.png")
