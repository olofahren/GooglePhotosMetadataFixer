#!/usr/bin/env python
import os
from functions.conversionFunctions import convertHEICtoJPEG
from functions.exifFunctions import writeMetadataDatetimeToImage
from functions.utilsFunctions import deleteAllMetadataJsonFilesInFolder, moveFileToSubfolder, extractAllJsonFileEndingsInFolder
from functions.videoFunctions import writeMetadataDatetimeToVideo
from functions.state import errorImages, imagesWithoutMetadataJson, incompatibleFileFormatImages, convertedImages
import functions.state

folder_path = "/home/olof/Downloads/TakeoutTests/takeout1"

#Main call script
def writeMetadataToAllImagesInFolder(folder):

    functions.state.candidates = extractAllJsonFileEndingsInFolder(folder)
    
    # print("Found JSON file endings in folder", folder, ":")
    # for ending in functions.state.candidates:
    #     print(ending , "\n")
    # print("Press any key to continue...")
    # input()

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

# Handle post-processing and reporting after all files have been processed
    if(errorImages):
        print("\n\n\n\n")
        print("The following files had errors during processing:")
        for errFile in errorImages:
            print(errFile)
        print("\n\n\n\n")

    if(imagesWithoutMetadataJson):
        print("The following image files had no metadata JSON file. \n These files were set to 1970-01-01 00:00:00 or had year extracted from file path if possible:")
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
    
    #handle files with errors
    if(errorImages):
        print("Some files could not be opened and and no metadata has been wrritten to them. \n Would you like to move the error files to a subfolder named 'error_files'? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            for errFile in errorImages:
                moveFileToSubfolder(errFile, folder_path + "/error_files")
            print("Moved error files to subfolder 'error_files'.")
    
    print("\n\n\n\n")
    
    if(incompatibleFileFormatImages):
        print("Would you like to move the incompatible format files to a subfolder named 'incompatible_files'? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            for errFile in incompatibleFileFormatImages:
                moveFileToSubfolder(errFile, folder_path + "/incompatible_files")
            print("Moved incompatible format files to subfolder 'incompatible_files'.")
    
    print("\n\n\n\n")

    print("Would you like to delete all metadata JSON files? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        print("This action cannot be undone. If you want to get them back, redownload the data from Google Takeout or extract the zip files again. \n Are you absolutely sure? (y/n)")
        confirm = input().strip().lower()
        if confirm == 'y':
            deleteAllMetadataJsonFilesInFolder(folder_path)
            print("Deleted all metadata JSON files in the folder.")

    print("\n\n\n\n")
    print("Summary: ")
    print("Total files processed:", numFiles)
    print("Files with errors:", len(errorImages))
    print("Files without metadata JSON:", len(imagesWithoutMetadataJson))
    print("Incompatible format files:", len(incompatibleFileFormatImages))
    print("HEIC files converted to JPEG:", len(convertedImages))
    print("\n")
    print("Success rate:", round((numFiles - len(errorImages) - len(incompatibleFileFormatImages)) / numFiles * 100, 2), "%")
    print("\n\n\n\n")

    print("All done! Exiting script.")


    
writeMetadataToAllImagesInFolder(folder_path)
