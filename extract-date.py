#!/usr/bin/env python3

import argparse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_date(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()

            if exif_data is not None:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "DateTimeOriginal":
                        return value
    except Exception as e:
        print(f"Error: {e}")

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', action='store', type=str, default=None, help='Filename to process.')
    args = parser.parse_args()
    image_path = args.filename
    date = get_exif_date(image_path)

    if date is not None:
        print(f"Date from EXIF data: {date}")
    else:
        print("Date not found in EXIF data.")

