from PIL import Image as PILImage

def convertHEICtoJPEG(file):
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        heic_image = PILImage.open(file)
        jpeg_file = file.rsplit('.', 1)[0] + '.jpg'
        heic_image.convert('RGB').save(jpeg_file, "JPEG")
        print("Converted HEIC to JPEG:", jpeg_file)
        return jpeg_file
    except ImportError:
        print(f"Error: pillow-heif not installed. Cannot convert {file}")
        print("Install it with: pip install pillow-heif")
        return None
    except Exception as e:
        print(f"Error converting HEIC to JPEG for {file}: {e}")
        return None