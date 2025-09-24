import os
import requests
import shutil
import hashlib

MODS_DIR = "C:\\Users\\Karim\\AppData\\Roaming\\.minecraft\\mods"
MINECRAFT_VERSION = "1.21.8"
LOADER = "fabric"
BACKUP_DIR = os.path.join(MODS_DIR, "backup")

GET_PROJECT_FROM_HASH = 'https://api.modrinth.com/v2/version_file/{}/update?algorithm=sha512'

def sha512sum(filename, chunk_size=8192):
    sha512 = hashlib.sha512()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha512.update(chunk)
    return sha512.hexdigest()

def get_project(jar_path):
    hash = sha512sum(jar_path)
    payload = {
        "loaders": [LOADER],
        "game_versions": [MINECRAFT_VERSION]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(GET_PROJECT_FROM_HASH.format(hash), json=payload, headers=headers)

    if response.status_code == 200:
        print('\nProject found!')
        return response.json()
    else:
        print(f"\nError {response.status_code}: {response.text}")

def download_mod(version, target_path):
    """Download the .jar file from Modrinth release files."""
    url = version["files"][0]["url"]
    print(f" Downloading {version['files'][0]['filename']}...")
    r = requests.get(url, stream=True)
    with open(target_path, "wb") as out:
        shutil.copyfileobj(r.raw, out)
    return version["files"][0]["filename"]

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for mod in os.listdir(MODS_DIR):
        if not mod.endswith(".jar"):
            continue

        mod_path = os.path.join(MODS_DIR, mod)
        project = get_project(mod_path)
        
        if not project:
            print(f" Skipping {mod}")
            continue

        latest_filename = project["files"][0]["filename"]
        print(f" Checking {mod}...")

        if latest_filename == mod:
            print(" Already up to date.")
            continue

        print(f" Update found: {latest_filename}")
        backup_path = os.path.join(BACKUP_DIR, mod)
        shutil.move(mod_path, backup_path)
        print(f"   Backed up old mod to {backup_path}")

        new_mod_path = os.path.join(MODS_DIR, latest_filename)
        downloaded = download_mod(project, new_mod_path)
        if downloaded:
            print(f"   Installed {downloaded}")
        else:
            print(" Failed to download new version.")


if __name__ == "__main__":
    main()
