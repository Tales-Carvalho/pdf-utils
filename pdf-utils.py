import PyPDF2
import os
from PIL import Image


def merge(inputFilenames):

    pdfWriter = PyPDF2.PdfFileWriter()

    for filename in inputFilenames:
        with open(os.path.join("input", filename), "rb") as inputFile:
            pdfReader = PyPDF2.PdfFileReader(inputFile)
            for pageNum in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(pageNum)
                pdfWriter.addPage(pageObj)
            inputFile.close()
    
    with open(os.path.join("output", "MergedFiles.pdf"), "wb") as pdfOutputFile:
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()

    return 0


def split(inputFilename, pageToSplit):

    inputFile = open(os.path.join("input", inputFilename), "rb")
    pdfReader = PyPDF2.PdfFileReader(inputFile)

    lastPage = pdfReader.getNumPages()

    if pageToSplit >= lastPage:
        print(f"Error: Invalid page number ({pageToSplit}) for {inputFilename}.")
        return -1

    pdfWriter = PyPDF2.PdfFileWriter()
    for page in range(pageToSplit):
        pdfWriter.addPage(pdfReader.getPage(page))
    with open(os.path.join("output", f"1-{pageToSplit}_{inputFilename}"), "wb") as pdfOutputFile:
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()
    
    pdfWriter = PyPDF2.PdfFileWriter()
    for page in range(pageToSplit, lastPage):
        pdfWriter.addPage(pdfReader.getPage(page))
    with open(os.path.join("output", f"{pageToSplit+1}-{lastPage}_{inputFilename}"), "wb") as pdfOutputFile:
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()

    return 0


def extractImages(inputFilename):

    inputFile = open(os.path.join("input", inputFilename), "rb")
    pdfReader = PyPDF2.PdfFileReader(inputFile)

    pages = []
    for i in range(pdfReader.getNumPages()):
        pages.append(pdfReader.getPage(i))

    xObjects = []
    for page in pages:
        xObjects.append(page['/Resources']['/XObject'].getObject())

    for xObject in xObjects:
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].getData()
                if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                    mode = "RGB"
                else:
                    mode = "P"

                if xObject[obj]['/Filter'] == '/FlateDecode':
                    img = Image.frombytes(mode, size, data)
                    img.save(os.path.join("output", obj[1:] + ".png"))
                    print("Saved file: " + os.path.join("output", obj[1:] + ".png"))
                elif xObject[obj]['/Filter'] == '/DCTDecode' or '/DCTDecode' in xObject[obj]['/Filter']:
                    img = open(os.path.join("output", obj[1:] + ".jpg"), "wb")
                    img.write(data)
                    img.close()
                    print("Saved file: " + os.path.join("output", obj[1:] + ".jpg"))
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    img = open(os.path.join("output", obj[1:] + ".jp2"), "wb")
                    img.write(data)
                    img.close()
                    print("Saved file: " + os.path.join("output", obj[1:] + ".jp2"))


def extractText(inputFilename):
    print("TODO")
    # TODO: create method

if __name__ == '__main__':
    print("TODO")
    # TODO: interface for PDF usage

