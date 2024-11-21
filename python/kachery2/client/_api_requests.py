def _initiate_file_upload_request(*, size: int, hash_alg: str, hash: str, zone: str) -> dict:
    payload = {
        'type': 'initiateFileUploadRequest',
        'size': size,
        'hashAlg': hash_alg,
        'hash': hash,
        'zoneName': zone
    }
    FINISH


def _finalize_file_upload_request(*, object_key: str, hash_alg: str, hash0: str, kachery_zone: str, size: int) -> dict:
    payload = {
        'type': 'finalizeFileUploadRequest',
        'objectKey': object_key,
        'hashAlg': hash_alg,
        'hash': hash0,
        'zoneName': kachery_zone,
        'size': size
    }
    FINISH


def find_file_request(*, hash_alg: str, hash: str, zone: str) -> dict:
    payload = {
        'type': 'findFileRequest',
        'hashAlg': hash_alg,
        'hash': hash,
        'zoneName': zone
    }
    FINISH
