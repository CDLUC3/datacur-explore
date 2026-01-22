import unittest
from app.repositories.repo_interface import RepoInterface


class TestFixFormatOfDoi(unittest.TestCase):
    def test_plain_doi(self):
        inp = "doi:10.5061/dryad.69p8cz920"
        out = RepoInterface._fix_format_of_doi(inp)
        self.assertEqual(out, "10.5061/dryad.69p8cz920")

    def test_datadryad_dataset_doi(self):
        inp = "https://datadryad.org/dataset/doi:10.5061/dryad.69p8cz920"
        out = RepoInterface._fix_format_of_doi(inp)
        self.assertEqual(out, "10.5061/dryad.69p8cz920")

    def test_datadryad_stash_doi(self):
        inp = "https://datadryad.org/stash/dataset/doi:10.5061/dryad.69p8cz920"
        out = RepoInterface._fix_format_of_doi(inp)
        self.assertEqual(out, "10.5061/dryad.69p8cz920")

    def test_doi_org(self):
        inp = "https://doi.org/10.5061/dryad.69p8cz920"
        out = RepoInterface._fix_format_of_doi(inp)
        self.assertEqual(out, "10.5061/dryad.69p8cz920")

    def test_zenodo(self):
        inp = "https://zenodo.org/records/13713417"
        out = RepoInterface._fix_format_of_doi(inp)
        self.assertEqual(out, "10.5281/zenodo.13713417")


if __name__ == "__main__":
    unittest.main()
