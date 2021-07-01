
import argparse
import os
from typing import List, Dict, Set, Any
from tabulate import tabulate

import tensorflow.compat.v1 as tf
tf.enable_eager_execution()

def parse_fn(example_proto): #type: ignore
    return tf.io.parse_single_example( #type: ignore
        serialized=example_proto,
        features={
            'image/object/class/text': tf.io.VarLenFeature(tf.string), #type: ignore

            # TODO assuming VarLen but could be fixed len?
            'image/object/bbox/xmin': tf.io.VarLenFeature(tf.float32), #type: ignore
            'image/object/bbox/xmax': tf.io.VarLenFeature(tf.float32), #type: ignore
            'image/object/bbox/ymin': tf.io.VarLenFeature(tf.float32), #type: ignore
            'image/object/bbox/ymax': tf.io.VarLenFeature(tf.float32), #type: ignore

            'image/width': tf.io.VarLenFeature(tf.int64), #type: ignore
            'image/height': tf.io.VarLenFeature(tf.int64) #type: ignore
        }
    ) # type: ignore

def count(infilenames: List[str], displaytotal: bool=False, displaycategories: bool=False,
        displaySizes: bool=False) -> None:

    def in_range(range, size):
        return range[0] < size and size < range[1]

    # Size categories from cocoeval.py
    small_area = (-1, 32 ** 2)
    med_area = (32 ** 2, 96 ** 2)
    large_area = (96 ** 2, 10000 ** 2)

    small_count: int = 0
    med_count: int = 0
    large_count: int = 0

    all_categories: Set[str] = set()
    total_cat_counts: Dict[str, int] = {}
    all_file_counts: List[Dict[str, int]] = []
    total: int = 0
    subtotals: List[int] = []
    for infilename in infilenames:
        indataset = tf.data.TFRecordDataset(infilename).map(parse_fn) # type: ignore

        file_cat_counts: Dict[str,int] = {}

        for row in indataset: # type: ignore
            image_cat_counts: Dict[str,int] = {}
            image_categories: List[str] = [c.decode("UTF-8") for c in tf.sparse.to_dense(row['image/object/class/text']).numpy()] #type: ignore

            image_height: int = tf.sparse.to_dense(row['image/height']).numpy() #type: ignore
            image_width: int = tf.sparse.to_dense(row['image/width']).numpy() #type: ignore

            #obj_dimensions = \
            #    zip(
            # TODO hardcoded * 300 to get pixel values from what seems to be [0,1]. 300 is what my pipeline
            # is currently set to

            # TODO  this seems to be missing labels, based on what's in labelbox
            objects = [o for o in zip(*[tf.sparse.to_dense(row[key]).numpy() for key in [
                'image/object/bbox/xmin',
                'image/object/bbox/xmax',
                'image/object/bbox/ymin',
                'image/object/bbox/ymax'
            ]])]

            # (xmax - xmin) * (ymax - ymin)
            object_sizes = [
                image_width * (o[1] - o[0]) * image_height * (o[3] - o[2])
                for o in objects]

            if displaySizes:
                for size in object_sizes:
                    #if (size > 300 ** 2):
                    #    print(f"Size is larger than expected: {size}")
                    #    return
                    if in_range(small_area, size):
                        small_count += 1
                    elif in_range(med_area, size):
                        med_count += 1
                    elif in_range(large_area, size):
                        large_count += 1
                    else:
                        print(f"Warning, object size {size} does not fit in size category")



            # Count up all the categories for the image
            for cat in image_categories:
                all_categories.add(cat)
                if image_cat_counts.get(cat) == None:
                    image_cat_counts[cat] = 0
                image_cat_counts[cat] += 1


            # Count up all the categories for the file
            for cat, image_cat_count in image_cat_counts.items():
                if file_cat_counts.get(cat) == None:
                    file_cat_counts[cat] = 0
                file_cat_counts[cat] += image_cat_count

        all_file_counts += [file_cat_counts]

        for cat, file_cat_count in file_cat_counts.items():
            if total_cat_counts.get(cat) == None:
                total_cat_counts[cat] = 0
            total_cat_counts[cat] += file_cat_count

        subtotals += [len([r for r in indataset])] # type: ignore
        total+=subtotals[-1]

    if displaytotal:
        print(total)

    elif displaySizes:
        # TODO use tabulate
        print(f"small: {small_count}")
        print(f"medium: {med_count}")
        print(f"large: {large_count}")

    elif displaycategories:
        table: Dict[str,List[Any]] = { 
            'filename': [os.path.basename(f) for f in infilenames],
            'total': subtotals
        }
        table = {**table, **{cat:[] for cat in all_categories}}
        for file_cat_counts in all_file_counts:
            for cat in all_categories:
                if file_cat_counts.get(cat) == None:
                    table[cat] += [0]
                else:
                    table[cat] += [file_cat_counts.get(cat)]

        print(tabulate(table, headers="keys"))

    else:
        for subtotal in subtotals:
            print(subtotal)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display the number of records in each file')
    parser.add_argument('infiles', metavar='infiles', type=str, nargs='+', help='files with records to be counted')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--total', '-t', action="store_true", help='instead of the the total for each file, display the sum total across all files')
    group.add_argument('--categories', '-c', action="store_true", help='display the number of labels of each category for each file')
    group.add_argument('--sizes', '-s', action="store_true", help='''
        display the number of labels of each COCO size for each file. The COCO metric sizes are: small: area < 32^2 pixels,
        medium: 32^2 < area < 96^2 pixels, large: 96^2 < area < 10000^2 pixels
    ''')

    # TODO Create a histogram of the # of labels of a given category per image across all files?
    # OR use the output of the -c flag to input to another tool
    #group.add_argument('--cat-hist', '-C',  type=str, nargs=1, help='create histogram of the number of labels per image for a given category')

    args = parser.parse_args()
    count(args.infiles, args.total, args.categories, args.sizes)