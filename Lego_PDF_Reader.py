#region Custom Classes
from Classes.Bricklink import Bricklink
from Classes.Bricklink_XML_Builder import Bricklink_XML_Builder
from Classes.LEGO_PDF_Part_Extractor import LEGO_PDF_Part_Extractor
from Classes.Rebrickable import Rebrickable
#endregion

if __name__ == "__main__":

    bricklink = Bricklink()
    pdf_extractor = LEGO_PDF_Part_Extractor()

    pdf_extractor.extract_parts()

    bricklink.get_part_details(pdf_extractor.part_dic)

    Bricklink_XML_Builder.build_and_save_xml(bricklink.part_details)