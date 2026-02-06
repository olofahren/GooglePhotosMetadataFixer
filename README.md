# WIP
This project is work in progress :)

# Yet another Google Photos metadata fixer
A simple script to fix the mess that Google Photos creates when exporting your own photos using Google Takeout. 

I created this script since the other solutions for this problem did not work well enough for me. It gives you control of what happens to the images for which metadata cannot be parsed and written.

## What this script aims to do
When exporting your photos and videos from Google Photos using Google Takeout, the metadata of a large percentage of files are delivered in separate JSON files. This script writes the time stamp back into the metadata of the images and videos to facilitate transfer to another gallery/photo service (ex. Nextcloud, Opencloud, or similar)

## Supported file types
This script curretly supports 

* JPG/JPEG
* PNG
* HEIC (Converts to JPG)
* MP4

## Dependencies
* python
* pip
* poetry
* git

## How to use the script
1. Clone the repository
2. Enter the repository ``` cd GooglePhotosMetadataFixer ``
3. Create a Python venv ```python -m venv path/to/venv```
4. Enter the venv using ``` source venv/bin/activate```
5. Install dependencies with ```pip install -r requirements.txt``` (Do this )
6. Edit the file path at the top of ``` script.py ``` and run the script. 


## Disclaimer 
This project is in no way affiliated with Google or Alphabet Inc. 

This project is in active development and contains bugs. I do not guarantee that it will work flawlessly for you. You are welcome to try it, but use it at your own discretion. 

This project is only tested on my own specific dataset from Google Photos. While i have tried to cover all edgecases that arose in my own testing, this does not guarantee that the script will function correctly for all images in your dataset. 