import glob
import winreg
import re

class DownloadError(Exception):
    pass

class FileFound(Exception):
    pass

def get_key():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam")
    return key

def get_steam_path():
    i = 0
    reg_key = get_key()
    while True:
        try:
            path = winreg.EnumValue(reg_key, i)
            if "SteamPath" == path[0]:
                winreg.CloseKey(reg_key)
                return path[1]
        except OSError:
            break
        i += 1
    winreg.CloseKey(reg_key)

def get_lib_path(steam_path):
    """This function will return ALL the existing library paths from steam."""
    lib_path = glob.glob(f"{steam_path}/steamapps/libraryfolders.vdf")
    i = 0
    paths = {}
    with open(lib_path[0], "r") as f:
        for line in f:
            try:
                conjunto = re.findall(r'"([^"]+)"',line)
                if "path" == conjunto[0]:
                    paths[i] = conjunto[1]
                    i+= 1
            except IndexError:
                continue 
    return paths   

def get_manifests(lib_paths):
    """This function retrieves the appmanifests.acf paths"""
    archive_paths= []
    for p in lib_paths.values():
        current_archive_paths = glob.glob(f"{p}/steamapps/appmanifest_*.acf")
        for a_paths in current_archive_paths:
            archive_paths.append(a_paths)
    return archive_paths

def get_download_data(manifests): 
    """This function will return the downloaded bytes, bytes to download and the appid"""
    
    for archive in manifests:
        manifest_data = {}
        try:
            with open(archive, "r") as a:
                for line in a:
                    try:
                        elem = re.findall(r'"([^"]+)"',line)
                        if "appid" == elem[0]:
                            manifest_data["appid"] = elem[1]
                        if "BytesToDownload" == elem[0]:
                            manifest_data["btd"] = float(elem[1])
                        elif "BytesDownloaded" == elem[0]:
                            manifest_data["bd"] = float(elem[1])
                    except IndexError:
                        continue
                try:
                    if manifest_data["bd"] != manifest_data["btd"]:
                        raise FileFound
                except KeyError:
                    raise KeyError("There was a missing key in the app manifest.")
        except FileFound:
            return manifest_data
        except KeyError:
            continue
    return DownloadError("There wasn't an active download")

