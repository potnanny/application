import os
import re
import argparse
import glob

def main():
    files = input_files(args.input)
    for f in files:
        minify_file(f, args.output)

def input_files(path):
    results = glob.glob(f"{path}/*.js")
    return results

def minify_file(path, output_path):
    name = os.path.basename(path)
    min_name = re.sub(r'.js', '.min.js', name)
    with open(path, 'r') as h:
        raw = h.read()

    minified = re.sub(r'\s+', ' ', raw)
    output = os.path.join(args.output, min_name)
    with open(output, 'w') as fh:
        fh.write(minified)
    print(f"{output} minified")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a VERY basic minifier. Read all *.js files from an input directort, minify them and write to output directory as *.min.js')
    parser.add_argument('--input', '-i',
        default="../potnanny/api/static/js",
        help='input directory')
    parser.add_argument('--output', '-o',
        default="../potnanny/api/static/js/min",
        help='output directory')

    args = parser.parse_args()
    args.input = os.path.abspath(args.input)
    args.output = os.path.abspath(args.output)

    main()
