# Minecraft Mod Updater

A Python script to automatically update Minecraft mods using Modrinth APIs.

## Lore

After spending too much time manually updating Minecraft mods on an Ubuntu Server machine, I decided to create a Python script to automate the process. This script scans the mods directory, checks for updates using the Modrinth API, and downloads the latest versions of the mods.

It also has a backup feature to save the current mods before updating, ensuring that you can revert to the previous versions if needed.

The script works both on Windows and Linux systems, both for client and server setups. However, for client setups, I suggest using a launcher like Prism, which has built-in mod management features.

## How to use

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python updateMods.py
   ```

Command-line arguments can be added to specify the mods directory, Minecraft version, loader type, and the backup directory.

- `-v`, `--Version`: Specify the Minecraft version
- `-l`, `--Loader`: Specify the mod loader (fabric, forge, etc.)
- `-d`, `--Directory`: Specify the directory where mods are located 
- `-b`, `--Backup`: Specify the backup directory

Example with arguments:
```bash
python updateMods.py -v 1.21.8 -l fabric -m "C:\Users\Bob\AppData\Roaming\PrismLauncher\instances\1.21.8\minecraft\mods" -b "C:\Users\Bob\AppData\Roaming\PrismLauncher\instances\1.21.8\minecraft\mods\backup"
```

To set default values, create a `.env` file in the same directory as the script with the following content:

```
MODS_DIR=path_to_your_mods_directory
MINECRAFT_VERSION=your_minecraft_version
LOADER=your_mod_loader
```

Example `.env` file:
```
MODS_DIR=C:\Users\Bob\AppData\Roaming\PrismLauncher\instances\1.21.8\minecraft\mods
MINECRAFT_VERSION=1.21.8
LOADER=fabric
``` 
