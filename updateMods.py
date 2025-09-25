import os, requests, shutil, hashlib, argparse, dotenv

dotenv.load_dotenv()

MODS_DIR = os.getenv("MODS_DIR", "")
MINECRAFT_VERSION = os.getenv("MINECRAFT_VERSION", "")
LOADER = os.getenv("LOADER", "")
BACKUP_DIR = os.path.join(MODS_DIR, "backup")

parser = argparse.ArgumentParser(description="Minecraft Mod Updater")
parser.add_argument("-v", "--Version", default=MINECRAFT_VERSION, help="Minecraft version")
parser.add_argument("-l", "--Loader", default=LOADER, help="Mod loader")
parser.add_argument("-d", "--Directory", default=MODS_DIR, help="Mods directory")
parser.add_argument("-b", "--Backup", default=BACKUP_DIR, help="Backup directory")
args = parser.parse_args()

MINECRAFT_VERSION = args.Version
LOADER = args.Loader
MODS_DIR = args.Directory
BACKUP_DIR = args.Backup

# Modrinth API endpoint to get project info from a file hash
GET_PROJECT_FROM_HASH = 'https://api.modrinth.com/v2/version_file/{}/update?algorithm=sha512'

# Compute SHA-512 hash of a file
def sha512sum(filename, chunk_size=8192):
    sha512 = hashlib.sha512()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha512.update(chunk)
    return sha512.hexdigest()

# Get project information from Modrinth using the file hash
def get_project(hash):
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

# Download the mod .jar file from Modrinth
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
        hash = sha512sum(mod_path)
        project = get_project(hash)
        
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
