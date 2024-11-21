import os


def get_kachery2_dir(*, respect_sandbox: bool = True):
    from pathlib import Path
    if respect_sandbox and (os.getenv('KACHERY2_USE_SANDBOX', '') == '1'):
        return os.environ['KACHERY2_SANDBOX_DIR']
    homedir = str(Path.home())
    hsd = os.getenv('KACHERY2_DIR', f'{homedir}/.kachery2')
    if not os.path.exists(hsd):
        os.makedirs(hsd)
    return hsd
