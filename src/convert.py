"""
Usage:
  # From tensorflow/models/
  # Create train data:
  python generate_tfrecord.py --csv_input=data/train_labels.csv  --output_path=train.record
  # Create test data:
  python generate_tfrecord.py --csv_input=data/test_labels.csv  --output_path=test.record


img_obj is of format
{
    'filename': the_file,
    'width': width,
    'height': height,
    'class': class, 
    'xmin': xmin, 
    'ymin': ymin, 
    'xmax': xmax, 
    'ymax': ymax
}
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import sys
import pandas as pd
import tensorflow as tf
import glob
import xml.etree.ElementTree as ET
import parse_labelbox
import argparse
from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict


def create_tf_example(record_obj, data):
    # with tf.io.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
    #     encoded_jpg = fid.read()
    # encoded_jpg_io = io.BytesIO(encoded_jpg)
    # image = Image.open(encoded_jpg_io)
    # width, height = image.size

    class_dict = parse_labelbox.get_classes_from_labelbox(data)

    #filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for label_obj in record_obj.labels:
        xmins.append(label_obj.xmin / record_obj.width)
        xmaxs.append(label_obj.xmax / record_obj.width)
        ymins.append(label_obj.ymin / record_obj.height)
        ymaxs.append(label_obj.ymax / record_obj.height)
        classes_text.append(label_obj.label.encode('utf8'))
        classes.append(class_dict[label_obj.label])

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(record_obj.height),
        'image/width': dataset_util.int64_feature(record_obj.width),
        'image/filename': dataset_util.bytes_feature(record_obj.filename),
        'image/source_id': dataset_util.bytes_feature(record_obj.filename),
        'image/encoded': dataset_util.bytes_feature(record_obj.encoded),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Labelbox data, and optionally convert to TFRecord format.')
    parser.add_argument('PUID', help="Project Unique ID (PUID) of your Labelbox project, found in URL of Labelbox project home page")
    parser.add_argument('API_KEY', help="API key associated with your Labelbox account")
    parser.add_argument('--dest', help="Destination folder for downloaded images", default="images")
    parser.add_argument('--download-only', help="Use this flag if you only want to download the images and not convert to TFRecord format.", action='store_true')
    args = parser.parse_args()
    print(args)

    if args.download_only:
        parse_labelbox.parse_labelbox_data(args.PUID, args.API_KEY, args.dest)
    else:
        data, records = parse_labelbox.parse_labelbox_data(args.PUID, args.API_KEY, args.dest)
        ret = create_tf_example(records[0], data)
        print(ret)
        print(type(ret))

    


