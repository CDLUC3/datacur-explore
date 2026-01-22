from abc import ABC, abstractmethod
import urllib.parse


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
        # make parsing robust to different URL shapes and prefixes
        if not string:
            return string

        s = string.strip()

        # If this looks like a URL, try to parse common cases
        try:
            parsed = urllib.parse.urlparse(s)
        except Exception:
            parsed = None

        if parsed and parsed.scheme in ("http", "https"):
            netloc = parsed.netloc.lower()
            path = parsed.path or ""

            # Handle datadryad.org URLs (both /stash/dataset/doi:... and /dataset/doi:... and /dataset/<doi>)
            if netloc.endswith('datadryad.org'):
                # If path contains 'doi:' anywhere, return everything after it (preserve slashes)
                idx = path.find('doi:')
                if idx != -1:
                    return path[idx + len('doi:'):].lstrip('/')

                # split the path into non-empty segments
                segments = [seg for seg in path.split('/') if seg]

                # Otherwise, look for a segment that looks like a DOI (commonly starts with '10.')
                for seg in reversed(segments):
                    if seg.startswith('10.'):
                        return seg

            # Handle doi.org URLs: https://doi.org/10.x/...
            if netloc.endswith('doi.org'):
                return path.lstrip('/')

            # Handle zenodo record URLs like https://zenodo.org/records/<id>
            if netloc.endswith('zenodo.org'):
                zen_prefix = '/records/'
                if path.startswith(zen_prefix):
                    rec = path[len(zen_prefix):].lstrip('/')
                    return f"10.5281/zenodo.{rec}"

        # Fallbacks for common prefixes (keep compatibility with older code)
        dryad_prefix = "https://datadryad.org/stash/dataset/doi:"
        alt_dryad_prefix = "https://datadryad.org/dataset/doi:"
        doi_prefix = "https://doi.org/"
        zen_record = "https://zenodo.org/records/"
        if s.startswith(dryad_prefix):
            return s[len(dryad_prefix):]
        elif s.startswith(alt_dryad_prefix):
            return s[len(alt_dryad_prefix):]
        elif s.startswith(doi_prefix):
            return s[len(doi_prefix):]
        elif s.startswith(zen_record):
            # this one is a bit sketchy but preserved for compatibility
            return f"10.5281/zenodo.{s[len(zen_record):]}"
        elif s.startswith("doi:"):
            return s[len("doi:"):]

        return s
