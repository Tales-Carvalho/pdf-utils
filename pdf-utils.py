import PyPDF2
import os
from PIL import Image


def merge(inputFilenames):

    pdfOutputFile = open(os.path.join("output", "MergedFiles.pdf"), "wb")
    pdfWriter = PyPDF2.PdfFileWriter()

    for filename in inputFilenames:
        with open(os.path.join("input", filename), "rb") as inputFile:
            pdfReader = PyPDF2.PdfFileReader(inputFile)
            for pageNum in range(pdfReader.getNumPages()):
                pdfWriter.addPage(pdfReader.getPage(pageNum))
            pdfWriter.write(pdfOutputFile)
            inputFile.close()
    
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
        if '/XObject' in page['/Resources']:
            xObjects.append(page['/Resources']['/XObject'].getObject())

    for xObject in xObjects:
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].getData()

                if '/Filter' in xObject[obj]:
                    if xObject[obj]['/Filter'] == '/DCTDecode' or '/DCTDecode' in xObject[obj]['/Filter']:
                        img = open(os.path.join("output", obj[1:] + ".jpg"), "wb")
                        img.write(data)
                        img.close()
                        print("Saved file: " + os.path.join("output", obj[1:] + ".jpg"))
                    elif xObject[obj]['/Filter'] == '/FlateDecode' or '/FlateDecode' in xObject[obj]['/Filter']:
                        if '/ColorSpace' not in xObject[obj]:
                            mode = None
                        elif xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                            mode = "RGB"
                        elif xObject[obj]['/ColorSpace'] == '/DeviceCMYK':
                            mode = "CMYK"
                        elif xObject[obj]['/ColorSpace'] == '/DeviceGray':
                            mode = "P"
                        else:
                            if type(xObject[obj]['/ColorSpace']) == PyPDF2.generic.ArrayObject:
                                if xObject[obj]['/ColorSpace'][0] == '/ICCBased':
                                    colorMap = xObject[obj]['/ColorSpace'][1].getObject()['/N']
                                    if colorMap == 1:
                                        mode = "P"
                                    elif colorMap == 3:
                                        mode = "RGB"
                                    elif colorMap == 4:
                                        mode = "CMYK"
                                    else:
                                        mode = None
                                else:
                                    mode = None
                            else:
                                mode = None
                        if mode != None:
                            img = Image.frombytes(mode, size, data)
                            if mode == "CMYK":
                                img = img.convert("RGB")
                            img.save(os.path.join("output", obj[1:] + ".png"))
                            print("Saved file: " + os.path.join("output", obj[1:] + ".png"))
                        else:
                            print("Color map nor supported for Image " + str(obj[1:]))
                    elif xObject[obj]['/Filter'] == '/JPXDecode':
                        img = open(os.path.join("output", obj[1:] + ".jp2"), "wb")
                        img.write(data)
                        img.close()
                        print("Saved file: " + os.path.join("output", obj[1:] + ".jp2"))
                    elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                        img = open(os.path.join("output", obj[1:] + ".tiff"), "wb")
                        img.write(data)
                        img.close()
                        print("Saved file: " + os.path.join("output", obj[1:] + ".tiff"))
                else:
                    img = Image.frombytes(mode, size, data)
                    img.save(os.path.join("output", obj[1:] + ".png"))
                    print("Saved file: " + os.path.join("output", obj[1:] + ".png"))


def extractText(inputFilename):
    
    inputFile = open(os.path.join("input", inputFilename), "rb")
    pdfReader = PyPDF2.PdfFileReader(inputFile)

    pages = []
    for i in range(pdfReader.getNumPages()):
        pages.append(pdfReader.getPage(i))

    for i, page in enumerate(pages):
        textContent = page.extractText()
        with open(os.path.join("output", f"{inputFilename}_page_{i}.txt"), "w") as outputFile:
            outputFile.write(textContent)
            outputFile.close()

if __name__ == '__main__':
    print("TODO")
    # TODO: interface for PDF usage

