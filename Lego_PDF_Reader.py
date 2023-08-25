#region Custom Classes
from Bricklink import Bricklink
from Bricklink_XML_Builder import Bricklink_XML_Builder
from LEGO_PDF_Part_Extractor import LEGO_PDF_Part_Extractor
#endregion

if __name__ == "__main__":

    bricklink = Bricklink(debug=True)
    pdf_extractor = LEGO_PDF_Part_Extractor()

    pdf_extractor.extract_parts()

    bricklink.get_part_details(pdf_extractor.part_dic)

    Bricklink_XML_Builder.build_and_save_xml(bricklink.part_details)