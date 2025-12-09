<p align="center">
  <img src="https://img.shields.io/badge/python-v3-brightgreen.svg?style=flat-square" alt="python" />
  <img src="https://img.shields.io/badge/tensorflow-v1-orange.svg?style=flat-square" alt="tensorflow" />
  <a href="https://github.com/Vets-Who-Code/vwc-site/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg?style=flat-square" alt="License: MIT" />
  </a>
</p>

> [!WARNING]
> This project was part of my master's thesis and is no longer being developed. Feel free to fork, of course.

# LabelboxToTFRecord
This repo contains some tools around working with data from the [Labelbox](https://labelbox.com/) platform, as well as creating and shaping [TFRecord](https://www.tensorflow.org/tutorials/load_data/tfrecord#tfrecords_format_details) files (a binary file format for machine learning training data) for use with TensorFlow. It can:

* Download data from Labelbox containing images and labels
* Convert downloaded Labelbox data into a .tfrecord file
* Perform operations on one or more .tfrecord files such as splitting, merging, shuffling, and listing information

## Installation

Installation may be done directly on a machine, via raw Docker, or via a VS Code container image.

### Direct Python Installation:

This method supports Tensorflow 2. Use of a pip-compatible virtual environment is encouraged.

1. Install TensorFlow's Object Detection API following the directions [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md). Choose the Python package method. The Docker instructions here have not been tested with this repo.
2. Clone this repo:
```
git clone git@github.com:xdhmoore/LabelboxToTFRecord.git
cd LabelboxToTFRecord
```
3. Run the following:

`python3 -m pip install -r requirements.txt`

4. To use, see the usage info for the `convert.py` script below.

### Docker Installation:
Unfortunately, this installation method does not support Tensorflow 2 yet.

1. Clone the repo:
```
git clone git@github.com:xdhmoore/LabelboxToTFRecord.git
cd LabelboxToTFRecord
```
2. Create a src/config.yaml file based on [src/config.yaml.sample](https://github.com/xdhmoore/LabelboxToTFRecord/blob/master/src/config.yaml.sample). Use the api key and project id found in Labelbox.
3. Build with docker:
```
# From project root
docker build -t lb2tf .
mkdir data
```
4. Run the following from the project root to download the data from Labelbox and convert it to 2 .tfrecord files via a 20%/80% split. See the Usage info and Examples below for more info:
```
# This will run convert.py, downloading the data to a ./data folder
docker run --mount "type=bind,src=${PWD}/data,dst=/data" lb2tf --split 80 20 --download --labelbox-dest /data/labelbox --tfrecord-dest /data/tfrecord
```
Change the mount src to change where the data is downloaded to.

> [!CAUTION]
> If you have downloaded a large amount of data in your project, when `docker build` runs it will copy the data as part of the context which may take a long time. To avoid this, either move downloaded data outside of the project folder before doing a build, use mount settings to save the data outside the project folder to begin with, or use a dockerignore file to ignore the data once downloaded.

> [!TIP]
> If you encounter permissions denied errors, check to see that docker hasn't created the `data` directory as root. `chown` or recreate the directory yourself to fix.

### Dev Container Installation
This method is experimental and may have some issues. As it depends on the "raw docker" method, it also is only setup for Tensorflow 1 currently.

1. Clone the repo, then open VS Code in that folder
```
git clone git@github.com:xdhmoore/LabelboxToTFRecord.git
cd LabelboxToTFRecord
code .
```
2. Click "Trust" the author and then click the "Reopen in Container" button in the bottom right. If this doesn't show up, try selecting "Rebuild and Reopen in Container" from the Command Palette (Ctrl+Shift+P).

> [!CAUTION]
> See the Caution above about building the docker image when it copies a large amount of dowloaded data. When you open VS Code, it will run a docker build.

3. See the usage info around the convert.py script below.

## Usage:

The individual script usages are found below. You will want to start with `convert.py` as it is the script that actually downloads from Labelbox and converts the data to .tfrecords. The rest of the scripts perform manipulations around existing .tfrecord files.

#### convert.py

    usage: convert.py [-h] [--puid PUID] [--api-key API_KEY]
                  [--labelbox-dest LABELBOX_DEST]
                  [--tfrecord-dest TFRECORD_DEST]
                  [--splits SPLITS [SPLITS ...]] [--download]

    Convert Labelbox data to TFRecord and store .tfrecord file(s) locally. Saving
    images to disk is optional. Create a file "config.yaml" in the current
    directory to store Labelbox sensitive data, see "config.yaml.sample" for an
    example.

    optional arguments:
      -h, --help            show this help message and exit
      --puid PUID           Project Unique ID (PUID) of your Labelbox project,
                        found in URL of Labelbox project home page
      --api-key API_KEY     API key associated with your Labelbox account
      --labelbox-dest LABELBOX_DEST
                        Destination folder for downloaded images and json file
                        of Labelbox labels.
      --tfrecord-dest TFRECORD_DEST
                        Destination folder for downloaded images
      --limit LIMIT         Only retrieve and convert the first LIMIT data items
      --splits SPLITS [SPLITS ...]
                        Space-separated list of integer percentages for
                        splitting the output into multiple TFRecord files
                        instead of one. Sum of values should be <=100.
                        Example: '--splits 10 70' will write 3 files with 10%,
                        70%, and 20% of the data, respectively
      --download            Save the images locally in addition to creating
                        TFRecord(s)

#### split.py

    usage: split.py [-h] infile splits [splits ...]

    Split a .tfrecord file into smaller files

    positional arguments:
      infile      the .tfrecord file to split
      splits      Space-separated list of integers, the number of records to put
                  in each output file. Should add up to the total number of
                  records in the input tfrecord file.

    optional arguments:
      -h, --help  show this help message and exit

#### shuffle.py

    usage: shuffle.py [-h] tfrfile randfile

    Shuffle a .tfrecord file using a random numbers file

    positional arguments:
      tfrfile     the .tfrecord file to shuffle
      randfile    A file containing a shuffled sequence of newline-separated
                  numbers from 0 to N-1, where N is the number of records in the
                  .tfrecord file.

    optional arguments:
      -h, --help  show this help message and exit

#### join.py

    usage: join.py [-h] outfile infiles [infiles ...]

    Combine several .tfrecord files into a new one

    positional arguments:
      outfile     the name of the output file
      infiles     files to be combined

    optional arguments:
      -h, --help  show this help message and exit


#### count.py

    usage: count.py [-h] [--total | --categories] infiles [infiles ...]

    Display the number of records in each file

    positional arguments:
      infiles           files with records to be counted

    optional arguments:
      -h, --help        show this help message and exit
      --total, -t       instead of the the total for each file, display the sum
                        total across all files
      --categories, -c  display the number of labels of each category for each
                        file


## Tests

To run the tests:

```
cd src
python -m unittest
```


## Examples

* Example 1 - Download Labelbox images and convert labels to TFRecord format:

`python convert.py PUID API_KEY`<br>

This will download all Labelbox data (images, label file) to ./labelbox, will output tfrecord file to tfrecord/<PUID>.tfrecord
  
* Example 2 - If you have a config.yaml file specified in the current directory, you can grab and convert the Labelbox data with a simple:

`python convert.py`<br>

See [src/config.yaml.sample](https://github.com/xdhmoore/LabelboxToTFRecord/blob/master/src/config.yaml.sample) for an example config file.

* Example 3 - To split data into two groups, with 30% in the first and 70% in the second...

`python convert.py --split 30 70`<br>

This is useful for setting up data sets for cross-validation

* Example 4 - To split data into two groups, with 30% in the first and 70% in the second, while downloading images locally...

`python convert.py --download --split 30 70`<br>

* Example 5 - You can also split an existing .tfrecord file into smaller pieces with split.py:

`python split.py ./10_record_file.tfrecord 3 2 5`<br>

This will write 3 new files containing 3, 2, and 5 records, respectively.

* Example 6 - To copy a .tfrecord file into a new file, shuffling the records according to a provided random_ints.txt
file:

`python shuffle.py ./10_record_file.tfrecord random_seq.txt`<br>

`random_seq.txt` should be a file of all the indices into the tfrecord file,
[0,N), where N is the number of records in the tfrecord file, each index
occurs exactly once, and there is one index per line. This allows you to
shuffle the tfrecord file using random data like from random.org.

* Example 7 - To copy several `.tfrecord` files into a new combined file:

`python join.py outfile.tfrecord infile1.tfrecord infile2.tfrecord infile3.tfrecord`<br>

* Example 8 - To display the number of records in each of files `pets_train.tfrecord` and `pets_val.tfrecord`...

`python count.py pets_train.tfrecord pets_val.tfrecord`<br>

* Example 9 - To display a table of the number of records in each category (shark, dolphin, etc.) in all files with "train" in the name...

`python count.py -c *train*.tfrecord`

The above prints something like:
```
2021-03-04 00:21:34.523331: I tensorflow/core/platform/cpu_feature_guard.cc:142] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
2021-03-04 00:21:34.531411: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 1992000000 Hz
2021-03-04 00:21:34.532907: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x42a1fd0 initialized for platform Host (this does not guarantee that XLA will be used). Devices:
2021-03-04 00:21:34.532962: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): Host, Default Version
filename                               total    sealion    person    dolphin    shark    boat
-----------------------------------  -------  ---------  --------  ---------  -------  ------
2021-01-26_cv_a_train_2824.tfrecord     2824          0      3078        712     2512     165
2021-01-26_cv_b_train_2824.tfrecord     2824          1      3188        689     2472     173
2021-01-26_cv_c_train_2824.tfrecord     2824          1      3201        686     2493     173
2021-01-26_cv_d_train_2824.tfrecord     2824          1      2977        729     2488     176
2021-01-26_cv_e_train_2824.tfrecord     2824          1      3132        680     2491     173
```

## Contributing
This project was part of my master's thesis and is no longer being developed.

## License
This project is under an [MIT license](/LICENSE).
