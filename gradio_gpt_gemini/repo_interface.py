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
