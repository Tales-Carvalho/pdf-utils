import PyPDF2
import os
import glob
from PIL import Image


def merge(inputFilenames, outputFilename):

    pdfOutputFile = open(os.path.join("output", outputFilename), "wb")
    pdfWriter = PyPDF2.PdfFileWriter()

    for filename in inputFilenames:
        with open(os.path.join("input", filename), "rb") as inputFile:
            pdfReader = PyPDF2.PdfFileReader(inputFile)
            for pageNum in range(pdfReader.getNumPages()):
                pdfWriter.addPage(pdfReader.getPage(pageNum))
            pdfWriter.write(pdfOutputFile)
            inputFile.close()
    
    pdfOutputFile.close()

    return True


def split(inputFilename, pageToSplit):

    inputFile = open(os.path.join("input", inputFilename), "rb")
    pdfReader = PyPDF2.PdfFileReader(inputFile)

    lastPage = pdfReader.getNumPages()

    if pageToSplit >= lastPage:
        print(f"Error: Invalid page number ({pageToSplit}) for {inputFilename}.")
        return False

    pdfWriter = PyPDF2.PdfFileWriter()
    for page in range(pageToSplit):
        pdfWriter.addPage(pdfReader.getPage(page))
    with open(os.path.join("output", f"1-{pageToSplit}_{inputFilename}"), "wb") as pdfOutputFile:
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()
    
    pdfReader = PyPDF2.PdfFileReader(inputFile) # Bypasses a file stream bug of PyPDF2
    pdfWriter = PyPDF2.PdfFileWriter()
    for page in range(pageToSplit, lastPage):
        pdfWriter.addPage(pdfReader.getPage(page))
    with open(os.path.join("output", f"{pageToSplit+1}-{lastPage}_{inputFilename}"), "wb") as pdfOutputFile:
        pdfWriter.write(pdfOutputFile)
        pdfOutputFile.close()

    return True


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
                        return True
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
                            return True
                        else:
                            print("Color map nor supported for Image " + str(obj[1:]))
                            return False
                    elif xObject[obj]['/Filter'] == '/JPXDecode':
                        img = open(os.path.join("output", obj[1:] + ".jp2"), "wb")
                        img.write(data)
                        img.close()
                        print("Saved file: " + os.path.join("output", obj[1:] + ".jp2"))
                        return True
                    elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                        img = open(os.path.join("output", obj[1:] + ".tiff"), "wb")
                        img.write(data)
                        img.close()
                        print("Saved file: " + os.path.join("output", obj[1:] + ".tiff"))
                        return True
                else:
                    img = Image.frombytes(mode, size, data)
                    img.save(os.path.join("output", obj[1:] + ".png"))
                    print("Saved file: " + os.path.join("output", obj[1:] + ".png"))
                    return True


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

    return True


if __name__ == '__main__':

    print('Welcome to PDF utilities!')
    inputFiles = glob.glob('input/*.pdf')
    print(f'Found {len(inputFiles)} PDF files:')
    [print(f'\t{os.path.basename(f)}') for f in inputFiles]
    
    print('\nChoose an action:')
    print('(1)\tMerge PDFs')
    print('(2)\tSplit PDF in two')
    print('(3)\tExtract images from PDF')
    print('(4)\tExtract text from PDF')
    print('(0)\tExit application')
    
    try:
        action = int(input('\nAction:\t'))
    except ValueError:
        print('Invalid action. Exiting.')
        exit(0)
    
    if action == 1: # Merge
        try:
            if len(inputFiles) < 2:
                print('Not enough files. Exiting.')
                exit(0)
            if len(inputFiles) == 2:
                numFiles = 2
            else:
                numFiles = int(input(f'How many files do you want to merge? (2 - {len(inputFiles)}) '))
                assert numFiles >= 2 and numFiles <= len(inputFiles)    
            
            print()
            [print(f'({i+1})\t{os.path.basename(f)}') for i, f in enumerate(inputFiles)]
            print()

            filesSequence = []
            for i in range(numFiles):
                num = int(input(f'Number of file #{i+1} to merge: '))
                assert num >= 1 and num <= len(inputFiles) and num not in filesSequence
                filesSequence.append(num)

            outputFilename = input('\nOutput file name: (leave blank for MergedFiles.pdf) ')
            
            if outputFilename == '':
                outputFilename = 'MergedFiles.pdf'
            elif '.pdf' not in outputFilename:
                outputFilename += '.pdf'

            result = merge([os.path.basename(inputFiles[i-1]) for i in filesSequence], outputFilename)

            if result:
                print('Success! Saved to output folder.')
                exit(0)
            else:
                print('Something went wrong...')
                exit(0)
            
        except (ValueError, AssertionError):
            print('Invalid number. Exiting.')
            exit(0)

    elif action == 2: # Split
        try:
            print()
            [print(f'({i+1})\t{os.path.basename(f)}') for i, f in enumerate(inputFiles)]
            print()

            num = int(input(f'Number of file to split: '))
            assert num >= 1 and num <= len(inputFiles)

            numPages = PyPDF2.PdfFileReader(inputFiles[num-1]).getNumPages()
            if numPages < 2:
                print('Not enough pages. Exiting.')
                exit(0)

            pageToSplit = int(input(f'Page to split PDF (from 1 to {numPages-1}): '))
            assert pageToSplit >= 1 and pageToSplit <= numPages - 1

            result = split(os.path.basename(inputFiles[num-1]), pageToSplit)

            if result:
                print('Success! Saved to output folder.')
                exit(0)
            else:
                print('Something went wrong...')
                exit(0)

        except (ValueError, AssertionError):
            print('Invalid number. Exiting.')
            exit(0)

    elif action == 3: # Extract images
        try:
            print()
            [print(f'({i+1})\t{os.path.basename(f)}') for i, f in enumerate(inputFiles)]
            print()

            num = int(input(f'Number of file to extract images: '))
            assert num >= 1 and num <= len(inputFiles)

            result = extractImages(os.path.basename(inputFiles[num-1]))

            if result:
                print('Success! Images saved to output folder.')
                exit(0)
            else:
                print('Something went wrong...')
                exit(0)

        except (ValueError, AssertionError):
            print('Invalid number. Exiting.')
            exit(0)

    elif action == 4: # Extract text
        try:
            print()
            [print(f'({i+1})\t{os.path.basename(f)}') for i, f in enumerate(inputFiles)]
            print()

            num = int(input(f'Number of file to extract text: '))
            assert num >= 1 and num <= len(inputFiles)

            result = extractText(os.path.basename(inputFiles[num-1]))

            if result:
                print('Success! Text saved to output folder.')
                exit(0)
            else:
                print('Something went wrong...')
                exit(0)

        except (ValueError, AssertionError):
            print('Invalid number. Exiting.')
            exit(0)
            
    elif action == 0:
        print('Bye!')
        exit(0)
    else:
        print('Invalid action. Exiting.')
        exit(0)
