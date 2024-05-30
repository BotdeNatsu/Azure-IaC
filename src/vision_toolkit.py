import os
from io import BytesIO

import requests
from itertools import product, chain
import numpy as np

# Azure Services
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Natural Language Processing
import unicodedata
import re
import vininfo

# Visualization
from PIL import Image
import itertools
import matplotlib.pyplot as plt

#%% PARAMS
VEHICLE_TYPES = ['Automóvil', 'Camión', 'Motocicleta']

#%% Vision Toolkit - Vehicle Image Class
class VehicleImage:

    def __init__(self, img_binary):

        self.__VISION_PREDICTION_KEY = os.environ["VISION_PREDICTION_KEY"]
        self.__VISION_CLASSIFICATION_ITERATION_NAME = os.environ["VISION_CLASSIFICATION_ITERATION_NAME"]
        self.__VISION_CLASSIFICATION_PROJECT_ID = os.environ["VISION_CLASSIFICATION_PROJECT_ID"]
        self.__VISION_PREDICTION_ENDPOINT = os.environ["VISION_PREDICTION_ENDPOINT"]
        self.__VISION_THRESHOLD_CLASSIFICATION = os.environ["VISION_THRESHOLD_CLASSIFICATION"]

        self.__VISION_DETECTION_ITERATION_NAME = os.environ["VISION_DETECTION_ITERATION_NAME"]
        self.__VISION_DETECTION_PROJECT_ID = os.environ["VISION_DETECTION_PROJECT_ID"]
        self.__VISION_THRESHOLD_PLATE_DETECTION = os.environ["VISION_THRESHOLD_PLATE_DETECTION"]

        self.__COMPUTER_VISION_ENDPOINT = os.environ["COMPUTER_VISION_ENDPOINT"]
        self.__COMPUTER_VISION_KEY = os.environ["COMPUTER_VISION_KEY"]

        self.__DOCUMENT_INTELLIGENCE_ENDPOINT = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
        self.__DOCUMENT_INTELLIGENCE_KEY = os.environ["DOCUMENT_INTELLIGENCE_KEY"]
        self.__DOCUMENT_INTELLIGENCE_MODEL_ID = os.environ["DOCUMENT_INTELLIGENCE_MODEL_ID"]
        self.__DOCUMENT_INTELLIGENCE_THRESHOLD_EXTRACTION = os.environ["DOCUMENT_INTELLIGENCE_THRESHOLD_EXTRACTION"]
        
        #%% PARAMS
        self.VEHICLE_TYPES = ['Automóvil', 'Camión', 'Motocicleta']
        self.PHOTO_TYPES = [
            'FRONTAL R2'  , 'FRONTAL R4'  ,
            'TRASERA R2'  , 'TRASERA R4'  ,
            'DERECHA R2'  , 'DERECHA R4'  ,
            'IZQUIERDA R2', 'IZQUIERDA R4',
            'INTERIOR R2' , 'INTERIOR R4' ,
            'VIN',
            'DOCUMENTO'
        ]


        #%% Azure APIs
        # Custom Vision ---------------------------------------------------------------
        self.HEADERS_CUSTOM_VISION = {
            'Content-Type': 'application/octet-stream',
            'Prediction-Key': self.__VISION_PREDICTION_KEY
        }
        # Classification
        PROJECT_NAME = self.__VISION_CLASSIFICATION_ITERATION_NAME
        PROJECT_ID = self.__VISION_CLASSIFICATION_PROJECT_ID
        self.ENDPOINT_CLASSIFICATION = (
            f'{self.__VISION_PREDICTION_ENDPOINT}'
            f'customvision/v3.0/Prediction/'
            f'{PROJECT_ID}/classify/iterations/{PROJECT_NAME}/image'
        )
        self.THRESHOLD_CLASSIFICATION = float(self.__VISION_THRESHOLD_CLASSIFICATION)
        # Object Detection
        PROJECT_NAME = self.__VISION_DETECTION_ITERATION_NAME
        PROJECT_ID = self.__VISION_DETECTION_PROJECT_ID
        self.ENDPOINT_PLATE_DETECTION = (
            f'{self.__VISION_PREDICTION_ENDPOINT}'
            f'customvision/v3.0/Prediction/'
            f'{PROJECT_ID}/detect/iterations/{PROJECT_NAME}/image'
        )
        self.THRESHOLD_PLATE_DETECTION = float(self.__VISION_THRESHOLD_PLATE_DETECTION)
        # -----------------------------------------------------------------------------


        # Computer Vision -------------------------------------------------------------
        self.ENDPOINT_PLATE_EXTRACTION = (
            f'{self.__COMPUTER_VISION_ENDPOINT}'
        )
        self.KEY_PLATE_EXTRACTION = self.__COMPUTER_VISION_KEY
        # -----------------------------------------------------------------------------


        # Document Intelligence -------------------------------------------------------
        self.ENDPOINT_DOCUMENT_INTELLIGENCE = self.__DOCUMENT_INTELLIGENCE_ENDPOINT
        self.KEY_DOCUMENT_INTELLIGENCE = self.__DOCUMENT_INTELLIGENCE_KEY
        self.MODEL_ID = self.__DOCUMENT_INTELLIGENCE_MODEL_ID

        self.THRESHOLD_DOC_EXTRACTION = float(self.__DOCUMENT_INTELLIGENCE_THRESHOLD_EXTRACTION)
        # -----------------------------------------------------------------------------

        self.img_binary = img_binary
        self.content = {
            'filename'          : None,
            'status'            : None,                                        # SUCCESS, REPEAT, REVIEW
            'message'           : None,
            'applied_fuctions'  : [],       
            'n_labels'          : 0,
            'vehicle_type'      : {'label': None, 'probability': None},
            'photo_type'        : {'label': None, 'probability': None},
            'vin'               : {'text' : None, 'probability': None},
            'plate'             : {'text' : None, 'probability': None}
        }

    @staticmethod
    def show(img_binary):
        with Image.open(BytesIO(img_binary)) as img:
            print(img.size)
            plt.imshow(img)
            plt.axis('off')
            plt.show()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans the given text by performing the following operations:
        1. Uppercase the text.
        2. Remove accents from the text.
        3. Replace '/' with ' ' between VINs.
        4. Remove special characters.
        5. Remove double spaces.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: The cleaned text.
        """
        if text is None:
            return ''

        text = text.upper()                                                    # Uppercase
        text = ''.join(                                                        # Remove accents
            char for char in unicodedata.normalize('NFD', text)
            if unicodedata.category(char) != 'Mn'                
        )
        text = re.sub(r'([A-Z0-9]+)[/]([A-Z0-9]+)', r'\1 \2', text)            # Replace '/' with ' ' between VINs
        text = re.sub(r'[^A-Z0-9\s]+', '', text)                               # Remove special characters
        text = re.sub(r'\s+', ' ', text)                                       # Remove double spaces

        return text

    @staticmethod
    def validate_entities(text: str, content_type: str) -> str:
        """
        Validates and extracts entities from the given text based on the 
        specified content type.

        Args:
            text (str): The input text to validate and extract entities from.
            content_type (str): The type of content to validate and extract 
                                entities for; valid options are 'vin' and 
                                'plate'.

        Returns:
            str: The extracted entity value if found, or None if no entity 
                 is found.
        """
        def get_ocr_combinations(vin_group: str, group_text: str) -> list: 
            """
            Generate all possible combinations of OCR errors for a given VIN group and group text.

            Args:
                vin_group (str): The VIN group.
                group_text (str): The text within the group.

            Returns:
                list: A list of complete VIN groups with all possible OCR error combinations.
            """

            # Define OCR errors observed
            OCR_ERRORS_OBSERVED = {  
                # Wrong: Correct values                                    # Recall that [IOQ] are illegal characters
                # Letters
                'A': ['4'],
                'I': ['1'],
                'J': ['9'],
                'O': ['0', '9'],
                'Q': ['0'],
                'R': ['K'],
                'S': ['8'],
                # Numbers
                '5': ['S']
            }

            # Generate mapping of OCR errors
            mapping_ocr_errors = {
                char_wrong:
                [
                    char_correct 
                    for char_correct in (char_corrects + [char_wrong]) 
                    if re.search(                                          # Check if the correct character is valid for that vin_group
                        VALID_VIN_CHARACTER[vin_group],
                        char_correct
                    )
                ] 
                for char_wrong, char_corrects in OCR_ERRORS_OBSERVED.items()
            }

            # Remove empty lists from mapping
            mapping_ocr_errors = {
                char_wrong:
                char_corrects
                for char_wrong, char_corrects in mapping_ocr_errors.items()
                if char_corrects != []
            }
            
            # Generate all combinations of OCR errors
            all_combinations_group = product(*[
                (
                    mapping_ocr_errors[char] 
                    if char in mapping_ocr_errors 
                    else [char]
                )
                for char in group_text
            ])
            
            # Generate complete VIN groups
            complete_vin_groups = [
                ''.join(chars) 
                for chars in all_combinations_group
            ]
            
            return complete_vin_groups

        if content_type == 'vin':
            VALID_VIN_CHARACTER = {
                'WMI_VDS'          : r'[A-HJ-NPR-Z0-9]',
                'CHECK_DIGIT'      : r'[0-9X]',
                'MODEL_YEAR'       : r'[A-HJ-NPR-Y1-9]',
                'PLANT_AND_SERIAL' : r'[A-HJ-NPR-Z0-9]'
            }

            pattern = (                                                        # Source: https://vin.dataonesoftware.com/vin_basics_blog/bid/96920/what-s-in-the-vehicle-identification-number#:~:text=Position%209%3A%20The%20Check%20Digit,encountered%20VIN%20using%20a%20calculation 
                r'\b'                                                          # Valid VIN characters:
                r'(?P<WMI_VDS>(?:[A-Z0-9]\s?){8})'                             # -> [A-HJ-NPR-Z0-9]{8}
                r'(?P<CHECK_DIGIT>(?:[A-Z0-9]\s?){1})'                         # -> [0-9X]
                r'(?P<MODEL_YEAR>(?:[A-Z0-9]\s?){1})'                          # -> [A-HJ-NPR-Y1-9]
                r'(?P<PLANT_AND_SERIAL>(?:[A-Z0-9]\s?){6}[A-Z0-9])'            # -> [A-HJ-NPR-Z0-9]{7}
                r'\b'
            )
            pattern = re.compile(pattern)
            entity_options = pattern.finditer(text) 
                                        
            for option in entity_options:
                option = {
                    vin_group: group_text.replace(' ', '') 
                    for vin_group, group_text in option.groupdict().items()
                }
                
                try:
                    vin_value = ''.join(option.values())
                    vin = vininfo.Vin(vin_value)

                    if vin.verify_checksum():
                        return vin_value
                    
                except:
                    print('VIN_NO_VALIDO', vin_value)
                
                VIN_EXTRACTED = {
                    vin_group
                    :
                    get_ocr_combinations(vin_group, group_text) 
                    for vin_group, group_text in option.items()
                }
                for vin_option in product(*VIN_EXTRACTED.values()):
        
                    try:
                        vin_value = ''.join(vin_option)
                        vin = vininfo.Vin(vin_value)
                        if vin.verify_checksum():
                            return vin_value
                        
                    except:
                        print('ERROR_VIN', vin_value)

            return None

        elif content_type == 'plate':
            pattern = r'(?:[A-Z]{3}|[0-9]{3})(?:[0-9]{2}[0-9A-Z])\b'
            pattern = re.compile(pattern)
            entity_options = pattern.finditer(text)

            for option in entity_options:
                return option.group()
        
        else:
            return text

    def set_status_message(self):
        n_labels     = self.content['n_labels']

        photo_type   = self.content['photo_type']['label']
        vehicle_type = self.content['vehicle_type']['label']

        vin_text     = self.content['vin']['text']
        plate_text   = self.content['plate']['text']

        # No classification (likely due to image quality) ---------------------
        if n_labels == 0:

            self.content['status'] = 'REPEAT'
            self.content['message'] = (
                'No classification (likely due to image quality)'
            )

        # Classification 1 (VIN, DOCUMENTO) -----------------------------------
        elif n_labels == 1:

            if photo_type == 'VIN':
                if vin_text:                                                 
                    self.content['status'] = 'SUCCESS'
                    self.content['message'] = 'Valid VIN was found'
                else:
                    self.content['status'] = 'REPEAT'
                    self.content['message'] = 'No valid VIN was found'

            elif photo_type == 'DOCUMENTO':
                if (plate_text is not None) and (vin_text is not None):
                    self.content['status'] = 'SUCCESS'
                    self.content['message'] = 'VIN and Plate were found'
                elif (plate_text is None) and (vin_text is None):
                    self.content['status'] = 'REPEAT'
                    self.content['message'] = 'VIN and Plate were not found'
                else:
                    self.content['status'] = 'REVIEW'
                    self.content['message'] = 'No VIN or Plate were found'

            else:
                self.content['status'] = 'REVIEW'
                self.content['message'] = (
                    'Single prediction but not in [VIN, DOCUMENTO]'
                )
    
        # Classification 2 (FRONTAL R2, TRASERA R2): --------------------------
        elif n_labels == 2:

            cond_trasera = (photo_type == 'TRASERA') and \
                           (vehicle_type in self.VEHICLE_TYPES)
            cond_frontal = (photo_type == 'FRONTAL') and \
                           (vehicle_type != 'Motocicleta')

            if cond_trasera or cond_frontal:
                if plate_text:
                    self.content['status'] = 'SUCCESS'
                    self.content['message'] = 'Valid Plate was found'
                else:
                    self.content['status'] = 'REPEAT'
                    self.content['message'] = 'No valid Plate was found'

            else:
                self.content['status'] = 'SUCCESS'
                self.content['message'] = 'No further processing needed'

        # Classification 3+: Model error --------------------------------------
        elif n_labels >= 3:

            self.content['status'] = 'REVIEW'
            self.content['message'] = (
                'Multiple predictions, at most 2 were expected'
            )
        
    def classify_vehicle_photo(self):
        """
        Classifies a vehicle photo using Azure AI Custom Vision API.

        This method sends the vehicle photo to the Azure AI Custom Vision API
        for classification. It retrieves the predictions and stores the most
        probable vehicle type and photo type in the `self.content` dictionary.
        """
        self.content['applied_fuctions'].append('classify_vehicle_photo')

        # Call Azure AI Custom vision API (multi-label) -----------------------
        response = requests.request( 
            method='POST', 
            url=self.ENDPOINT_CLASSIFICATION,
            headers=self.HEADERS_CUSTOM_VISION, 
            data=self.img_binary#img_binary
        )

        # The predictions are ordered from lowest to highest probability 
        # to guarantee that the most probable values will be present in 
        # 'self.content', regardless of the number of labels predicted. 
        predictions = response.json()['predictions'][::-1]

        for prediction in predictions:  
                
            if prediction['probability'] >= self.THRESHOLD_CLASSIFICATION:

                if prediction['tagName'] in self.VEHICLE_TYPES:
                    self.content['vehicle_type']['label'] = \
                        prediction['tagName']
                    self.content['vehicle_type']['probability'] = \
                        prediction['probability']

                else: # self.PHOTO_TYPES
                    self.content['photo_type']['label'] = \
                        prediction['tagName'].split()[0]                       # i.e. 'FRONTAL R4' -> 'FRONTAL'
                    self.content['photo_type']['probability'] = \
                        prediction['probability']

                self.content['n_labels'] += 1

    def extract_entities_from_doc(self):
        """
        Extracts entities from a document using Azure AI Document Intelligence
        API.

        This method calls the Azure AI Document Intelligence API to analyze 
        a document and extract entities such as license plate (Placa) and 
        vehicle identification number (VIN). It cleans the extracted values 
        and validates them before storing them in the `content` dictionary.
        """
        self.content['applied_fuctions'].append('extract_entities_from_doc')

        # Call Azure AI Document Intelligence API -----------------------------
        client = DocumentAnalysisClient(
            endpoint=self.ENDPOINT_DOCUMENT_INTELLIGENCE, 
            credential=AzureKeyCredential(self.KEY_DOCUMENT_INTELLIGENCE)
        )
            
        response = client.begin_analyze_document(
            model_id=self.MODEL_ID, 
            document=self.img_binary
        )
        # ---------------------------------------------------------------------
        
        fields = response.result().documents[0].fields

        plate_value = VehicleImage.clean_text(fields['Placa'].value)
        plate_value = VehicleImage.validate_entities(plate_value, 'plate')
        plate_confidence = fields['Placa'].confidence

        vin_value = VehicleImage.clean_text(fields['VIN'].value)
        vin_value = VehicleImage.validate_entities(vin_value, 'vin')
        vin_confidence = fields['VIN'].confidence

        self.content['applied_fuctions'].append('clean_text&validate_entities')
        self.content['plate']['text']        = plate_value
        self.content['plate']['probability'] = plate_confidence
        self.content['vin'  ]['text']        = vin_value
        self.content['vin'  ]['probability'] = vin_confidence

    def detect_plate(self):
        """
        Detects and extracts the license plate from an image using Azure
        AI Custom Vision API.
        """

        def crop_image(image, bounding_box, min_size=50):
            """
            Crops an image based on the bounding box coordinates. The cropped
            image is then resized to a minimum size.

            Parameters:
            - image: The input image to be cropped.
            - bounding_box: A dictionary containing the coordinates of the 
                    bounding box. The dictionary should have the 
                    following keys: 'left', 'top', 'width', and 
                    'height'.
            - min_size: The minimum size of the cropped image.

            Returns:
            - image_bytes: The cropped image data in bytes format.
            """
            # Extract region defined by the bounding box
            left   = bounding_box['left']   * image.width
            top    = bounding_box['top']    * image.height
            width  = max(min_size, bounding_box['width']  * image.width)
            height = max(min_size, bounding_box['height'] * image.height)

            # Crop the image
            img_cropped = image.crop((
                left, 
                top, 
                left + width, 
                top + height
            ))

            # Create an in-memory bytes buffer
            image_bytes = BytesIO()

            # Save the image to the bytes buffer
            img_cropped.save(image_bytes, format='PNG')
            
            # Get the byte data from the buffer
            image_bytes = image_bytes.getvalue()

            return image_bytes


        self.content['applied_fuctions'].append('detect_plate')

        # Call Azure AI Custom vision API (object-detection) ------------------
        img_data = BytesIO(self.img_binary)
        original_image = Image.open(img_data)

        response = requests.request(
            method='POST', 
            url=self.ENDPOINT_PLATE_DETECTION, 
            headers=self.HEADERS_CUSTOM_VISION, 
            data=self.img_binary
        )
        # ---------------------------------------------------------------------

        predictions = response.json()['predictions']

        if predictions and (predictions[0]['probability'] 
                            >= self.THRESHOLD_PLATE_DETECTION
                            ):
            bounding_box = predictions[0]['boundingBox']
            self.content['plate']['probability']  = \
                predictions[0]['probability']

            # Cropped Image ---------------------------------------------------
            img_cropped_bytes = crop_image(
                original_image, 
                bounding_box
            )
            img_cropped_bytes = BytesIO(img_cropped_bytes)

            img_cropped = VehicleImage(img_cropped_bytes)
            img_cropped.extract_text(content_type='plate')
            self.content['applied_fuctions'].append('extract_text:cropped')
            # -----------------------------------------------------------------

            self.content['plate']['text'] = \
                img_cropped.content['plate']['text']

    def extract_text(self, content_type: str):
        """
        Extracts text from an image using Azure AI Vision API (OCR).

        Args:
            content_type (str): The type of content being extracted.
        """
        self.content['applied_fuctions'].append(f'extract_text:{content_type}')         

        # Call Azure AI Vision API (OCR) --------------------------------------
        client = ImageAnalysisClient(
            endpoint=self.ENDPOINT_PLATE_EXTRACTION,
            credential=AzureKeyCredential(self.KEY_PLATE_EXTRACTION)
        )

        response = client.analyze(
            image_data=self.img_binary,
            visual_features=[VisualFeatures.READ]
        )
        # ---------------------------------------------------------------------
        
        lines = response.read['blocks'][0]['lines']
        text = ' '.join(line['text'] for line in lines)
        text_cleaned = VehicleImage.clean_text(text)
        search = VehicleImage.validate_entities(text_cleaned, content_type)
        self.content['applied_fuctions'].append('clean_text&validate_entities')

        if search:                                                 
            self.content[content_type]['text'] = search

            confidence_per_line = [
                [word['confidence'] for word in line['words']] 
                for line in lines
            ]
            self.content[content_type]['probability'] = np.median(
                list(chain.from_iterable(confidence_per_line))
            )