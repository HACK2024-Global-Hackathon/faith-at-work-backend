import requests
import json

def upload_image_to_event(event_id, image_path, oauth_token):
    # Step 1: Upload the image
    media_upload_url = "https://www.eventbriteapi.com/v3/media/upload/"
    upload_params = {
        'type': 'image-event-logo',
        'token': oauth_token
    }
    
    # Get upload instructions
    response = requests.get(media_upload_url, params=upload_params)
    response_data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"Failed to get upload instructions: {response_data.text}")

    print(response_data)

    # Step 2: Upload the actual image
    upload_url = response_data['upload_url']
    print(f"upload_url: {upload_url}")
    file_param_name = response_data['file_parameter_name']
    print(file_param_name)
    
    with open(image_path, 'rb') as img_file:
        file_data = {file_param_name: img_file.read()}
    
    print(f"size in bytes: {len(file_data[file_param_name])}")
    print(upload_url)

    upload_response = requests.post(
        upload_url,
        data=response_data['upload_data'],
        files=file_data
    )
    
    if upload_response.status_code != 200:
        print(dir(upload_response))
        print(f"Status code: {upload_response.status_code}")
        print(f"Raw: {upload_response.raw}")
        # print(upload_response.json())
        print(f"Reason: {upload_response.reason}")
        raise Exception(f"Failed to upload image: {upload_response.text}")
    
    # Step 3: Assign the uploaded image to the event
    uploaded_image_id = upload_response.json()['id']
    
    event_update_url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Content-Type': 'application/json'
    }
    
    update_data = json.dumps({"event": {"logo_id": uploaded_image_id}})
    update_response = requests.post(event_update_url, headers=headers, data=update_data)
    
    if update_response.status_code != 200:
        raise Exception(f"Failed to update event with image: {update_response}")
    
    return update_response.json()


oauth_token = "replace this"
event_id = 'replace this'
image_path = '../assets/1483741-381095183.jpg'
result = upload_image_to_event(event_id, image_path, oauth_token)
print(result)
