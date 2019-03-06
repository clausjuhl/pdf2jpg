#! python
'''
This script extracts and saves first image of the first page of an imagebased PDF.

If an image has no /SMask entry, it is stored using the raw image buffer -
i.e. not necessarily as a PNG file.
If the image has an /SMask entry, it is processed using PyMuPDF pixmaps.
'''
from __future__ import print_function
import fitz
import sys
import csv
from pathlib import Path


CSVFILE = Path(r"C:\Workflows\workflow_lib_binary\csv-files\PR_8_deployed.csv")
ARCHIVE_FOLDER = Path(r"M:\Borgerservice-Biblioteker\Stadsarkivet\_DIGITALT ARKIV\ark_binary_access\access")
IMAGES_FOLDER = r"M:\Borgerservice-Biblioteker\Stadsarkivet\Projekter\Preben Rasmussens samling\images"
PORTRAITS_FOLDER = r"M:\Borgerservice-Biblioteker\Stadsarkivet\Projekter\Preben Rasmussens samling\portraits"
THUMBS_FOLDER = r"M:\Borgerservice-Biblioteker\Stadsarkivet\Projekter\Preben Rasmussens samling\thumbs"


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

def main():
    log = []

    with open(CSVFILE) as pr:
        reader = csv.DictReader(pr)
        ids = [_d.get("uniqueID") + "_c.pdf" for _d in reader]

    arc_ids = [i.name for i in ARCHIVE_FOLDER.iterdir()]

    for _id in ids:
        if _id not in arc_ids:
            log.append(_id + " not in _digital_arkiv")
            continue

        doc = fitz.open(str(Path(ARCHIVE_FOLDER, _id)))  # the PDF
        assert doc.isPDF, "This script can only process PDF documents."

        imglist = doc.getPageImageList(0)  # list of images used by the first page
        img = imglist[0]  # first image on first page
        pix = recoverpix(doc, img[:2]) # make pixmap from image
        # imgfile = "p%i-%i" % (0, img[0])
        imgfile = _id.replace("_c.pdf", "_m")

        if type(pix) is not fitz.Pixmap:  # a raw image buffer
            fout = open(str(Path(IMAGES_FOLDER, imgfile + "." + pix["ext"])), "wb")
            fout.write(pix["image"])
            fout.close()
        else:
            if pix.n - pix.alpha < 4:  # can be saved as PNG
                pass
            else:  # must convert CMYK first
                pix0 = fitz.Pixmap(fitz.csRGB, pix)
                pix = pix0
            pix.writePNG(str(Path(IMAGES_FOLDER, imgfile + ".png")))
        print(imgfile + " converted")
    if log:
        [print(f) for f in log]
    else:
        print("no errors")

if __name__ == '__main__':
    main()
