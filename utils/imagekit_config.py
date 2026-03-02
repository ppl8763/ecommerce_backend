from imagekitio import ImageKit
import os
from dotenv import load_dotenv

load_dotenv()

IMAGEKIT_PUBLIC_KEY = os.getenv("IMAGEKIT_PUBLIC_KEY")
IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")
IMAGEKIT_URL_ENDPOINT = os.getenv("IMAGEKIT_URL_ENDPOINT")

if not IMAGEKIT_PUBLIC_KEY or not IMAGEKIT_PRIVATE_KEY or not IMAGEKIT_URL_ENDPOINT:
    raise Exception("ImageKit environment variables not set")

imagekit = ImageKit(
    public_key=IMAGEKIT_PUBLIC_KEY,
    private_key=IMAGEKIT_PRIVATE_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)