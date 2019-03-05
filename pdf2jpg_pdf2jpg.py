from pdf2jpg import pdf2jpg

def main():
    inputpath = r"C:\302015_c.pdf"
    outputpath = r"C:\Users\azkb075\Downloads"
    # To convert single page
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="1, 2")
    print(result)


if __name__ == '__main__':
    main()
