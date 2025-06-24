# upload_to_r2.py

import os
from utils.r2_uploader import upload_to_r2

DATA_DIR = "website/data"

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json"):
        file_path = os.path.join(DATA_DIR, filename)
        upload_to_r2(file_path)
