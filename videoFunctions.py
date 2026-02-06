# Video metadata section
import ffmpeg
from utilsFunctions import updateFileSystemTimestamp


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



def writeMetadataDatetimeToVideo(file):
    """Update video file system timestamp to match its metadata creation_time"""
    creation_time = getCreationTimeFromVideo(file)
    if creation_time:
        updateFileSystemTimestamp(file, creation_time)
    else:
        print(f"No creation_time found in video metadata for {file}")
        #set to epoch time if no metadata found
        updateFileSystemTimestamp(file, '1970-01-01T00:00:00.000000Z')
