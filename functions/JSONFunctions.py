
import json
import os


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


def getPhotoTakenTimeFormattedUTCFromJSON(file):
    metadata = getMetadataFromJSONFile(file)
    return metadata["photoTakenTime"]["formatted"]