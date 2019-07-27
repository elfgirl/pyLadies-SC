import requests
import json

class Utility :

    def read_file(self, filename):
        with open(filename, 'r') as open_file :
            return open_file.readline()

    def get_api(self, uri):
        results = requests.get(uri)
        results.raise_for_status()
        return results.text

    def new_user(self, uri, data):
        results = requests.post(uri, data)
        results.raise_for_status()

        # Do something with results
        user_results = json.loads(results.text)

        # Return transformation
        return user_results['userId']
