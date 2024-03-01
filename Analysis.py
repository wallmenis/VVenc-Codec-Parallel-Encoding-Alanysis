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
TILE_NUMBERS = ["2x1", "2x2", "4x2", "4x4"]         # Tile configuration to be used.
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


def make_bar_graph(name_array, array, name_array_title, array_title, plot_title, plot_file):
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
        print(f"Now reading filesize of {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266")
        filesizeinthread.append(float(os.stat(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266").st_size))
        with open(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266.log","r") as infile:
            print(f"Now reading {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266.log")
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
        print(f"Now reading filesize of {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266")
        filesizeinthread.append(float(os.stat(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266").st_size))
        with open(f"{DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266.log","r") as infile:
            lines = infile.readlines()
            print(f"Now reading {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}-WPP.266.log")
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

# print(filesizes)
# print(bitrates)
# print(psnrs)
# print(times)

make_plot(np.array(THREAD_NUMBERS, dtype=float), times[0].T[0], "Number of threads used","Encoding Time (seconds)","Encoding Time vs Number of threads", f"{DATA_OUTPUT}/ET_VS_NT.svg")
make_plot(np.array(THREAD_NUMBERS, dtype=float), bitrates[0].T[0], "Number of threads used","Average Bitrate (kbps)","Average Bitrate vs Number of threads", f"{DATA_OUTPUT}/ABT_VS_NT.svg")
make_plot(np.array(THREAD_NUMBERS, dtype=float), psnrs[0].T[0], "Number of threads used","PSNR","PSNR vs Number of threads", f"{DATA_OUTPUT}/PSNR_VS_NT.svg")


make_plot(np.array(TILE_NUMBERS, dtype=float), times[0][0], "Tile configuration used","Encoding Time (seconds)","Encoding Time vs Tile configuration", f"{DATA_OUTPUT}/ET_VS_NTILE.svg")
make_plot(np.array(TILE_NUMBERS, dtype=float), bitrates[0][0], "Tile configuration used","Average Bitrate (kbps)","Average Bitrate vs Tile configuration", f"{DATA_OUTPUT}/ABT_VS_NTILE.svg")
make_plot(np.array(TILE_NUMBERS, dtype=float), psnrs[0][0], "Tile configuration used","PSNR","PSNR vs Tile configuration", f"{DATA_OUTPUT}/PSNR_VS_NTILE.svg")


make_bar_graph(["No WPP", "With WPP"], np.array([times[0][0][0], times[1][0][0]]), "WaveFront Synchronization", "Encoding Time (seconds)", "Encoding Time whether we use WaveFront Syncronization or not", f"{DATA_OUTPUT}/ET_VS_WPP.svg")
make_bar_graph(["No WPP", "With WPP"], np.array([bitrates[0][0][0], bitrates[1][0][0]]), "WaveFront Synchronization", "Average Bitrate (kbps)", "Average Bitrate whether we use WaveFront Syncronization or not", f"{DATA_OUTPUT}/ABT_VS_WPP.svg")
make_bar_graph(["No WPP", "With WPP"], np.array([psnrs[0][0][0], psnrs[1][0][0]]), "WaveFront Synchronization", "PSNR", "PSNR Values whether we use WaveFront Syncronization or not", f"{DATA_OUTPUT}/PSNR_VS_WPP.svg")
