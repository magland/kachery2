import os
import shutil
import requests
from typing import Union
from urllib.parse import quote
import time

from .get_kachery2_dir import get_kachery2_dir

from .store_file_local import _random_string
from .store_file_local import _compute_file_hash, store_file_local
from ._custom_storage_backend import get_custom_storage_backend

from ._api_requests import _initiate_file_upload_request, _finalize_file_upload_request


def store_file(filename: str, *, label: Union[str, None] = None, cache_locally: bool = False, local: bool = False):
    if local:
        return store_file_local(filename, label=label)
    if os.environ.get('KACHERY_STORE_FILE_DIR') is not None:
        return store_file_local(filename, label=label, store_file_dir=os.environ['KACHERY_STORE_FILE_DIR'], store_file_prefix=os.getenv('KACHERY_STORE_FILE_PREFIX', None))

    _custom_storage_backend = get_custom_storage_backend()
    use_custom_storage_backend = _custom_storage_backend is not None and hasattr(_custom_storage_backend, 'store_file')
    if not use_custom_storage_backend:
        size = os.path.getsize(filename)
        alg = 'sha1'
        hash0 = _compute_file_hash(filename, algorithm=alg)
        uri = f'{alg}://{hash0}'
        kachery_zone = os.environ.get('KACHERY_ZONE', 'default')
        timer = time.time()
        response = None
        while True:
            response = _initiate_file_upload_request(
                size=size,
                hash_alg=alg,
                hash=hash0,
                zone=kachery_zone
            )
            already_exists = response.get('alreadyExists', False)
            already_pending = response.get('alreadyPending', False)
            if already_exists:
                if label is not None:
                    uri = f'{uri}?label={quote(label)}'
                return uri
            elif already_pending:
                elapsed = time.time() - timer
                if elapsed > 60:
                    raise Exception(f'Upload is already pending... timeout: {uri}')
                print(f'Upload is already pending... waiting to retry {uri}')
                time.sleep(5)
            else:
                break

        assert response is not None

        signed_upload_url = response['signedUploadUrl']
        object_key = response['objectKey']
        with open(filename, 'rb') as f:
            resp_upload = requests.put(signed_upload_url, data=f)
            if resp_upload.status_code != 200:
                print(signed_upload_url)
                raise Exception(f'Error uploading file to bucket ({resp_upload.status_code}) {resp_upload.reason}: {resp_upload.text}')
        response2 = _finalize_file_upload_request(
            object_key=object_key,
            hash_alg=alg,
            hash0=hash0,
            kachery_zone=kachery_zone,
            size=size
        )

        if not response2.get('success', False):
            raise Exception(f'Error finalizing file upload: {uri}')

        if label is not None:
            uri = f'{uri}?label={quote(label)}'

        if label is not None:
            uri = f'{uri}?label={quote(label)}'
    else:
        # custom storage backend
        assert _custom_storage_backend is not None
        uri = _custom_storage_backend.store_file(filename, label=label)
        hash0 = None # only computed if needed

    if cache_locally:
        kachery_cloud_dir = get_kachery2_dir()
        if hash0 is None:
            # this would be None for custom storage backend
            hash0 = _compute_file_hash(filename, algorithm='sha1')
        e = hash0
        cache_parent_dir = f'{kachery_cloud_dir}/hash0/{e[0]}{e[1]}/{e[2]}{e[3]}/{e[4]}{e[5]}'
        if not os.path.exists(cache_parent_dir):
            os.makedirs(cache_parent_dir)
        cache_filename = f'{cache_parent_dir}/{hash0}'
        if not os.path.exists(cache_filename):
            tmp_filename = f'{cache_filename}.tmp.{_random_string(8)}'
            shutil.copyfile(filename, tmp_filename)
            try:
                os.rename(tmp_filename, filename)
                # _chmod_file(filename)
            except: # noqa
                if not os.path.exists(cache_filename):
                    raise Exception(f'Problem renaming file: {tmp_filename} {filename}')

    return uri
