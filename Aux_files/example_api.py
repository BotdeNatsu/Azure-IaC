import base64
from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

from vision_toolkit import VehicleImage

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    if not request.data:
        return jsonify({'error': 'No image data found in the request'}), 400

    try:
        # Read the binary data from the request body
        # img_data = BytesIO(request.data)                                # TEMP
        # image = Image.open(img_data)
        # print('request_type', type(request.data))
        print(type(request.data))
        img = VehicleImage(request.data)
        img.classify_vehicle_photo()

        # No classification (likely due to image quality)
        if (img.content['n_info'] == 0):
            img.content['status'] = 'REPEAT'

        # Classification 1 (VIN, DOCUMENTO): Get VIN or Plate
        if img.content['n_info'] == 1:
            if img.content['photo_type']['label'] == 'VIN':
                img.extract_text(content_type='vin')
            if img.content['photo_type']['label'] == 'DOCUMENTO':
                img.extract_entities_from_doc()

        # Classification 2 (FRONTAL R2, TRASERA R2): Get plata
        if img.content['n_info'] == 2:
            if (img.content['photo_type']['label'] in ['FRONTAL', 'TRASERA']):  # [NEXT] MOTO
                cropped_image = img.detect_plate()
            else:
                img.content['status'] = 'SUCCESS'
        # Classification 3+: Model error -> REVIEW
        if (img.content['n_info'] >= 3):
            img.content['status'] = 'REVIEW'
        
        # buffered = BytesIO()
        # image.save(buffered, format='PNG')
        # # plt.imshow(image)
        # img_byte = buffered.getvalue()
        # img_base64 = base64.b64encode(img_byte).decode('utf-8')

        return jsonify(img.content)
    except Exception as e:
        return jsonify({'error': str(e), 'response': str(img.content)}), 500

if __name__ == '__main__':
    app.run(debug=True)
