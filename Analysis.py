import sys
import os
import re
import json
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
VVENC_BIN = "vvenc/bin/release-static/vvencFFapp"     # Path for vvenc binary
VIDEO_INPUT = get_file("SourceVideo", ".yuv")       # Input file. Get file function implemented for ease of use
DATA_OUTPUT = "Data"                                # Outpout directory
THREAD_NUMBERS = ["2", "4", "6", "8"]               # How many threads are used per instance
TILE_NUMBERS = ["2", "4", "6", "8"]                 # How many tiles by dimentions to use (eg. if 8 it will do 8
                                                    # collumns by 8 rows (--Tiles=8x8 when calling vvenc ))
# Checks both with WFS (WaveFront Syncronization) and without will be done regardless
# We do them by appending --WaveFrontSynchro=1 when calling vvenc for WFS and
# --WaveFrontSynchro=0 for no WFS


# to be removed...
VIDEO_CODECS = ["libx264", "libx265"]
VIDEO_QP_VALUES = ["10", "23", "30", "40", "50"]
VIDEO_PRESETS = ["veryfast", "fast", "medium", "slow", "veryslow"]


def get_from_codec(codec, input_array):
    output_array = np.copy(input_array)
    codec_index = VIDEO_CODECS.index(codec)
    space_between_parts = int(output_array.size/(len(VIDEO_CODECS)))
    output_array = output_array[space_between_parts*codec_index:space_between_parts*(codec_index+1)]
    return output_array


def get_from_preset_and_codec(preset, codec, input_array):
    output_array = np.copy(input_array)
    preset_index = VIDEO_PRESETS.index(preset)
    codec_index = VIDEO_CODECS.index(codec)
    space_between_parts = int(output_array.size/(len(VIDEO_CODECS)))
    output_array = output_array[space_between_parts*codec_index:space_between_parts*(codec_index+1)]
    space_between_parts = int(output_array.size/(len(VIDEO_PRESETS)))
    output_array = output_array[space_between_parts*preset_index:space_between_parts*(preset_index+1)]
    return output_array


def make_plot(array1, array2, name_of_array_1, name_of_array_2, plot_name, plot_file):
    plt.figure(figsize=(12, 8))
    plt.plot(array1, array2, marker='o', linestyle='-', color='b', label=f"{name_of_array_1} vs {name_of_array_2}")

    # Adding labels and title
    plt.xlabel(name_of_array_1)
    plt.ylabel(name_of_array_2)
    plt.title(plot_name)
    plt.grid(True)

    for i, txt in enumerate(zip(array1, array2)):
        plt.annotate(f'({txt[0]}, {txt[1]})', (array1[i], array2[i]), textcoords="offset points", xytext=(5, 0), ha='left')

    plt.savefig(plot_file)
    plt.close()
    # plt.show()


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
    # plt.show()


if not os.path.isfile(VVENC_BIN):
    print("VVenc not in specified folder.")
    print("")
    print("Did you forget to build it? If you want to build it, you may run ./build_vvenc.sh or consult build documentation (https://github.com/fraunhoferhhi/vvenc/wiki/Build) if running from windows.")
    exit()

if VIDEO_INPUT is None:
    print("Video file not found. Please check your attributes")
    exit()

null_dir = "/dev/null"          # Assumes unix-like,
if sys.platform == "win32":     # unless shown otherwise...
    null_dir = "NUL"

