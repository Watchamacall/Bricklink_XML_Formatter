from pdfminer.high_level import extract_text
import fitz
if __name__ == "__main__":
    pdf_location = "C:\\Users\\ryanc\\Documents\\Projects\\Bricklink_XML_Formatter\\Lego\\Pokemon\\Pokeball.pdf"

    open_file = fitz.open(pdf_location)
    page_list = [93,94,95]

    for page_no in page_list:

        page = open_file.load_page(page_no)

        img = page.get_pixmap()

        output_file = 'test.jpg'

        img.save(output_file)

    open_file.close()