import csv
import json

def csv2json(csv_file):
    """Converts a CSV file to JSON object
    :param csv_file: String, File Path to the CSV file

    :returns: JSON Object

    """
    with open(csv_file, "r") as csv_file_handle:
        reader = csv.DictReader(csv_file_handle)
        return json.dumps([row for row in reader])
