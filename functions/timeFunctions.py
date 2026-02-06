from datetime import datetime
import os

import pytz


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

def getPhotoYearFromPhotoPath(file):
    # Extract year from file path, assuming format like "Takeout/Photos/2022/09/09/photo.jpg"
    parts = file.split(os.sep)
    for part in parts:
        if("Photos" in part):
            subparts = part.split(" ")
            for subpart in subparts:
                if subpart.isdigit() and len(subpart) == 4:  # Check for 4-digit year
                    return subpart
    return None