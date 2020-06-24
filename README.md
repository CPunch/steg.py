## Steg.py

This small python script will encode files in PNG images (or any other losslessly compressed image format.) 

An example output looks something like:

![demo result](encoded_cutestcat.png)

## Installation

This script reqiures pillow and argparse, both of which can be installed from pypi using
```bash
pip install pillow argparse
```

## Example usage

You can encode a file in an image by first passing the image you want the end result to look like, followed by the -e option and the file you want to encode. You can also specify the output path with -o
```bash
steg.py testData/cutestcat.png -e testData/test.png -o encoded.png
```

You can also decode from an encoded image by just passing the encoded image to the file, then specifying an output path with -o
```bash
steg.py encoded -o out
```
