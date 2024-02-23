import os
import re
import numpy as np
import matplotlib.pyplot as plt


def get_file(path, oftype):
    files_in_path = os.listdir(path)
    if not re.search(".*/", path):
        path = path + "/"
    for i in files_in_path:
        if re.search(oftype, i):
            return path + i
    return None


# You may modify below as you preffer
ROUNDING = 2                                        # How many decimal diggits will be kept when making the graphs

VIDEO_FRAMERATE = "120"
VIDEO_RESOLUTION = "1920x1080"
VIDEO_BIT_DEPTH = "8"                               # If we check later, we also change the internal bit depth.
                                                    # This is to match the input with the output bit depth.
VVENC_CONFIG_FILE = "vvenc_configuration.cfg"
VVENC_BIN = "vvenc/bin/release-static/vvencFFapp"   # Path for vvenc binary
VIDEO_INPUT = get_file("SourceVideo", ".yuv")       # Input file. Get file function implemented for ease of use
DATA_OUTPUT = "Data"                                # Outpout directory
THREAD_NUMBERS = ["1", "2", "4", "6", "8"]          # How many threads are used per instance
TILE_NUMBERS = ["2", "4", "6", "8"]                 # How many tiles by dimentions to use (eg. if 8 it will do 8
                                                    # collumns by 8 rows (--Tiles=8x8 when calling vvenc ))
# Checks both with WFS (WaveFront Syncronization) and without will be done regardless
# We do them by appending --WaveFrontSynchro=1 when calling vvenc for WFS and
# --WaveFrontSynchro=0 for no WFS


def make_plot(array1, array2, name_of_array_1, name_of_array_2, plot_name, plot_file):
    plt.figure(figsize=(12, 8))
    plt.plot(array1, array2, marker='o', linestyle='-', color='b', label=f"{name_of_array_1} vs {name_of_array_2}")

    plt.xlabel(name_of_array_1)
    plt.ylabel(name_of_array_2)
    plt.title(plot_name)
    plt.grid(True)

    for i, txt in enumerate(zip(array1, array2)):
        plt.annotate(f'({txt[0]}, {txt[1]})', (array1[i], array2[i]), textcoords="offset points", xytext=(5, 0), ha='left')

    plt.savefig(plot_file)
    plt.close()


def make_bar_graph(array, name_array, array_title, name_array_title, plot_title, plot_file):
    plt.figure(figsize=(12, 8))
    plt.bar(name_array, array, color='red', width=0.4)
    plt.xlabel(name_array_title)
    plt.ylabel(array_title)
    plt.title(plot_title)
    plt.grid(True)
    for i, txt in enumerate(array):
        plt.annotate(txt, (i, array[i]), ha='center')
    plt.savefig(plot_file)
    plt.close()


if not os.path.isfile(VVENC_BIN):
    print("VVenc not in specified folder.")
    print("")
    print("Did you forget to build it? If you want to build it, you may run ./build_vvenc.sh or consult build documentation (https://github.com/fraunhoferhhi/vvenc/wiki/Build) if running from windows.")
    exit()

if VIDEO_INPUT is None:
    print("Video file not found. Please check your attributes")
    exit()

for THREAD in THREAD_NUMBERS:
    for TILE in TILE_NUMBERS:
        print(f"Now processing {VIDEO_INPUT} with tiling {TILE}x{TILE} , {THREAD} threads and no WPP")
        os.system(f"{VVENC_BIN} --InputFile {VIDEO_INPUT} -c {VVENC_CONFIG_FILE} --FrameRate {VIDEO_FRAMERATE} --Size {VIDEO_RESOLUTION} --InputBitDepth {VIDEO_BIT_DEPTH} --Tiles {TILE}x{TILE} --Threads {THREAD} --WaveFrontSynchro 0 --InternalBitDepth {VIDEO_BIT_DEPTH} --BitstreamFile {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266 > {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266.log")
        print(f"Now processing {VIDEO_INPUT} with tiling {TILE}x{TILE} , {THREAD} threads with WPP")
        os.system(f"{VVENC_BIN} --InputFile {VIDEO_INPUT} -c {VVENC_CONFIG_FILE} --FrameRate {VIDEO_FRAMERATE} --Size {VIDEO_RESOLUTION} --InputBitDepth {VIDEO_BIT_DEPTH} --Tiles {TILE}x{TILE} --Threads {THREAD} --WaveFrontSynchro 1 --InternalBitDepth {VIDEO_BIT_DEPTH}  --BitstreamFile {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266 > {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266.log")
print("Generation and processing DONE!")

times = []
bitrates = []
psnrs = []
filesizes = []

timeswpp = []
bitrateswpp = []
psnrswpp = []
filesizeswpp = []

for THREAD in THREAD_NUMBERS:
    timeinthread = []
    bitrateinthread = []
    psnrinthread = []
    filesizeinthread = []
    for TILE in TILE_NUMBERS:
        filesizeinthread.append(float(os.stat(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266").st_size))
        with open(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266.log","r") as infile:
            lines = infile.readlines()
            for i in range(len(lines)):
                if re.search("YUV-PSNR", lines[i]):
                    line = lines[i+1].split()
                    bitrateinthread.append(float(line[4]))
                    psnrinthread.append(float(line[8]))
                if re.search("Total Time", lines[i]):
                    line = lines[i].split()
                    timeinthread.append(float(line[7]))
    timeswpp.append(timeinthread)
    bitrateswpp.append(bitrateinthread)
    psnrswpp.append(psnrinthread)
    filesizeswpp.append(filesizeinthread)

times.append(timeswpp)
bitrates.append(bitrateswpp)
psnrs.append(psnrswpp)
filesizes.append(filesizeswpp)

timeswpp = []
bitrateswpp = []
psnrswpp = []
filesizeswpp = []

for THREAD in THREAD_NUMBERS:
    timeinthread = []
    bitrateinthread = []
    psnrinthread = []
    filesizeinthread = []
    for TILE in TILE_NUMBERS:
        filesizeinthread.append(float(os.stat(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266").st_size))
        with open(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266.log","r") as infile:
            lines = infile.readlines()
            for i in range(len(lines)):
                if re.search("YUV-PSNR", lines[i]):
                    line = lines[i+1].split()
                    bitrateinthread.append(float(line[4]))
                    psnrinthread.append(float(line[8]))
                if re.search("Total Time", lines[i]):
                    line = lines[i].split()
                    timeinthread.append(float(line[7]))
    timeswpp.append(timeinthread)
    bitrateswpp.append(bitrateinthread)
    psnrswpp.append(psnrinthread)
    filesizeswpp.append(filesizeinthread)

times.append(timeswpp)
bitrates.append(bitrateswpp)
psnrs.append(psnrswpp)
filesizes.append(filesizeswpp)

filesizes = np.array(filesizes)
bitrates = np.array(bitrates)
psnrs = np.array(psnrs)
times = np.array(times)

make_plot(filesizes[0][0], bitrates[0][0], "Filesize (bytes)", "Bitrates (Kbps)", "Filesize VS Bitrate", f"{DATA_OUTPUT}/Filesize_vs_bitrate.svg")
