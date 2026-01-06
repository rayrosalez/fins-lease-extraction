"""
Utility functions for Databricks interactions
"""
from databricks.sdk import WorkspaceClient
from io import BytesIO
import random

def upload_to_volume(client, file_bytes, file_name, volume_path):
    """Upload file to Databricks Volume with random 4-digit suffix"""
    try:
        # Split filename and extension
        name_parts = file_name.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, extension = name_parts
            # Append random 4-digit number to filename
            random_suffix = random.randint(1000, 9999)
            new_file_name = f"{base_name}_{random_suffix}.{extension}"
        else:
            # No extension found, just append to the end
            random_suffix = random.randint(1000, 9999)
            new_file_name = f"{file_name}_{random_suffix}"
        
        # Construct the full path in the volume
        full_path = f"{volume_path}/uploads/{new_file_name}"
        
        # Convert bytes to BytesIO object (file-like object)
        file_obj = BytesIO(file_bytes)
        
        # Upload the file using the Files API
        client.files.upload(
            file_path=full_path,
            contents=file_obj,
            overwrite=True
        )
        
        return True, full_path, None
    except Exception as e:
        return False, None, str(e)

