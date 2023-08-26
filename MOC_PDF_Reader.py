from pdfminer.high_level import extract_text
import fitz
import keras_ocr

import math


class Organised_Left_Right:
    def get_distance(predictions):
        """
        Function returns dictionary with (key,value):
            * text : detected text in image
            * center_x : center of bounding box (x)
            * center_y : center of bounding box (y)
            * distance_from_origin : hypotenuse
            * distance_y : distance between y and origin (0,0)
        """
        
        # Point of origin
        x0, y0 = 0, 0    # Generate dictionary
        detections = []
        for group in predictions:
            # Get center point of bounding box
            top_left_x, top_left_y = group[1][0]
            bottom_right_x, bottom_right_y = group[1][1]
            center_x = (top_left_x + bottom_right_x) / 2
            center_y = (top_left_y + bottom_right_y) / 2    # Use the Pythagorean Theorem to solve for distance from origin
        distance_from_origin = math.dist([x0,y0], [center_x, center_y])    # Calculate difference between y and origin to get unique rows
        distance_y = center_y - y0    # Append all results
        detections.append({
                            'text':group[0],
                            'center_x':center_x,
                            'center_y':center_y,
                            'distance_from_origin':distance_from_origin,
                            'distance_y':distance_y
                        })    
        return detections
    
    def distinguish_rows(lst, thresh=15):
        """Function to help distinguish unique rows"""
        
        sublists = [] 
        for i in range(0, len(lst)-1):
            if lst[i+1]['distance_y'] - lst[i]['distance_y'] <= thresh:
                if lst[i] not in sublists:
                    sublists.append(lst[i])
                sublists.append(lst[i+1])
            else:
                yield sublists
                sublists = [lst[i+1]]
        yield sublists

    def detect_w_keras(image_path):
        """Function returns detected text from image"""
    
        # Initialize pipeline
        pipeline = keras_ocr.pipeline.Pipeline()    # Read in image path
        read_image = keras_ocr.tools.read(image_path)    # prediction_groups is a list of (word, box) tuples
        prediction_groups = pipeline.recognize([read_image])    
        return prediction_groups[0]
    
    def main(image_paths, thresh, order='yes'):
        """
        Function returns predictions in human readable order 
        from left to right & top to bottom
        """
        
        predictions = Organised_Left_Right.detect_w_keras(image_paths)
        predictions = Organised_Left_Right.get_distance(predictions)
        predictions = list(Organised_Left_Right.distinguish_rows(predictions, thresh))    # Remove all empty rows
        predictions = list(filter(lambda x:x!=[], predictions))    # Order text detections in human readable format
        ordered_preds = []
        ylst = ['yes', 'y']
        for pr in predictions:
            if order in ylst: 
                row = sorted(pr, key=lambda x:x['distance_from_origin'])
                for each in row: 
                    ordered_preds.append(each['text'])    
        return ordered_preds
    

if __name__ == "__main__":
    pdf_location = "C:\\Users\\ryanc\\Documents\\Projects\\Bricklink_XML_Formatter\\Lego\\Pokemon\\Pokeball.pdf"

    open_file = fitz.open(pdf_location)
    page_list = [93,94,95]

    pipeline = keras_ocr.pipeline.Pipeline()

    image_pages = []
    for index, page_no in enumerate(page_list):

        page = open_file.load_page(page_no - 1)
        temp_pixmap = page.get_pixmap()
        file_name = "temp" + str(index) + ".jpg"
        temp_pixmap.save(file_name)
        image_pages.append(file_name)

    read_images = [keras_ocr.tools.read(img) for img in image_pages]
    prediction_groups = pipeline.recognize(read_images)

    olr = []
    for img in image_pages:
        olr.append(Organised_Left_Right.main(img, 15))

    for parts in prediction_groups:
        for text in parts:
            print(text[0])


    open_file.close()


