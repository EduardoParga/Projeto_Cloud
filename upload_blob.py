import sys
from load_azure import upload_file_to_blob

if len(sys.argv) < 3:
    print("Uso: python upload_blob.py <container> <local_path> [blob_name]")
    sys.exit(1)

container = sys.argv[1]
local_path = sys.argv[2]
blob_name = sys.argv[3] if len(sys.argv) > 3 else None
if blob_name is None:
    import os
    blob_name = os.path.basename(local_path)

upload_file_to_blob(container, local_path, blob_name)
print("Upload concluído:", blob_name)
