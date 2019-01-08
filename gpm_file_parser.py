import csv
import html
import json
import logging


class Song:
    def __init__(self, title, artist, album):
        self._title = title
        self._artist = artist
        self._album = album

    def __str__(self):
        return f"{self._title} - {self._album} by {self._artist}"


    @property
    def title(self):
        return self._title


    @property
    def artist(self):
        return self._artist


    @property
    def album(self):
        return self._album


class GpmFileParser:
    
    def _csv2json(self, csv_file):
        """Converts a CSV file to JSON object
        :param csv_file: String, File Path to the CSV file

        :returns: JSON Object

        """
        with open(csv_file, "r") as csv_file_handle:
            reader = csv.DictReader(csv_file_handle)
            return json.dumps([row for row in reader])


    def parse_file(self, csv_file):
        try:
            song = self._csv2json(csv_file)
            song = json.loads(song)[0]

            return Song(
                    html.unescape(song["Title"]), 
                    html.unescape(song["Artist"]), 
                    html.unescape(song["Album"])
                )
        
        except Exception as e:
            logging.exception(f"Can't parse {csv_file}")