# print(len(sys.argv))
if len(sys.argv) < 3:
    # yuv420p because 4:2:0 video with progressive scan.
    for THREAD in THREAD_NUMBERS:
        for TILE in TILE_NUMBERS:
            print(f"Now processing {VIDEO_INPUT} with tiling {TILE}x{TILE} , {THREAD} threads and no WFS")
            os.system(f"{VVENC_BIN} --InputFile {VIDEO_INPUT} --FrameRate {VIDEO_FRAMERATE} --Size {VIDEO_RESOLUTION} -c yuv420 --Tiles {TILE}x{TILE} --Threads {THREAD} --WaveFrontSynchro 0  --BitstreamFile {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266")
            print(f"Now processing {VIDEO_INPUT} with tiling {TILE}x{TILE} , {THREAD} threads with WFS")
            os.system(f"{VVENC_BIN} --InputFile {VIDEO_INPUT} --FrameRate {VIDEO_FRAMERATE} --Size {VIDEO_RESOLUTION} -c yuv420 --Tiles {TILE}x{TILE} --Threads {THREAD} --WaveFrontSynchro 1  --BitstreamFile {DATA_OUTPUT}/output-threads{THREAD}-tile{TILE}.266")
    print("Generation and processing DONE!")
    for CODEC in VIDEO_CODECS:
        for PRESET in VIDEO_PRESETS:
            for QP in VIDEO_QP_VALUES:
                # for RCODEC in VIDEO_CODECS:
                #     print(
                #         f"Now calculating psnr of {VIDEO_INPUT} with source codec {CODEC} with preset {PRESET}, quantization parameter {QP} and refference codec {RCODEC}."
                #     )
                #     os.system(
                #         f'ffmpeg -i {VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.mkv -i {VIDEO_INPUT}-lossless-{RCODEC}.mkv -filter_complex "psnr" -f null {null_dir} 2> {VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}-{RCODEC}-psnr.log'
                #     )

               print( f"Now calculating psnr of {VIDEO_INPUT} with source codec {CODEC} with preset {PRESET}, quantization parameter {QP}.")
               os.system(f'ffmpeg -i {VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.mkv -s:v {VIDEO_RESOLUTION} -r {VIDEO_FRAMERATE} -i {VIDEO_INPUT} -filter_complex "psnr" -f null {null_dir} 2> {VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}-psnr.log')
                    # -i : input,  before -i we put the attributes of the input file.
                    # -filter_complex : selects the filter graph to be used, in this case, the psnr filter graph is being used.
                    # Since we don't need the output from the filter complex and only the terminal output, we just it to /dev/null
                    # the input format is set to null because we want it to autodetect it
        print( f"Now calculating psnr of {VIDEO_INPUT} with source codec {CODEC} that is lossless.")
        os.system(f'ffmpeg -i {VIDEO_INPUT}-lossless-{CODEC}.mkv -s:v {VIDEO_RESOLUTION} -r {VIDEO_FRAMERATE} -i {VIDEO_INPUT} -filter_complex "psnr" -f null {null_dir} 2> {VIDEO_INPUT}-lossless-{CODEC}-psnr.log')
        # Same as above but for the lossless video
    print("PSNR calculations DONE!")


average_QP_values = []
average_QP_lossless_values = []
times = []
times_lossless = []
y_psnr_values = []
u_psnr_values = []
v_psnr_values = []
a_psnr_values = []
ma_psnr_values = []
mi_psnr_values = []

y_psnr_lossless_values = []
u_psnr_lossless_values = []
v_psnr_lossless_values = []
a_psnr_lossless_values = []
ma_psnr_lossless_values = []
mi_psnr_lossless_values = []

filesizes = []
filesizes_lossless = []

# This ran on a friend's computer because the ammount of processing is too big
# for my laptop to handle. He had a ready script that counted the filesizes
# and it outputs it to a json file.
json_is_there = 1
try:
    json_file = "file_sizes.json"
    with open(json_file) as json_data:
        jdata = json.load(json_data)
except Exception:
    json_is_there = 0

