from datetime import datetime
import os

import pytz


def moveFileToSubfolder(file, subfolder):
    try:
        os.makedirs(subfolder, exist_ok=True)
        new_path = os.path.join(subfolder, os.path.basename(file))
        os.rename(file, new_path)
        print(f"Moved {file} to {new_path}")
    except Exception as e:
        print(f"Error moving file {file} to subfolder {subfolder}: {e}")

def updateFileSystemTimestamp(file, timestamp_str):
    """Update file system modification and access time to match metadata timestamp
    timestamp_str format: '2022-09-09T17:47:03.000000Z' (ISO 8601)
    or '2 Jun 2013, 19:15:16 UTC'"""
    try:
        # Parse ISO 8601 timestamp first
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            # Parse "2 Jun 2013, 19:15:16 UTC" style timestamps
            parsed = None
            for fmt in ("%d %b %Y, %H:%M:%S UTC", "%d %B %Y, %H:%M:%S UTC"):
                try:
                    parsed = datetime.strptime(timestamp_str, fmt)
                    break
                except ValueError:
                    continue
            if parsed is None:
                raise
            dt = parsed
            dt = pytz.UTC.localize(dt)
        # Convert to Unix timestamp
        unix_time = dt.timestamp()
        # Set both access time and modification time
        os.utime(file, (unix_time, unix_time))
        # print(f"Updated file system timestamp for {file} to {timestamp_str}")
    except Exception as e:
        print(f"Error updating file system timestamp for {file}: {e}")