##### This is an assignment for the Video Coding class in our university (University of Thessally)

We are tasked on evaluating vvenc's performance based on a different number of threads and a 
few settings (mainly whether we use 2x2 row x column tiles and whether WaveFront synchronization is on or off). **These are scripts that help generate data for an easier analysis of the codec.**

**Not an analysis** (_should have changed the title..._)

Feel free to contribute anything after the deadline has passed (1st of March 2024).

This is a joint effort by Dimosthenis Krallis (`wallmenis`) and David Parathyras (`h1dd3n3y3`).


- - -
###### How to use:

First off, find a .yuv video...

This is very important since it is lossless data that we compare. We are encoding, not decoding : )

Then place it in the `SourceVideo` directory. The scripts will detect it and spew the data in the `Data` directory... Speaking of scripts...

We have 3 shell executables and 2 python scripts.

The python scripts use plain old `matplotlib` and `numpy`

The shell scripts are there to install a virtual environment and automatically run the corresponding script.

For example, `run_generate_in_virtual_environment.sh` will run the `Generate.py` script ect.

The `run_all_at_once.sh` script runs... all at once...

Well actually it just runs the scripts with the right order. First the `Generate.py` script to generate the logs and conversions of the source video and then the `Analysis.py` script.

With that in mind, the right way of running these scripts is:

``run_generate_in_virtual_environment.sh -> run_analysis_in_virtual_environment.sh`` _or you could run_ `run_all_at_once.sh`

If you attempt on running this outside of a virtual environment, please run in this order:

``Generate.py -> Analysis.py``

You may find sample analysis data in `Data/sample_data`. It does't contain any video data though in case of any copyright violation...
