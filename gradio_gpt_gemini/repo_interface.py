from abc import ABC, abstractmethod


class RepoInterface(ABC):
    @abstractmethod
    def id_exists(self):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

    @abstractmethod
    def get_filenames_and_links(self):
        pass

    @staticmethod
    def _fix_format_of_doi(string):
        dryad_prefix = "https://datadryad.org/stash/dataset/doi:"
        doi_prefix = "https://doi.org/"
        zen_record = "https://zenodo.org/records/"
        if string.startswith(dryad_prefix):
            return string[len(dryad_prefix):]
        elif string.startswith(doi_prefix):
            return string[len(doi_prefix):]
        elif string.startswith("https://doi.org/"):
            return string[len("https://doi.org/"):]
        elif string.startswith(zen_record):
            # this one is a bit sketchy
            return f"10.5281/zenodo.{string[len(zen_record):]}"
        elif string.startswith("doi:"):
            return string[len("doi:"):]
        return string