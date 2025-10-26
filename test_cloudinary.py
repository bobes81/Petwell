
import os
import cloudinary
from cloudinary.uploader import upload

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

try:
    result = upload("https://upload.wikimedia.org/wikipedia/commons/a/a3/June_odd-eyed-cat.jpg")
    print("✅ Upload successful:", result.get("secure_url"))
except Exception as e:
    print("❌ Upload failed:", e)

