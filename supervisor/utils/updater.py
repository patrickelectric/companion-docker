import json
import docker
from .dockerhub import TagFetcher

class Updater:
    all_versions: dict
    tag_fetcher: TagFetcher

    def __init__(self):
        self.all_versions = {}
        self.tag_fetcher = TagFetcher()

    def fetch_available_versions(self):
        # TODO: load from url
        with open("versions.json") as config_file:
            versions = json.load(config_file)
            self.all_versions = versions

    def is_update_available(self):
        self.fetch_available_versions()
        
        for version, version_config in self.all_versions.items():
            missing = False
            for docker, config in version_config["dockers"].items():
                if not config["tag"] in self.tag_fetcher.fetch_versions(config["image"]):
                    missing = True
            self.all_versions[version]["available"] = not missing
            print(version, "available" if not missing else "unavailable")

if __name__ == "__main__":
    Updater().is_update_available()
