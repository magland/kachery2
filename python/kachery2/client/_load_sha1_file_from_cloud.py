from typing import Union
import os
import shutil
import requests
from .get_kachery2_dir import get_kachery2_dir
from ._random_string import _random_string
from ._api_requests import find_file_request


def _load_sha1_file_from_cloud(sha1: str, *, verbose: bool, dest: Union[None, str] = None, _get_info: bool = False) -> Union[str, dict, None]:
    kachery_zone = os.environ.get('KACHERY_ZONE', 'default')

    response = find_file_request(hash_alg='sha1', hash=sha1, zone=kachery_zone)

    found = response['found']
    uri = f'sha1://{sha1}'
    if found:
        url = response['url']
    else:
        return None

    if _get_info:
        # we don't want the user to get the idea they should use the URL directly!
        del response['url']
        return response

    kachery_cloud_dir = get_kachery2_dir()
    e = sha1
    parent_dir = f'{kachery_cloud_dir}/sha1/{e[0]}{e[1]}/{e[2]}{e[3]}/{e[4]}{e[5]}'
    filename = f'{parent_dir}/{sha1}'
    if verbose:
        print(f'Loading file from kachery cloud: {uri}')
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    tmp_filename = f'{filename}.tmp.{_random_string(8)}'
    with requests.get(url, stream=True) as r:
        if r.status_code == 404:
            raise Exception(f'Unexpected: file not found in bucket: {url}')
        r.raise_for_status()
        with open(tmp_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    try:
        os.rename(tmp_filename, filename)
        # _chmod_file(filename)
    except Exception:
        if not os.path.exists(filename): # maybe some other process beat us to it
            raise Exception(f'Unexpected problem moving file {tmp_filename}')
    if dest is not None:
        shutil.copyfile(filename, dest)
        return dest
    return filename
