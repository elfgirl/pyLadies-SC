import json
from unittest import TestCase
from unittest import mock
from unittest.mock import MagicMock

import requests
from requests import HTTPError

from Utility import Utility


class TestUtility(TestCase):

    # https://pypi.org/project/requests-mock/
    # https://realpython.com/testing-third-party-apis-with-mocks/

    def setUp(self):
        self.utility = Utility()

    def test_read_file(self):

        self.utility.read_file = MagicMock(return_value='Foo')
        results = self.utility.read_file("Non-ExistentFile.csv")

        self.assertEqual(results, 'Foo', 'Read CSV Failed')
        self.utility.read_file.assert_called_once()

    # Eh Test but it masks the WHOLE function. Not the actual external interaction

    @mock.patch("builtins.open", create=True)
    def test_read_file_better(self, mock_open):
        mock_open.side_effect = [
            mock.mock_open(read_data="Lorem Ipsum Sum").return_value,
            mock.mock_open(read_data="Sum Ipsum Lorem").return_value
        ]

        first_results = self.utility.read_file('Foo.txt')
        second_results = self.utility.read_file('Oof.txt')
        self.assertEqual(first_results, "Lorem Ipsum Sum")
        self.assertEqual(second_results, "Sum Ipsum Lorem")

        calls = [mock.call('Foo.txt', 'r'),
                 mock.call('Oof.txt', 'r')]

        mock_open.assert_has_calls(calls=calls)

    @mock.patch.object(requests, 'post')
    def test_new_user_post(self, mock_post):
        mock_response = MagicMock()
        mock_response.text = r'{"userId": "031411"}'
        mock_response.status_code = '200'

        mock_post.return_value = mock_response

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Alice'})

        self.assertEqual(id, '031411')

    def test_get_first_but_not_all(self):
        with mock.patch('requests.get') as mock_once:
            mock_response = MagicMock()
            mock_response.text = "No Relevant Results Found"

            mock_once.return_value = mock_response
            results = self.utility.get_api('http://www.bing.com')

        live_results = self.utility.get_api('http://www.google.com')

        self.assertTrue(True)

    @mock.patch.object(requests, 'post')
    def test_new_user_post_multiple(self, mock_post):

        data = [(json.dumps({'userId': '031234'}), '200'),
                (json.dumps({'userId': '474332'}), '200'),
                (json.dumps({'userId': ''}), '404')  # Gotcha with Mocks!!
                ]
        mock_responses = []
        for datum in data:
            mock_response = MagicMock(requests.Response)
            mock_response.text = datum[0]
            mock_response.status_code = datum[1]
            mock_responses.append(mock_response)

        mock_post.side_effect = mock_responses

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Alice'})
        self.assertEqual(id, '031234')

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Betty'})
        self.assertEqual(id, '474332')

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Carol'})
        self.assertEqual(id, '')

    @mock.patch.object(requests, 'post')
    def test_new_user_post_multiple_fixed(self, mock_post):

        data = [(json.dumps({'userId': '031234'}), '200', lambda: None),
                (json.dumps({'userId': '474332'}), '200', lambda: None),
                (json.dumps({'userId': ''}), '404', HTTPError("Raise it"))  # Fixed Gotcha with Mocks!!
                ]
        mock_responses = []
        for datum in data:
            mock_response = MagicMock(requests.Response)
            mock_response.text = datum[0]
            mock_response.status_code = datum[1]
            mock_response.raise_for_status.side_effect = datum[2]
            mock_responses.append(mock_response)

        mock_post.side_effect = mock_responses

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Alice'})
        self.assertEqual(id, '031234')

        id = self.utility.new_user('http://does.not.matter/userId', data={'Name': 'Betty'})
        self.assertEqual(id, '474332')

        self.assertRaises(HTTPError, self.utility.new_user, 'http://does.not.matter/userId', {'Name': 'Carol'})


raise_for_status = HTTPError("google is down")
