from unittest.mock import patch

import pytest

import data.cloudinary_connect as ccon


def test_configure_missing_cloud_name():
    with patch.multiple(
        ccon,
        CLOUD_NAME=None,
        API_KEY='test_key',
        API_SECRET='test_secret',
    ):
        with pytest.raises(ValueError, match='CLOUDINARY_CLOUD_NAME'):
            ccon._configure()


def test_configure_missing_api_key():
    with patch.multiple(
        ccon,
        CLOUD_NAME='test_cloud',
        API_KEY=None,
        API_SECRET='test_secret',
    ):
        with pytest.raises(ValueError, match='CLOUDINARY_API_KEY'):
            ccon._configure()


def test_configure_missing_api_secret():
    with patch.multiple(
        ccon,
        CLOUD_NAME='test_cloud',
        API_KEY='test_key',
        API_SECRET=None,
    ):
        with pytest.raises(ValueError, match='CLOUDINARY_API_SECRET'):
            ccon._configure()


def test_configure_success_calls_cloudinary_config():
    with patch.multiple(
        ccon,
        CLOUD_NAME='test_cloud',
        API_KEY='test_key',
        API_SECRET='test_secret',
    ), patch('data.cloudinary_connect.cloudinary.config') as mock_config:
        ccon._configure()

    mock_config.assert_called_once_with(
        cloud_name='test_cloud',
        api_key='test_key',
        api_secret='test_secret',
        secure=True,
    )


def test_upload_image_returns_secure_url():
    expected_url = 'https://res.cloudinary.com/demo/image/upload/axis.png'

    with patch.multiple(
        ccon,
        CLOUD_NAME='test_cloud',
        API_KEY='test_key',
        API_SECRET='test_secret',
    ), patch('data.cloudinary_connect.cloudinary.config'), patch(
        'data.cloudinary_connect.cloudinary.uploader.upload'
    ) as mock_upload:
        mock_upload.return_value = {'secure_url': expected_url}
        url = ccon.upload_image('fake_file')

    assert url == expected_url
    mock_upload.assert_called_once_with(
        'fake_file',
        folder=ccon.CLOUDINARY_FOLDER,
        resource_type='image',
    )
