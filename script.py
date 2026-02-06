#!/usr/bin/env python
import os
from functions.conversionFunctions import convertHEICtoJPEG
from functions.exifFunctions import writeMetadataDatetimeToImage
from functions.utilsFunctions import moveFileToSubfolder
from functions.videoFunctions import writeMetadataDatetimeToVideo
from functions.state import errorImages, imagesWithoutMetadataJson, incompatibleFileFormatImages, convertedImages

folder_path = "/home/olof/Downloads/TakeoutTests/takeout1"

#Main call script
def writeMetadataToAllImagesInFolder(folder):

    #get number of files in folder
    numFiles = sum(len(files) for _, _, files in os.walk(folder))
    countFilesDone = 0

    if(numFiles == 0):
        print("No files found in folder:", folder, "Exiting.")
        return
    
    for root, dirs, files in os.walk(folder):
        for filename in files:
            countFilesDone += 1
            print(f"({countFilesDone}/{numFiles})", end='\r', flush=True)
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
            print("Moved error files to subfolder 'error_files'.")
    print("All done! Exiting script.")

    
writeMetadataToAllImagesInFolder(folder_path)
