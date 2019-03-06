#! python
'''
This demo extracts and saves first image of the first page of an imagebased PDF.

If an image has no /SMask entry, it is stored using the raw image buffer -
i.e. not necessarily as a PNG file.
If the image has an /SMask entry, it is processed using PyMuPDF pixmaps.

The image is stored in the PDF's directory and named "p<i>-<j>.ext",

Usage:
------
python extract_img3.py <input.pdf>

'''
from __future__ import print_function
import fitz
import sys

def recoverpix(doc, item):
    x = item[0]  # xref of PDF image
    s = item[1]  # xref of its /SMask
    if s == 0:  # no /SMask: use raw image
        return doc.extractImage(x)

    pix1 = fitz.Pixmap(doc, x)
    pix2 = fitz.Pixmap(doc, s)  # create pixmap of /SMask entry
    # check that we are safe
    if not (pix1.irect == pix2.irect and \
            pix1.alpha == pix2.alpha == 0 and \
            pix2.n == 1):
        print("pix1", pix1, "pix2", pix2)
        raise ValueError("unexpected situation")
    pix = fitz.Pixmap(pix1)  # copy of pix1, alpha channel added
    pix.setAlpha(pix2.samples) # treat pix2.samples as alpha value
    pix1 = pix2 = None  # free temp pixmaps
    return pix

assert len(sys.argv) == 2, 'Usage: %s <input file>' % sys.argv[0]
doc = fitz.open(sys.argv[1])  # the PDF
assert doc.isPDF, "This script can only process PDF documents."
lenXREF = doc._getXrefLength()  # only used for information

# display some file info
print("file: %s, pages: %s, objects: %s" % (sys.argv[1], len(doc), lenXREF-1))

imglist = doc.getPageImageList(0)  # list of images used by the first page
img = imglist[0]  # first image on first page
pix = recoverpix(doc, img[:2]) # make pixmap from image
# imgfile = "p%i-%i" % (0, img[0])
imgfile = "p%i-%i" % (0, img[0])

if type(pix) is not fitz.Pixmap:  # a raw image buffer
    fout = open(imgfile + "." + pix["ext"], "wb")
    fout.write(pix["image"])
    fout.close()
else:
    if pix.n - pix.alpha < 4:  # can be saved as PNG
        pass
    else:  # must convert CMYK first
        pix0 = fitz.Pixmap(fitz.csRGB, pix)
        pix = pix0
    pix.writePNG(imgfile + ".png")

print("extracted image")