for CODEC in VIDEO_CODECS:
    for PRESET in VIDEO_PRESETS:
        for QP in VIDEO_QP_VALUES:
            if json_is_there == 1:
                filesizes.append(int(jdata[f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.mkv"]))
            else:
                filesizes.append(os.stat(f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.mkv").st_size)
    if json_is_there == 1:
        filesizes_lossless.append(int(jdata[f"{VIDEO_INPUT}-lossless-{CODEC}.mkv"]))
    else:
        filesizes_lossless.append(os.stat(f"{VIDEO_INPUT}-lossless-{CODEC}.mkv").st_size)

avgQPfloat = 0
for CODEC in VIDEO_CODECS:
    for PRESET in VIDEO_PRESETS:
        if CODEC == "libx264":
            with open(f"{VIDEO_INPUT}-lossless-{CODEC}.log") as reader:
                counter = 0
                for line in reader:
                    if re.search("rtime", line):
                        bench = line
                        time = re.sub("s", "", re.sub(".*rtime=", "", bench))
                        time = re.sub("\n", "", time)
                        times_lossless.append(float(time))
                    if re.search("Avg QP", line):
                        bench = line
                        avgQP = re.sub(".* Avg QP:", "", re.sub("size:.*", "", bench))
                        avgQP = re.sub("\n", "", avgQP)
                        counter = counter + 1
                        avgQPfloat += float(avgQP)
                    if counter == 3:
                        avgQPfloat = avgQPfloat / 3.0
                        average_QP_lossless_values.append(avgQPfloat)
                        counter = 0
                        avgQPfloat = 0
        if CODEC == "libx265":
            with open(f"{VIDEO_INPUT}-lossless-{CODEC}.log") as reader:
                for line in reader:
                    if re.search("rtime", line):
                        bench = line
                        time = re.sub("s", "", re.sub(".*rtime=", "", bench))
                        time = re.sub("\n", "", time)
                        times_lossless.append(float(time))
                    if re.search("encoded ", line):
                        bench = line
                        avgQP = re.sub(".* Avg QP:", "", bench)
                        avgQP = re.sub("\n", "", avgQP)
                        average_QP_lossless_values.append(float(avgQP))
        for QP in VIDEO_QP_VALUES:
            if CODEC == "libx264":
                with open(f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.log") as reader:
                    counter = 0
                    for line in reader:
                        if re.search("rtime", line):
                            bench = line
                            time = re.sub("s", "", re.sub(".*rtime=", "", bench))
                            time = re.sub("\n", "", time)
                            times.append(float(time))
                        if re.search("Avg QP", line):
                            bench = line
                            avgQP = re.sub(".* Avg QP:", "", re.sub("size:.*", "", bench))
                            avgQP = re.sub("\n", "", avgQP)
                            counter = counter + 1
                            avgQPfloat += float(avgQP)
                        if counter == 3:
                            avgQPfloat = avgQPfloat / 3.0
                            average_QP_values.append(avgQPfloat)
                            counter = 0
                            avgQPfloat = 0
            if CODEC == "libx265":
                with open(f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}.log") as reader:
                    for line in reader:
                        if re.search("rtime", line):
                            bench = line
                            time = re.sub("s", "", re.sub(".*rtime=", "", bench))
                            time = re.sub("\n", "", time)
                            times.append(float(time))
                        if re.search("encoded ", line):
                            bench = line
                            avgQP = re.sub(".* Avg QP:", "", bench)
                            avgQP = re.sub("\n", "", avgQP)
                            average_QP_values.append(float(avgQP))
# for RCODEC in VIDEO_CODECS:
for CODEC in VIDEO_CODECS:
    for PRESET in VIDEO_PRESETS:
        for QP in VIDEO_QP_VALUES:
            with open(
                # f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}-{RCODEC}-psnr.log"
                f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}-psnr.log"
            ) as reader:
                for line in reader:
                    if re.search("PSNR", line):
                        psnr = line
                        psnr = re.sub(".* PSNR", "", psnr)
                        psnr = re.sub(" ", "", psnr, 1)
                        y = re.sub(" .*", "", re.sub("y:", "", psnr))
                        u = re.sub(" .*", "", re.sub(".*u:", "", psnr))
                        v = re.sub(" .*", "", re.sub(".*v:", "", psnr))
                        average = re.sub(" .*", "", re.sub(".*average:", "", psnr))
                        minimum = re.sub(" .*", "", re.sub(".*min:", "", psnr))
                        maximum = re.sub(" .*", "", re.sub(".*max:", "", psnr))
                        y_psnr_values.append(float(y))
                        u_psnr_values.append(float(u))
                        v_psnr_values.append(float(v))
                        a_psnr_values.append(float(average))
                        mi_psnr_values.append(float(minimum))
                        ma_psnr_values.append(float(maximum))
    with open(
        f"{VIDEO_INPUT}-{PRESET}-{QP}-{CODEC}-psnr.log"
    ) as reader:
        for line in reader:
            if re.search("PSNR", line):
                psnr = line
                psnr = re.sub(".* PSNR", "", psnr)
                psnr = re.sub(" ", "", psnr, 1)
                y = re.sub(" .*", "", re.sub("y:", "", psnr))
                u = re.sub(" .*", "", re.sub(".*u:", "", psnr))
                v = re.sub(" .*", "", re.sub(".*v:", "", psnr))
                average = re.sub(" .*", "", re.sub(".*average:", "", psnr))
                minimum = re.sub(" .*", "", re.sub(".*min:", "", psnr))
                maximum = re.sub(" .*", "", re.sub(".*max:", "", psnr))
                y_psnr_lossless_values.append(float(y))
                u_psnr_lossless_values.append(float(u))
                v_psnr_lossless_values.append(float(v))
                a_psnr_lossless_values.append(float(average))
                mi_psnr_lossless_values.append(float(minimum))
                ma_psnr_lossless_values.append(float(maximum))

average_QP_values = np.array(average_QP_values)
times = np.array(times)
y_psnr_values = np.array(y_psnr_values)
u_psnr_values = np.array(u_psnr_values)
v_psnr_values = np.array(v_psnr_values)
a_psnr_values = np.array(a_psnr_values)
ma_psnr_values = np.array(ma_psnr_values)
mi_psnr_values = np.array(mi_psnr_values)
filesizes = np.array(filesizes)

average_QP_lossless_values = np.array(average_QP_lossless_values)
times_lossless = np.array(times_lossless)
y_psnr_lossless_values = np.array(y_psnr_lossless_values)
u_psnr_lossless_values = np.array(u_psnr_lossless_values)
v_psnr_lossless_values = np.array(v_psnr_lossless_values)
a_psnr_lossless_values = np.array(a_psnr_lossless_values)
ma_psnr_lossless_values = np.array(ma_psnr_lossless_values)
mi_psnr_lossless_values = np.array(mi_psnr_lossless_values)
filesizes_lossless = np.array(filesizes_lossless)

times_veryfast = get_from_preset_and_codec("veryfast", "libx264", times)
times_fast = get_from_preset_and_codec("fast", "libx264", times)
times_medium = get_from_preset_and_codec("medium", "libx264", times)
times_slow = get_from_preset_and_codec("slow", "libx264", times)
times_veryslow = get_from_preset_and_codec("veryslow", "libx264", times)

times_averages = np.array([np.sum(times_veryfast), np.sum(times_fast), np.sum(times_medium), np.sum(times_slow), np.sum(times_veryslow)])
times_averages = np.round(times_averages/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

times_averages_x264 = times_averages.copy()

make_bar_graph(times_averages, VIDEO_PRESETS, "Average times (seconds)", "Presets", "Average time it took to compress with each preset in h264.", "AVG_TIME_PRESET_x264.svg")
make_bar_graph(np.round(times_veryfast, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset veryfast per QP value in h264.", "VERYFAST_TIME_QP_x264.svg")
make_bar_graph(np.round(times_fast, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset fast per QP value in h264.", "FAST_TIME_QP_x264.svg")
make_bar_graph(np.round(times_medium, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset medium per QP value in h264.", "MEDIUM_TIME_QP_x264.svg")
make_bar_graph(np.round(times_slow, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset slow per QP value in h264.", "SLOW_TIME_QP_x264.svg")
make_bar_graph(np.round(times_veryslow, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset veryslow per QP value in h264.", "VERYSLOW_TIME_QP_x264.svg")

times_veryfast = get_from_preset_and_codec("veryfast", "libx265", times)
times_fast = get_from_preset_and_codec("fast", "libx265", times)
times_medium = get_from_preset_and_codec("medium", "libx265", times)
times_slow = get_from_preset_and_codec("slow", "libx265", times)
times_veryslow = get_from_preset_and_codec("veryslow", "libx265", times)

times_averages = np.array([np.sum(times_veryfast), np.sum(times_fast), np.sum(times_medium), np.sum(times_slow), np.sum(times_veryslow)])
times_averages = np.round(times_averages/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

times_averages_x265 = times_averages.copy()

make_bar_graph(times_averages, VIDEO_PRESETS, "Average times (seconds)", "Presets", "Average time it took to compress with each preset in h265.", "AVG_TIME_PRESET_x265.svg")
make_bar_graph(np.round(times_veryfast, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset veryfast per QP value in h265.", "VERYFAST_TIME_QP_x265.svg")
make_bar_graph(np.round(times_fast, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset fast per QP value in h265.", "FAST_TIME_QP_x265.svg")
make_bar_graph(np.round(times_medium, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset medium per QP value in h265.", "MEDIUM_TIME_QP_x265.svg")
make_bar_graph(np.round(times_slow, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset slow per QP value in h265.", "SLOW_TIME_QP_x265.svg")
make_bar_graph(np.round(times_veryslow, decimals=ROUNDING), VIDEO_QP_VALUES, "Times (seconds)", "QP Values", "Time it took to compress with preset veryslow per QP value in h265.", "VERYSLOW_TIME_QP_x265.svg")

times_averages = np.array([np.sum(times_averages_x264), np.sum(times_averages_x265)])
times_averages = np.round(times_averages/float(len(VIDEO_PRESETS)), decimals=ROUNDING)

make_bar_graph(times_averages, VIDEO_CODECS, "Average Times (Seconds)", "Presets", "h264 vs h265 in average time to encode (Seconds)", "AVG_TIME_PRESET_h264_V_h265.svg")

filesizes_veryfast = np.round(get_from_preset_and_codec("veryfast", "libx264", filesizes)/(1024*1024), decimals=ROUNDING)
filesizes_fast = np.round(get_from_preset_and_codec("fast", "libx264", filesizes)/(1024*1024), decimals=ROUNDING)
filesizes_medium = np.round(get_from_preset_and_codec("medium", "libx264", filesizes)/(1024*1024), decimals=ROUNDING)
filesizes_slow = np.round(get_from_preset_and_codec("slow", "libx264", filesizes)/(1024*1024), decimals=ROUNDING)
filesizes_veryslow = np.round(get_from_preset_and_codec("veryslow", "libx264", filesizes)/(1024*1024), decimals=ROUNDING)

filesizes_averages = np.array([np.sum(filesizes_veryfast), np.sum(filesizes_fast), np.sum(filesizes_medium), np.sum(filesizes_slow), np.sum(filesizes_veryslow)])
filesizes_averages = np.round(filesizes_averages/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

filesizes_averages_x264 = filesizes_averages.copy()

make_bar_graph(filesizes_averages, VIDEO_PRESETS, "Average Sizes (Mb)", "Presets", "Average space it took to compress with each preset in h264.", "AVG_FILESIZE_PRESET_x264.svg")
make_bar_graph(filesizes_veryfast, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset veryfast per QP value in h264.", "VERYFAST_FILESIZE_QP_x264.svg")
make_bar_graph(filesizes_fast, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset fast per QP value in h264.", "FAST_FILESIZE_QP_x264.svg")
make_bar_graph(filesizes_medium, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset medium per QP value in h264.", "MEDIUM_FILESIZE_QP_x264.svg")
make_bar_graph(filesizes_slow, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset slow per QP value in h264.", "SLOW_FILESIZE_QP_x264.svg")
make_bar_graph(filesizes_veryslow, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset veryslow per QP value in h264.", "VERYSLOW_FILESIZE_QP_x264.svg")

filesizes_veryfast = np.round(get_from_preset_and_codec("veryfast", "libx265", filesizes)/(1024*1024), decimals=ROUNDING )
filesizes_fast = np.round(get_from_preset_and_codec("fast", "libx265", filesizes)/(1024*1024), decimals=ROUNDING )
filesizes_medium = np.round(get_from_preset_and_codec("medium", "libx265", filesizes)/(1024*1024), decimals=ROUNDING )
filesizes_slow = np.round(get_from_preset_and_codec("slow", "libx265", filesizes)/(1024*1024), decimals=ROUNDING )
times_veryslow = np.round(get_from_preset_and_codec("veryslow", "libx265", filesizes)/(1024*1024), decimals=ROUNDING )

filesizes_averages = np.array([np.sum(filesizes_veryfast), np.sum(filesizes_fast), np.sum(filesizes_medium), np.sum(filesizes_slow), np.sum(filesizes_veryslow)])
filesizes_averages = np.round(filesizes_averages/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

filesizes_averages_x265 = filesizes_averages.copy()

make_bar_graph(filesizes_averages, VIDEO_PRESETS, "Average Sizes (Mb)", "Presets", "Average space it took to compress with each preset in h265.", "AVG_FILESIZE_PRESET_x265.svg")
make_bar_graph(filesizes_veryfast, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset veryfast per QP value in h265.", "VERYFAST_FILESIZE_QP_x265.svg")
make_bar_graph(filesizes_fast, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset fast per QP value in h265.", "FAST_FILESIZE_QP_x265.svg")
make_bar_graph(filesizes_medium, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset medium per QP value in h265.", "MEDIUM_FILESIZE_QP_x265.svg")
make_bar_graph(filesizes_slow, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset slow per QP value in h265.", "SLOW_FILESIZE_QP_x265.svg")
make_bar_graph(filesizes_veryslow, VIDEO_QP_VALUES, "Sizes (Mb)", "QP Values", "Space it took to compress with preset veryslow per QP value in h265.", "VERYSLOW_FILESIZE_QP_x265.svg")

filesizes_averages = np.array([np.sum(filesizes_averages_x264), np.sum(filesizes_averages_x265)])
filesizes_averages = np.round(filesizes_averages/float(len(VIDEO_PRESETS)), decimals=ROUNDING)

make_bar_graph(filesizes_averages, VIDEO_CODECS, "Average Sizes (Mb)", "Presets", "h264 vs h265 in average filesize (Mb)", "AVG_FILESIZE_PRESET_h264_V_h265.svg")

average_QP_values_veryfast = get_from_preset_and_codec("veryfast", "libx264", average_QP_values)
average_QP_values_fast = get_from_preset_and_codec("fast", "libx264", average_QP_values)
average_QP_values_medium = get_from_preset_and_codec("medium", "libx264", average_QP_values)
average_QP_values_slow = get_from_preset_and_codec("slow", "libx264", average_QP_values)
average_QP_values_veryslow = get_from_preset_and_codec("veryslow", "libx264", average_QP_values)

a_psnr_values_veryfast = get_from_preset_and_codec("veryfast", "libx264", a_psnr_values)
a_psnr_values_fast = get_from_preset_and_codec("fast", "libx264", a_psnr_values)
a_psnr_values_medium = get_from_preset_and_codec("medium", "libx264", a_psnr_values)
a_psnr_values_slow = get_from_preset_and_codec("slow", "libx264", a_psnr_values)
a_psnr_values_veryslow = get_from_preset_and_codec("veryslow", "libx264", a_psnr_values)

VIDEO_QP_VALUES_NUM=np.array([int(numeric_string) for numeric_string in VIDEO_QP_VALUES])

make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_veryfast, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h264 veryfast", "QP_V_PSNR_H264_VERYFAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_fast, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h264 fast", "QP_V_PSNR_H264_FAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_medium, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h264 medium", "QP_V_PSNR_H264_MEDIUM.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_slow, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h264 slow", "QP_V_PSNR_H264_SLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_veryslow, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h264 veryslow", "QP_V_PSNR_H264_VERYSLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_veryfast, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h264 veryfast", "QP_V_QP_ACTUAL_H264_VERYFAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_fast, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h264 fast", "QP_V_QP_ACTUAL_H264_FAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_medium, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h264 medium", "QP_V_QP_ACTUAL_H264_MEDIUM.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_slow, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h264 slow", "QP_V_QP_ACTUAL_H264_SLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_veryslow, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h264 veryslow", "QP_V_QP_ACTUAL_H264_VERYSLOW.svg")

average_a_psnr_values_x264 = np.array([ np.sum(a_psnr_values_veryfast), np.sum( a_psnr_values_fast), np.sum( a_psnr_values_medium), np.sum( a_psnr_values_slow), np.sum(a_psnr_values_veryslow) ])
average_a_psnr_values_x264 = np.round(average_a_psnr_values_x264/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

average_QP_values_veryfast = get_from_preset_and_codec("veryfast", "libx265", average_QP_values)
average_QP_values_fast = get_from_preset_and_codec("fast", "libx265", average_QP_values)
average_QP_values_medium = get_from_preset_and_codec("medium", "libx265", average_QP_values)
average_QP_values_slow = get_from_preset_and_codec("slow", "libx265", average_QP_values)
average_QP_values_veryslow = get_from_preset_and_codec("veryslow", "libx265", average_QP_values)

a_psnr_values_veryfast = get_from_preset_and_codec("veryfast", "libx265", a_psnr_values)
a_psnr_values_fast = get_from_preset_and_codec("fast", "libx265", a_psnr_values)
a_psnr_values_medium = get_from_preset_and_codec("medium", "libx265", a_psnr_values)
a_psnr_values_slow = get_from_preset_and_codec("slow", "libx265", a_psnr_values)
a_psnr_values_veryslow = get_from_preset_and_codec("veryslow", "libx265", a_psnr_values)

make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_veryfast, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h265 veryfast", "QP_V_PSNR_H265_VERYFAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_fast, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h265 fast", "QP_V_PSNR_H265_FAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_medium, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h265 medium", "QP_V_PSNR_H265_MEDIUM.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_slow, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h265 slow", "QP_V_PSNR_H265_SLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(a_psnr_values_veryslow, decimals=ROUNDING), "QP Values", "PSNR Values", "QP setting values vs PSNR values on h265 veryslow", "QP_V_PSNR_H265_VERYSLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_veryfast, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h265 veryfast", "QP_V_QP_ACTUAL_H265_VERYFAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_fast, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h265 fast", "QP_V_QP_ACTUAL_H265_FAST.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_medium, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h265 medium", "QP_V_QP_ACTUAL_H265_MEDIUM.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_slow, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h265 slow", "QP_V_QP_ACTUAL_H265_SLOW.svg")
make_plot(VIDEO_QP_VALUES_NUM, np.round(average_QP_values_veryslow, decimals=ROUNDING), "QP Values", "QP Actual Values", "QP setting values vs QP Actual values on h265 veryslow", "QP_V_QP_ACTUAL_H265_VERYSLOW.svg")

average_a_psnr_values_x265 = np.array([ np.sum(a_psnr_values_veryfast), np.sum( a_psnr_values_fast), np.sum( a_psnr_values_medium), np.sum( a_psnr_values_slow), np.sum(a_psnr_values_veryslow) ])
average_a_psnr_values_x265 = np.round(average_a_psnr_values_x265/float(len(VIDEO_QP_VALUES)), decimals=ROUNDING)

make_bar_graph(average_a_psnr_values_x264, VIDEO_PRESETS, "PSNR Values", "Presets", "h264 average quality (PSNR) per preset setting", "PRESET_AVG_PSNR_X264.svg")
make_bar_graph(average_a_psnr_values_x265, VIDEO_PRESETS, "PSNR Values", "Presets", "h265 average quality (PSNR) per preset setting", "PRESET_AVG_PSNR_X265.svg")

average_a_psnr_values = np.array([np.sum(average_a_psnr_values_x264), np.sum(average_a_psnr_values_x265)])
average_a_psnr_values = np.round(average_a_psnr_values/float(len(VIDEO_PRESETS)), decimals=ROUNDING)

make_bar_graph(average_a_psnr_values, VIDEO_CODECS, "PSNR Values", "Codecs", "h264 vs h265 in average quality (PSNR)", "PSNR_X264_V_X265.svg")

a_psnr_values_x264_lossless = get_from_codec("libx264", a_psnr_lossless_values)
a_psnr_values_x265_lossless = get_from_codec("libx265", a_psnr_lossless_values)

average_a_psnr_values_lossless = np.array([np.sum(a_psnr_values_x264_lossless), np.sum(a_psnr_values_x265_lossless)])

make_bar_graph(average_a_psnr_values_lossless, VIDEO_CODECS, "PSNR Values", "Codecs", "h264 vs h265 quality in lossless compression (PSNR)", "PSNR_X264_V_X265_LOSSLESS.svg")

times_x264_lossless = get_from_codec("libx264", times_lossless)
times_x265_lossless = get_from_codec("libx265", times_lossless)

times_values_lossless = np.array([np.sum(times_x264_lossless), np.sum(times_x265_lossless)])

make_bar_graph(times_values_lossless, VIDEO_CODECS, "Time (Seconds)", "Codecs", "h264 vs h265 compression time in lossless compression (Seconds)", "TIMES_X264_V_X265_LOSSLESS.svg")

filesizes_x264_lossless = get_from_codec("libx264", filesizes_lossless)
filesizes_x265_lossless = get_from_codec("libx265", filesizes_lossless)

filesizes_values_lossless = np.array([np.sum(filesizes_x264_lossless), np.sum(filesizes_x265_lossless)])
filesizes_values_lossless = np.round(filesizes_values_lossless/(1024*1024), decimals=ROUNDING)

make_bar_graph(filesizes_values_lossless, VIDEO_CODECS, "Size (Mb)", "Codecs", "h264 vs h265 compressed file size in lossless compression (Mb)", "FILESIZES_X264_V_X265_LOSSLESS.svg")
