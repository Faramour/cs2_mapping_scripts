"""
Author: Faramour
Date: May 2024

Usage:
Script converts .tga frames of .mks textures into a single .tga frame sheet to be used for animated textures.
Input: relative path to the .mks texture (without extension) or directory containing .mks textures (script finds .mks textures if directory is provided)
Optional arguments:
    -o : Name of output .tga frame sheet. Works only for single-texture input
    -c : Number of columns in the frame sheet
"""

import os, argparse
from PIL import Image
import numpy as np

# inputs
parser = argparse.ArgumentParser( prog='make_frame_sheet', description='Creates .tga frame sheet from animated .mks textures imported by source1importer' )
parser.add_argument( 'input', help='name of texture or folder of textures. If folder is provided, script will find all .mks files')
parser.add_argument( '-o', default=None, dest='output', help='name of output texture frame sheet file (defaults to input name, works only for single texture input)')
parser.add_argument( '-c', dest='sheetCols', default=1, type=int, help='number of columns in the frame sheet (defaults to 1)')
args = parser.parse_args()

def makeFrameSheet(inputTexture, outputTexture=None, columnCount=1):
    frameFileName = lambda idx : inputTexture + f'{idx:03d}' + '.tga'

    if not os.path.isfile(frameFileName(0)):
        raise FileNotFoundError(f"File \'{frameFileName(0)}\' not found. At least 1 frame texture needed to make frame sheet.")

    frameCount = 1
    cond = True
    while cond:
        cond = os.path.isfile(frameFileName(frameCount))
        if cond:
            frameCount += 1

    sheetCols = columnCount
    if frameCount < sheetCols:
        sheetCols = frameCount

    # animated texture sheets have limit on number of rows/cols at 64 each
    while frameCount // sheetCols >= 64:
        sheetCols += 1

    sheetRows, rem = divmod(frameCount, sheetCols)
    if rem != 0:
        sheetRows += 1

    imageNP = np.array(Image.open(frameFileName(0)))
    width, height, channels = imageNP.shape

    frameSheet = np.zeros((width*sheetRows, height*sheetCols, channels), dtype=np.uint8)
    frame = 0
    for row in range(sheetRows):
        for col in range(sheetCols):
            if frame >= frameCount:
                break
            imageNP = np.array(Image.open(frameFileName(frame)))
            frameSheet[row*width:(row+1)*width, col*height:(col+1)*height] = imageNP
            frame += 1

    result = Image.fromarray(frameSheet)
    if outputTexture is None:
        result.save(inputTexture + '.tga')
    else:
        result.save(outputTexture + '.tga')
    
    return frameCount, sheetCols, sheetRows

def makeFrameSheetDirectory(inputDir, columnCount=1):
    createdSheets = []
    dir = os.fsencode(inputDir)
    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        texture, ext = os.path.splitext(filename)
        if ext == '.mks':
            frameCount, sheetCols, sheetRows = makeFrameSheet(texture, columnCount=columnCount)
            createdSheets.append([texture, frameCount, sheetCols, sheetRows])
    return createdSheets

if __name__ == "__main__":
    input = args.input
    outputTexture = args.output
    columns = args.sheetCols
    
    if os.path.isfile(input + '.mks'):
        # create single frame sheet file
        frameCount, sheetCols, sheetRows = makeFrameSheet(input, outputTexture, columns)
        print('In Texture Animation properties, input:')
        print(f'\tTexture: {input}.tga')
        print(f'\tAnimation Grid: {sheetCols} x {sheetRows}')
        print(f'Num Animation Cells: {frameCount}')

    elif os.path.isdir(input):
        # find .mks files in directory and create frame sheets for them
        createdSheets = makeFrameSheetDirectory(input, columns)
        if len(createdSheets):
            print("In Texture Animation properties, input:")
            for i in range(len(createdSheets)):
                print(f'\tTexture: {createdSheets[i][0]}.tga')
                print(f'\tAnimation Grid: {createdSheets[i][1]} x {createdSheets[i][2]}')
                print(f'\tNum Animation Cells: {createdSheets[i][3]}\n')
        else:
            print(f"No .mks files found in directory \'{input}\'")
        
    else:
        raise FileNotFoundError(f"Couldn't find directory or texture with given input: \'{input}\'")
