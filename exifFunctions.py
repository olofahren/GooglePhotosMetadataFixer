from datetime import datetime, time
from exif import Image
from PIL import Image as PILImage
import piexif
import ffmpeg

from JSONFunctions import getMetadataFromJSONFile, getPhotoTakenTimeFormattedUTCFromJSON
from timeFunctions import convertTimestampToExifTime
from state import errorImages, imagesWithoutMetadataJson

def readMetadataDatetimeFromImage(file):
    img = Image(open(file, 'rb'))
    if(not img.has_exif):
        return #"No EXIF metadata found for image file: " + file
    return img.datetime_original

def writeEXIFTimeToImage(file, exif_time):
    try:
        # Try using the exif library first
        with open(file, 'rb') as img_file:
            img = Image(img_file)
        
        img.datetime_original = exif_time
        
        with open(file, 'wb') as new_img_file:
            new_img_file.write(img.get_file())
    except Exception as e:
        # If exif library fails, use Pillow + piexif to add EXIF data
        # print(f"Image {file} has no/corrupted EXIF data. Using Pillow to add EXIF...")
        try:
            # Open image with Pillow
            pil_img = PILImage.open(file)
            
            # Create EXIF data structure
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Add datetime_original (tag 36867)
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_time.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_time.encode('utf-8')
            exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_time.encode('utf-8')
            
            # Convert to bytes
            exif_bytes = piexif.dump(exif_dict)
            
            # Save with EXIF data
            pil_img.save(file, exif=exif_bytes)
            # print(f"Successfully added EXIF data to {file}")
        except Exception as e2:
            print(f"Failed to add EXIF data using Pillow: {type(e2).__name__}: {e2}")
            return
    
    # Verify the write was successful
    try:
        writtenTime = readMetadataDatetimeFromImage(file)
        if(writtenTime != exif_time):
            print("Error writing to image EXIF time. Written time:", writtenTime, "Expected time:", exif_time)
    except Exception:
        pass

def writeMetadataDatetimeToImage(file):
    if(imageHasDateTimeMetadata(file)):
        # print("Image already has metadata:", file, ". Timestamp is", readMetadataDatetimeFromImage(file))
        return
    if(getMetadataFromJSONFile(file) is None):
        print("Metadata JSON file not found for image file:",file,". Setting to 1970-01-01 00:00:00",)
        exif_time = "1970:01:01 00:00:00"
        imagesWithoutMetadataJson.append(file)
    else:
        exif_time = convertTimestampToExifTime( getMetadataFromJSONFile(file)["photoTakenTime"]["timestamp"], getPhotoTakenTimeFormattedUTCFromJSON(file))

    writeEXIFTimeToImage(file, exif_time)

def imageHasDateTimeMetadata(file):
    
    if(file.endswith(".mp4") or file.endswith(".MP4")):
        try:
            probe_data = ffmpeg.probe(file)
            # Check format tags for creation time
            if 'format' in probe_data and 'tags' in probe_data['format']:
                tags = probe_data['format']['tags']
                print("Format tags:", tags)
                if 'creation_time' in tags:
                    print(f"Creation time: {tags['creation_time']}")
                    return True
            # Also check stream tags
            if 'streams' in probe_data:
                for stream in probe_data['streams']:
                    if 'tags' in stream and 'creation_time' in stream['tags']:
                        print(f"Stream creation time: {stream['tags']['creation_time']}")
                        return True
            return False
        except Exception as e:
            print(f"Error probing video file {file}: {e}")
            errorImages.append(file)
            return False
    else:
        try:
            img = Image(open(file, 'rb'))
        except Exception as e:
            # print(f"Error reading image file {file}: {e}")
            errorImages.append(file)
            return False
        return img.has_exif and hasattr(img, 'datetime_original')