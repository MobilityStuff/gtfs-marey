import logging
import shutil
from os import path

import filetype
import partridge as ptg
import pyrfc6266
import requests

from .utils import DIRS, is_valid_url

logger = logging.getLogger(__name__)


class Feed:
    def __init__(self, source_path: str, route_names: str):
        self.source_path: str = source_path
        self.route_names: str = route_names

        self.feed_name: str = source_path.rpartition("/")[-1].rpartition(".")[:-2][0]
        self.designated_path: str = f"{DIRS['ASSETS']}/{self.feed_name}"
        self.feed = None

    def _locate(self) -> str:
        """Proceed to locate the feed in the file system.

        If the path is a valid url, the feed is downloaded from the net

        Returns the feed path, or throws ValueError in case of error
        """
        if path.exists(self.source_path):
            return self.source_path

        if path.exists(self.designated_path):
            return self.designated_path
        elif is_valid_url(self.source_path):
            logger.info(f"Downloading feed from {self.source_path}")
            response = requests.get(self.source_path, stream=True, verify=False)

            if not response.headers["content-type"] == "application/zip":
                raise ValueError(
                    f"Expected a zip file to download, found {response.headers['content-type']}"
                )
            file_name = pyrfc6266.requests_response_to_filename(response)
            designated_path = f"{DIRS['ASSETS']}/{file_name}"

            if path.exists(
                designated_path
            ):  # The feed was already downloaded. Keep the local version
                response.close()
            else:
                with open(designated_path, "wb") as zip:
                    zip.write(response.content)

            return designated_path
        else:
            raise ValueError(f"Inexisting path {self.source_path}")

    def _unzip(self, given_path) -> str:
        """Extract the zip file into a folder"""
        if path.isdir(given_path):  # Already extracted
            return given_path
        elif filetype.guess(given_path).mime == "application/zip":
            designated_path = f"{DIRS['ASSETS']}/{self.feed_name}"
            shutil.unpack_archive(given_path, designated_path)
            return designated_path
        else:
            raise ValueError(f"Inexisting path or not a zip file {path}")

    def get(self):
        """Load the GTFS feed in memory and choose the route numbers as given in input"""
        if not self.feed == None:
            return self.feed

        view = {
            "routes.txt": {"route_short_name": self.route_names},
        }
        designated_path = self._locate()
        feed_folder = self._unzip(designated_path)
        self.feed = ptg.load_feed(feed_folder, view)

        return self.feed
