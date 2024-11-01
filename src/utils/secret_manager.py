from google.cloud import secretmanager

def get_secret(key: str):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/392395172966/secrets/{key}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("utf-8")
