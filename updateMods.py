import os
import requests
import shutil
import zipfile
import json
import urllib.parse

MODS_DIR = "./mods"
MINECRAFT_VERSION = "1.21.8"
LOADER = "fabric"
BACKUP_DIR = os.path.join(MODS_DIR, "backup")

SEARCH_PROJECT = 'https://api.modrinth.com/v2/search?query={}&facets=[["versions:{}"],["categories:{}"]]'
API_VERSIONS = 'https://api.modrinth.com/v2/project/{}/version?game_versions=["{}"]&loaders=["{}"]'

def search_project(name):
    url = SEARCH_PROJECT.format(urllib.parse.quote(name), MINECRAFT_VERSION, LOADER)
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        projects = r.json()
        if not projects:
            return None
        return projects["hits"]
    except Exception:
        return None

# Extract mod names from fabric.mod.json inside the jar
def get_mod_names_from_jar(jar_path):
    try:
        with zipfile.ZipFile(jar_path, "r") as jar:
            if "fabric.mod.json" not in jar.namelist():
                return None
            with jar.open("fabric.mod.json") as f:
                data = json.load(f)
                project = search_project(data.get("name"))
                projectId = project[0]["project_id"] if project else None
                return [data.get("id"), data.get("name").replace(" ", "-"), projectId]
    except Exception as e:
        print(f" Could not read {jar_path}: {e}")
        return None

# Get the latest version of a mod from Modrinth
def get_latest_version(project_slug):
    url = API_VERSIONS.format(project_slug, MINECRAFT_VERSION, LOADER)
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        versions = r.json()
        if not versions:
            return None
        return versions[0]
    except Exception:
        return None

# Download the mod file from Modrinth
def download_mod(version, target_path):
    files = version.get("files", [])
    for f in files:
        if f["filename"].endswith(".jar"):
            url = f["url"]
            print(f" ⬇️ Downloading {f['filename']}...")
            r = requests.get(url, stream=True)
            with open(target_path, "wb") as out:
                shutil.copyfileobj(r.raw, out)
            return f["filename"]
    return None


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for mod in os.listdir(MODS_DIR):
        if not mod.endswith(".jar"):
            continue

        mod_path = os.path.join(MODS_DIR, mod)
        project_names = get_mod_names_from_jar(mod_path)
        print(f"\n{project_names}")

        if not project_names:
            print(f"\nSkipping {mod} (no fabric.mod.json)")
            continue

        version = None
        for n in project_names:
            version = get_latest_version(n)
            if version:
                break

        print(f"\nChecking {mod}...")
        if not version:
            print(" Could not find project/version on Modrinth.")
            continue

        latest_filename = version["files"][0]["filename"]
        if latest_filename == mod:
            print(" Already up to date.")
            continue

        print(f" Update found: {latest_filename}")
        backup_path = os.path.join(BACKUP_DIR, mod)
        shutil.move(mod_path, backup_path)
        print(f"   Backed up old mod to {backup_path}")

        new_mod_path = os.path.join(MODS_DIR, latest_filename)
        downloaded = download_mod(version, new_mod_path)
        if downloaded:
            print(f"   Installed {downloaded}")
        else:
            print(" Failed to download new version.")


if __name__ == "__main__":
    main()
