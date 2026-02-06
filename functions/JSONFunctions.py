import json
import os

from . import state


def getMetadataFromJSONFile(file):
    base_name = os.path.basename(file)
    directory = os.path.dirname(file)

    metadata_path = None
    for candidate in state.candidates:
        candidate_path = os.path.join(directory, base_name + "." + candidate)
        if os.path.exists(candidate_path):
            metadata_path = candidate_path
            break

    if metadata_path is None:
        return None

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata


def getPhotoTakenTimeFormattedUTCFromJSON(file):
    metadata = getMetadataFromJSONFile(file)
    return metadata["photoTakenTime"]["formatted"]