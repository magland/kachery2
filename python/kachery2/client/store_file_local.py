import os
import json
import shutil
from tempfile import TemporaryDirectory
from urllib.parse import quote
from typing import Union
from .get_kachery2_dir import get_kachery2_dir
from ._compute_file_hash import _compute_file_hash
from ._random_string import _random_string


def store_file_local(filename: str, *, label: Union[str, None] = None, store_file_dir: Union[str, None] = None, store_file_prefix: Union[str, None] = None):
    from .load_file import load_file
    if filename.startswith('sha1://'):
        a = load_file(filename)
        if a is None:
            raise Exception(f'Problem loading file: {filename}')
        filename = a
    if not os.path.isabs(filename):
        filename = os.path.abspath(filename)
    sha1 = _compute_file_hash(filename, algorithm='sha1')
    if store_file_prefix is None:
        uri = f'sha1://{sha1}'
    else:
        uri = f'{store_file_prefix}/sha1/{sha1}'
    if label is not None:
        uri = f'{uri}?label={quote(label)}'
    if store_file_dir is None:
        kachery2_dir = get_kachery2_dir()
        kachery_storage_parent_dir = f'{kachery2_dir}/sha1/{sha1[0]}{sha1[1]}/{sha1[2]}{sha1[3]}/{sha1[4]}{sha1[5]}'
        kachery_storage_file_name = f'{kachery_storage_parent_dir}/{sha1}'
    else:
        kachery_storage_parent_dir = f'{store_file_dir}/sha1'
        kachery_storage_file_name = f'{kachery_storage_parent_dir}/{sha1}'
    if not os.path.exists(kachery_storage_file_name):
        if not os.path.exists(kachery_storage_parent_dir):
            os.makedirs(kachery_storage_parent_dir)
        tmp_filename = f'{kachery_storage_file_name}.{_random_string(10)}'
        shutil.copyfile(filename, tmp_filename)
        try:
            os.rename(tmp_filename, kachery_storage_file_name)
            # _chmod_file(kachery_storage_file_name)
        except Exception:
            # Maybe another client renamed the file
            if not os.path.exists(kachery_storage_file_name):
                raise Exception(f'Unexpected problem renaming file: {tmp_filename} {kachery_storage_file_name}')
    return uri

def store_json_local(obj, *, label: Union[str, None] = None):
    with TemporaryDirectory() as tmpdir:
        fname = f'{tmpdir}/tmp.json'
        with open(fname, 'w') as f:
            json.dump(obj, f)
        return store_file_local(fname, label=label)
