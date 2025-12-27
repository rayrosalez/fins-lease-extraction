import dbutils

# Define paths for the Volumes
volume_path = "/Volumes/fins_team_3/lease_management/raw_lease_docs"
checkpoint_path = "/Volumes/fins_team_3/lease_management/pipeline_checkpoints/autoloader_checkpoints"

# Create internal directories for organizational workflow
dbutils.fs.mkdirs(f"{volume_path}/uploads")
dbutils.fs.mkdirs(f"{volume_path}/processed")
dbutils.fs.mkdirs(f"{volume_path}/failed")

print(f"Directory structure initialized at {volume_path}")