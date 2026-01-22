import unittest
from unittest.mock import patch, Mock
import urllib.parse
from app.repositories.dryad_api import DryadApi, BASE_URL


class TestDryadApi(unittest.TestCase):
    @patch('app.repositories.dryad_api.requests.get')
    def test_get_metadata_success_and_url(self, mock_get):
        # Setup mock response for the metadata call
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'id': 'test', 'title': 'Test Dataset'}
        mock_get.return_value = mock_resp

        da = DryadApi('https://datadryad.org/dataset/doi:10.5061/dryad.69p8cz920')
        meta = da.get_metadata()

        # Ensure metadata returned
        self.assertIsNotNone(meta)
        self.assertEqual(meta['id'], 'test')

        # Ensure requests.get was called with the expected URL containing the encoded DOI
        called_url = mock_get.call_args[0][0]
        expected = f"{BASE_URL}/api/v2/datasets/doi:{urllib.parse.quote('10.5061/dryad.69p8cz920', safe='')}"
        self.assertEqual(called_url, expected)

    @patch('app.repositories.dryad_api.requests.get')
    def test_get_metadata_not_found(self, mock_get):
        # 404 should result in None
        mock_resp = Mock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        da = DryadApi('10.5061/dryad.69p8cz920')
        meta = da.get_metadata()
        self.assertIsNone(meta)


if __name__ == '__main__':
    unittest.main()
