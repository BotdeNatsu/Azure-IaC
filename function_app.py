
import logging
import json
import uuid

from src.vision_toolkit import VehicleImage, VEHICLE_TYPES

from src.database import Database

from src.storage_account import DataLake
# Azure Services
import azure.functions as func


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="VisionPrediction")
def VisionPrediction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    appCaller = req.headers.get('appCaller')
    appRecieverId = req.headers.get('appRecieverId')

    db = Database()
    get_date = db.get_date()
    
    if not req.files.values():
        return func.HttpResponse(
            {'error': 'No image data found in the request'}, 
            status_code=400
        )

    try:
        for file in req.files.values():
            # 0. Setup --------------------------------------------------------
            img_binary = file.stream.read()
            img = VehicleImage(img_binary)
            img.content['filename'] = file.filename

            # 1. Classification------------------------------------------------
            img.classify_vehicle_photo()
            n_labels     = img.content['n_labels']
            photo_type   = img.content['photo_type'  ]['label']
            vehicle_type = img.content['vehicle_type']['label']

            # 2. Classification Options ---------------------------------------
            # Classification 1 (VIN, DOCUMENTO): Get VIN or Plate
            if n_labels == 1:

                if photo_type == 'VIN':
                    img.extract_text(content_type='vin')
                elif photo_type == 'DOCUMENTO':
                    img.extract_entities_from_doc()

            # Classification 2 (FRONTAL R2, TRASERA R2): Get plate
            elif n_labels == 2:

                cond_trasera = (photo_type == 'TRASERA') and \
                                (vehicle_type in VEHICLE_TYPES)
                cond_frontal = (photo_type == 'FRONTAL') and \
                                (vehicle_type != 'Motocicleta')
                
                if cond_trasera or cond_frontal:
                    img.detect_plate()

            # 3. Set status and message ---------------------------------------
            img.set_status_message()
            logging.info(img.content)
            
            # 4. Obtaining parameters for the upload path
            path1 = img.content['vehicle_type']['label']
            path2 = img.content['photo_type']['label']

            if path1 is None:
                path1 = 'None'

            if path2 is None:
                path2 = 'None'    

            #Upload Image to Datalake
            st = DataLake()

            upload_file=st.upload_to_azure_blob(get_date.get('year'),get_date.get('month'),get_date.get('day'),path1,path2,file.filename,img_binary)
            break

        #Instance Cosmos Client
        client_cosmos = db.create_client()
        

        # Create Cosmos registry
        db.create_item(
                    client=client_cosmos.get('message'),
                    hour=get_date.get('hour_cosmos'),
                    status_code=200,
                    callcoment=str(img.content),
                    image_path=upload_file.get('path'),
                    guId= upload_file.get('guid'),
                    appCaller= appCaller,
                    appRecieverId= appRecieverId
                )
        

        return func.HttpResponse(
            body=json.dumps(img.content),
            status_code=200, 
            mimetype='application/json'
        )
    
    except Exception as e:
        logging.info(f'ERROR: {e}')
        return func.HttpResponse(
            body={'error': str(e), 'response': file.filename},
            status_code=500,
            mimetype='application/json'
        )
    