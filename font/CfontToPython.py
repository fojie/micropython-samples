#! /usr/bin/python3

# Convert a font C source file to Python source.

# Copyright Peter Hinch 2016
# Released under the MIT licence
# Files created by GLCD Font Creator http://www.mikroe.com/glcd-font-creator/
# The code attempts two ways of deducing font height and width in pixels.
# Files produced by the GLCD Font Creator have a '//GLCD FontSize'  comment line which species these.
# This is used if it exists. However some files on the website lack this and have an initial record
# written into the data: this is used if necessary.

# Usage:
# ./CfontToPython -i Arial16x16.c -o arial16x16.py
import argparse
chars_processed = 0
horiz, vert = 0, 0

def process(infile, outfile, sourcefile):
    global chars_processed, horiz, vert
    phase = 0
    header_done = False
    for line in infile:
        if phase == 0:
            start = line.find('//GLCD FontSize')
            if start >= 0:                          # Found the font size: parse line
                start = line.find(':')
                line = line[start +1:]
                operator = line.find('x')
                if operator > 0 :
                    horiz = int(line[ : operator])
                    vert = int(line[operator +1 :])
                    print('Header found')
                    outfile.write('# Code generated by CfontToPython.py\n')
                    outfile.write('import pyfont\n')
                    outfile.write("_font = b'")
                    header_done = True
                    phase = 1
            elif line.find('{') >= 0:
                phase = 1
        if phase == 1:                           # Skip to 1st data after '{'
            start = line.find('{')
            if start >= 0:
                line = line[start +1:]
                phase = 2
        if phase == 2:
            if not (line == '' or line.isspace()):
                comment = line.find('//')
                if comment > 0 :
                    line = line[:comment]
                hexnums = line.split(',')
                if header_done:              # Ignore manually entered header data
                    if len(hexnums) > 5:
                        phase = 3               # Real font data will have many more fields per line
                else:
                    if len(hexnums) <= 5:
                        nums = [x for x in hexnums if not x.isspace()]
                        h = nums[1]
                        v = nums[2]
                        horiz, vert = int(h, 16), int(v, 16)
                        print('Header found')
                        outfile.write('import pyfont\n')
                        outfile.write("_font = b'")
                        header_done = True
                    else:
                        break                   # No header data
        if phase == 3:                          # Process data until '}'
            end = line.find('}')
            if end > 0 :
                line = line[:end]
                phase = 4
            comment = line.find('//')
            if comment > 0 :
                line = line[:comment]
            hexnums = line.split(',')
            if hexnums[0] != '':
                for hexnum in [x for x in hexnums if not x.isspace()]:
                    outfile.write('\\')
                    outfile.write(hexnum.strip()[1:5])
                chars_processed += 1
            outfile.write("\\\n")
    if phase == 4 :
        outfile.write("'\n")
        outfile.write('font = pyfont.PyFont(_font, {}, {}, {})'.format(vert, horiz, chars_processed))
        outfile.write('\n\n')
        print("Characters in font = ", chars_processed)
    else:
        print(''.join(("File: '", sourcefile, "' is not a valid C font file")))

def load_c(sourcefile, destfile):
    try:
        with open(sourcefile, 'r') as f:
            with open(destfile, 'w') as outfile:
                process(f, outfile, sourcefile)
    except OSError as err:
        print(err)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__, description="Convert C font generated by GLCD font creator to Python.\nSample usage:\n ./CfontToPython -i Arial16x16.c -o arial16x16.py")
    parser.add_argument("--outfile", "-o", help="Path and name of output file", required=True)
    parser.add_argument("--infile", "-i", help="Path and name of C font file", required=True)
    args = parser.parse_args()
    load_c(args.infile, args.outfile)
