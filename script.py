from datetime import datetime, time
import json
from exif import Image
from datetime import datetime
import pytz
import os
from PIL import Image as PILImage
import piexif
import ffmpeg
import sys
from pprint import pprint # for printing Python dictionaries in a human-readable way

errorImages: list = []
imagesWithoutMetadataJson: list = []
incompatibleFileFormatImages: list = []
convertedImages: list = []

#General functions
def getMetadataFromJSONFile(file):
    base_name = os.path.basename(file)
    directory = os.path.dirname(file)

    candidates = [
        base_name + ".supplemental-metadata.json",
        base_name + ".supplemen.json",
        base_name + ".suppl.json",
        base_name + ".supplemental-metad.json",
        base_name + ".supplemental-me.json",
        base_name + ".supplemental-met.json",
        base_name + ".supplemental-metadat.json"
    ]

    metadata_path = None
    for candidate in candidates:
        candidate_path = os.path.join(directory, candidate)
        if os.path.exists(candidate_path):
            metadata_path = candidate_path
            break

    if metadata_path is None:
        return None

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata


#Time/date metadata section
def getPhotoTakenTimeFormattedUTCFromJSON(file):
    metadata = getMetadataFromJSONFile(file)
    return metadata["photoTakenTime"]["formatted"]


def readMetadataDatetimeFromImage(file):
    img = Image(open(file, 'rb'))
    if(not img.has_exif):
        return #"No EXIF metadata found for image file: " + file
    return img.datetime_original

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


def getTimezoneOffsetFromFormattedTimestamp(timestamp):
    # timestamp format: "9 Sept 2022, 19:47:03 UTC"
    date, time_part = timestamp.split(", ")
    day, month, year = date.split(" ")
    
    # Remove "UTC" from time_part
    time_part = time_part.replace(" UTC", "")
    hours, minutes, seconds = time_part.split(":")
    
    # Handle non-standard month abbreviations like "Sept"
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Sept': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    month_num = month_map.get(month)
    if not month_num:
        month_num = datetime.strptime(month, "%B").month
    dt = datetime(int(year), month_num, int(day), int(hours), int(minutes), int(seconds))
    
    # Use Sweden's timezone
    sweden_tz = pytz.timezone('Europe/Stockholm')
    dt_aware = sweden_tz.localize(dt)
    
    # Get UTC offset in hours
    timezone_offset_hours = dt_aware.utcoffset().total_seconds() / 3600
    return timezone_offset_hours

def convertTimestampToExifTime(timestamp, formattedTimestamp):
    timestamp = int(timestamp)
    
    # Create timezone-aware datetime in Sweden's timezone
    sweden_tz = pytz.timezone('Europe/Stockholm')
    dt = datetime.fromtimestamp(timestamp, tz=sweden_tz)

    # Format the datetime object to EXIF time format (YYYY:MM:DD HH:MM:SS)
    exif_time = dt.strftime("%Y:%m:%d %H:%M:%S")
    return exif_time

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


# Video metadata section
def getCreationTimeFromVideo(file):
    """Extract creation_time from video metadata"""
    try:
        probe_data = ffmpeg.probe(file)
        # Check format tags first
        if 'format' in probe_data and 'tags' in probe_data['format']:
            tags = probe_data['format']['tags']
            if 'creation_time' in tags:
                return tags['creation_time']
        # Check stream tags
        if 'streams' in probe_data:
            for stream in probe_data['streams']:
                if 'tags' in stream and 'creation_time' in stream['tags']:
                    return stream['tags']['creation_time']
        return None
    except Exception as e:
        print(f"Error getting creation time from video {file}: {e}")
        return None

def updateFileSystemTimestamp(file, timestamp_str):
    """Update file system modification and access time to match metadata timestamp
    timestamp_str format: '2022-09-09T17:47:03.000000Z' (ISO 8601)"""
    try:
        # Parse ISO 8601 timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Convert to Unix timestamp
        unix_time = dt.timestamp()
        # Set both access time and modification time
        os.utime(file, (unix_time, unix_time))
        # print(f"Updated file system timestamp for {file} to {timestamp_str}")
    except Exception as e:
        print(f"Error updating file system timestamp for {file}: {e}")

def writeMetadataDatetimeToVideo(file):
    """Update video file system timestamp to match its metadata creation_time"""
    creation_time = getCreationTimeFromVideo(file)
    if creation_time:
        updateFileSystemTimestamp(file, creation_time)
    else:
        print(f"No creation_time found in video metadata for {file}")
        #set to epoch time if no metadata found
        updateFileSystemTimestamp(file, '1970-01-01T00:00:00.000000Z')

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
def moveFileToSubfolder(file, subfolder):
    try:
        os.makedirs(subfolder, exist_ok=True)
        new_path = os.path.join(subfolder, os.path.basename(file))
        os.rename(file, new_path)
        print(f"Moved {file} to {new_path}")
    except Exception as e:
        print(f"Error moving file {file} to subfolder {subfolder}: {e}")

#Main call script
def writeMetadataToAllImagesInFolder(folder):
    
    #get number of files in folder
    numFiles = sum(len(files) for _, _, files in os.walk(folder))
    
    for root, dirs, files in os.walk(folder):
        for filename in files:
            print(f"({files.index(filename)+1}/{numFiles})", end='\r', flush=True)
            filepath = os.path.join(root, filename)
            if filename.endswith((".mp4", ".MP4")):
                writeMetadataDatetimeToVideo(filepath)
            elif filename.endswith((".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")):
                writeMetadataDatetimeToImage(filepath)
            elif(filename.endswith((".HEIC", ".heic"))):
                jpeg_file = convertHEICtoJPEG(filepath)
                if jpeg_file:
                    convertedImages.append(jpeg_file)
                    writeMetadataDatetimeToImage(jpeg_file)
                else:
                    incompatibleFileFormatImages.append(filename)

            elif(not filename.endswith((".json", ".supplemental-metadata.json", ".supplemen.json"))):
                print("!!! Skipping unsupported file:", filename)
                incompatibleFileFormatImages.append(filename)
    print("Done writing metadata to all images and videos in folder:", folder)

    if(errorImages):
        print("\n\n\n\n")
        print("The following files had errors during processing:")
        for errFile in errorImages:
            print(errFile)
        print("\n\n\n\n")

    if(imagesWithoutMetadataJson):
        print("The following image files had no metadata JSON file:")
        for imgFile in imagesWithoutMetadataJson:
            print(imgFile)
        print("\n\n\n\n")

    if(incompatibleFileFormatImages):
        print("The following files had unsupported formats and were skipped:")
        for imgFile in incompatibleFileFormatImages:
            print(imgFile)
        print("\n\n\n\n")
    if(convertedImages):
        print("The following HEIC images were converted to JPEG:")
        for imgFile in convertedImages:
            print(imgFile)
        print("\n\n\n\n")
    
    if(errorImages):
        print("Would you like to move the error files to a subfolder named 'error_files'? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            for errFile in errorImages:
                moveFileToSubfolder(errFile, folder_path + "/error_files")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path>")
        print("Example: python script.py /home/user/photos")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        sys.exit(1)
    
    writeMetadataToAllImagesInFolder(folder_path)
