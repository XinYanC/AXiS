"""
All interaction with Cloudinary (image hosting) should be through this file.

Required environment variables:
    CLOUDINARY_CLOUD_NAME  — found in your Cloudinary dashboard under
                             Settings > API Keys > Cloud name
    CLOUDINARY_API_KEY     — found in your Cloudinary dashboard under
                             Settings > API Keys > API key
    CLOUDINARY_API_SECRET  — found in your Cloudinary dashboard under
                             Settings > API Keys > API secret
"""
import os

import cloudinary
import cloudinary.uploader

CLOUDINARY_FOLDER = 'axis_listings'

CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
API_KEY = os.environ.get('CLOUDINARY_API_KEY')
API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')


def _configure():
    if not CLOUD_NAME:
        raise ValueError(
            'CLOUDINARY_CLOUD_NAME environment variable is not set.'
        )
    if not API_KEY:
        raise ValueError(
            'CLOUDINARY_API_KEY environment variable is not set.'
        )
    if not API_SECRET:
        raise ValueError(
            'CLOUDINARY_API_SECRET environment variable is not set.'
        )
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True,
    )


def upload_image(file) -> str:
    """
    Upload a file-like object or local path to Cloudinary.

    Args:
        file: A file-like object (e.g. from Flask's request.files) or a
              local file path string.

    Returns:
        str: The HTTPS URL of the uploaded image.

    Raises:
        ValueError: If Cloudinary credentials are missing.
        Exception: If the Cloudinary upload fails.
    """
    _configure()
    result = cloudinary.uploader.upload(
        file,
        folder=CLOUDINARY_FOLDER,
        resource_type='image',
    )
    return result['secure_url']
