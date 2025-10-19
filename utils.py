# utils.py

import os
from PIL import Image, ImageTk, UnidentifiedImageError # Import specific PIL error

def load_image(path, width, height):
    # 1. Check if file exists (crucial for debugging paths)
    if not os.path.exists(path):
        print(f"⚠️ ERROR: Image file NOT FOUND at path: {path}")
        return None
        
    try:
        # 2. Open and resize the image
        img = Image.open(path)
        img = img.resize((width, height), Image.LANCZOS)
        
        # 3. Convert to Tkinter format
        return ImageTk.PhotoImage(img)
        
    except FileNotFoundError:
        # This is redundant due to the os.path.exists check, but good for safety
        print(f"⚠️ ERROR: File not found (FileNotFoundError): {path}")
        return None
        
    except UnidentifiedImageError:
        # This catches issues where the file exists but isn't a recognizable image format
        print(f"❌ ERROR: Cannot identify image file format (UnidentifiedImageError) for: {path}")
        print("   -> Check the file's extension (is it .jpg, .png, etc.?)")
        return None
        
    except Exception as e:
        # Catch any other unexpected issues (like permissions or internal PIL errors)
        print(f"🛑 UNEXPECTED ERROR loading image {path}: {e}")
        return None