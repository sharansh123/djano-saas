import requests
from pathlib import Path

def download_to_local(url:str, out_path:Path, parent_mk_dir:bool = True):
    if not isinstance(out_path,Path):
        raise ValueError()
    if parent_mk_dir:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        out_path.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        print(f'failed to download file from {url}: {e}')
        return False
