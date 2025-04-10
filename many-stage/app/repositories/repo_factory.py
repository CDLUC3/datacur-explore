from app.repositories.dryad_api import DryadApi
from app.repositories.zenodo_api import ZenodoApi


# import repo_factory
# repo = repo_factory.repo_factory('10.5281/zenodo.13713417')
# repo.get_metadata()
# repo.get_filenames_and_links()
# repo.id_exists()

def repo_factory(doi):
    if "dryad" in doi:
        return DryadApi(doi)
    elif "zenodo" in doi:
        return ZenodoApi(doi)
    else:
        my_class = DryadApi(doi)
        if my_class.id_exists():
            return my_class
        else:
            my_class = ZenodoApi(doi)
            if my_class.id_exists():
                return my_class
        raise ValueError(f"Unknown repository for DOI: {doi}")