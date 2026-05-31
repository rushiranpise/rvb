import tomllib
import json
import urllib.parse
import re

CONFIG_FILE = "config.toml"
OUTPUT_FILE = "README.md"

REPO_URL = "https://github.com/rushiranpise/rvb"
AUTHOR = "rushiranpise"

BASE_OBTAINIUM_URL = (
    "https://apps.obtainium.imranr.dev/redirect?r=obtainium://app/"
)

def prettify_name(section_name):
    name = section_name.replace("-Morphe", "")
    name = name.replace("-", " ")

    if name.startswith("Google "):
        name = name.replace("Google ", "")

    if name == "Music":
        name = "YouTube Music"

    return name

def slugify(text):
    return (
        text.lower()
        .replace(" ", "-")
        .replace("+", "plus")
    )

def generate_regex(section_name):
    slug = slugify(section_name)
    return f"^{slug}-morphe-v?\\d.*\\.apk$"

def extract_package_names(config_text):
    package_map = {}

    current_section = None

    for line in config_text.splitlines():

        line = line.strip()

        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            continue

        match = re.match(
            r"#\s*package-name\s*=\s*(.+)",
            line
        )

        if match and current_section:
            package_name = match.group(1).strip()

            package_name = package_name.replace(
                "com.google.android.",
                "app.morphe.android."
            )

            package_map[current_section] = package_name

    return package_map

def generate_obtainium_link(
    display_name,
    regex,
    package_name,
):
    payload = {
        "id": package_name,
        "url": REPO_URL,
        "author": AUTHOR,
        "name": display_name,
        "preferredApkIndex": 0,
        "additionalSettings": json.dumps({
            "includePrereleases": False,
            "fallbackToOlderReleases": True,
            "filterReleaseTitlesByRegEx": "",
            "filterReleaseNotesByRegEx": "",
            "verifyLatestTag": False,
            "sortMethodChoice": "date",
            "useLatestAssetDateAsReleaseDate": False,
            "releaseTitleAsVersion": False,
            "trackOnly": False,
            "versionExtractionRegEx": "",
            "matchGroupToUse": "",
            "versionDetection": False,
            "releaseDateAsVersion": False,
            "useVersionCodeAsOSVersion": False,
            "apkFilterRegEx": regex,
            "invertAPKFilter": False,
            "autoApkFilterByArch": True,
            "appName": "",
            "appAuthor": "",
            "shizukuPretendToBeGooglePlay": False,
            "allowInsecure": False,
            "exemptFromBackgroundUpdates": False,
            "skipUpdateNotifications": False,
            "about": "",
            "refreshBeforeDownload": False,
            "includeZips": False,
            "zippedApkFilterRegEx": ""
        }),
        "overrideSource": "GitHub"
    }

    encoded = urllib.parse.quote(json.dumps(payload))
    return BASE_OBTAINIUM_URL + encoded

def main():

    with open(CONFIG_FILE, "rb") as f:
        data = tomllib.load(f)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config_text = f.read()

    package_names = extract_package_names(config_text)

    lines = []

    lines.append("# Install With Obtainium\n")

    count = 1

    for section_name, values in data.items():

        if not values.get("enabled", False):
            continue

        display_name = prettify_name(section_name)

        regex = generate_regex(section_name)

        package_name = package_names.get(section_name, "")

        obtainium_link = generate_obtainium_link(
            display_name,
            regex,
            package_name,
        )

        lines.append(
            f"{count}. {display_name} "
            f"[![Add to Obtainium]"
            f"(https://img.shields.io/badge/Add_to-Obtainium-4500FF?logo=obtainium)]"
            f"({obtainium_link})\n"
        )

        count += 1

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write("\n".join(lines))

    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()