import os
import aiohttp
import asyncio
import base64
from io import BytesIO
from quart import Quart, request, abort
from drive_defs import create_folder, upload_to_drive
from utility_defs import time_conversion

pi_cams = ['http://192.168.0.101:5000']

app = Quart(__name__)

def check_basic_auth(auth_header):
    if not auth_header:
        return False
    auth_type, auth_string = auth_header.split(' ')
    if auth_type.lower() != 'basic':
        return False
    return auth_string == os.environ.get("BASIC_AUTH_CREDENTIALS")

async def capture_image(pi, idx, folder_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{pi}/capture') as response:
            if response.status == 200:
                image_data = await response.read()
                print(f'Image {idx} received.')

                # Upload the image to Google Drive
                if upload_to_drive(BytesIO(image_data), f'cam_{idx}.jpg', folder_id):
                    print(f'Image {idx} uploaded to Google Drive.')
                else:
                    print(f'Error uploading image {idx} to Google Drive.')
            else:
                print(f'Error: {response.status} from {pi}')

@app.route('/webhook', methods=['POST'])
async def webhook_listener():
    if not check_basic_auth(request.headers.get('Authorization')):
        abort(401)
    data = await request.get_json()
    if data is None:
        return 'No data received', 400

    # Process the received data here
    timestamp = time_conversion(data['SubmittedAt'])
    folder_name = timestamp + ' ' + data['Truck Rego']
    parent_id = os.environ.get("PARENT_ID")
    folder_id = create_folder(parent_id, folder_name)

    # Capture and upload images
    tasks = [capture_image(pi, idx, folder_id) for idx, pi in enumerate(pi_cams, start=1)]
    await asyncio.gather(*tasks)

    return 'Webhook received', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

