"""
This script fetches ORCID IDs from the students' profiles on
github.com/QMUL-MAT/gatsby-mat and for each student generates
a bibtex file with their publications. Output is written to
a `public` directory at the current working directory.
"""
import pathlib
from typing import Generator, List

import frontmatter
import requests

STUDENTS_URL = "https://api.github.com/repos/QMUL-MAT/gatsby-mat/contents/src/content/students"
ORCID_BASE_URL = "http://orcid.org"
ORCID_HEADERS = {"Accept": "application/orcid+json"}
OUTPUT_DIR = pathlib.Path('public')


def get_json(url: str, **kwargs) -> dict:
    """Wrapper around `requests.get`."""
    resp = requests.get(url, **kwargs)
    assert resp.status_code == 200, resp.status_code
    return resp.json()


def orcid(path: str) -> dict:
    """Retrieve data from the ORCID API."""
    return get_json(ORCID_BASE_URL + path, headers=ORCID_HEADERS)


def citations_gen(orcid_id: str) -> List[str]:
    """Retrieve bibtex entries of an ORCID author."""
    author = orcid(f"/{orcid_id}/works")
    for work in author["group"]:
        work_path = work["work-summary"][0]["path"]
        work_details = orcid(work_path)
        citation = work_details["citation"]
        if citation["citation-type"] == "bibtex":
            yield citation["citation-value"].strip()


def students_orcid_ids_gen() -> Generator[str]:
    """
    Yield ORCID IDs from students' profile from the
    gatsby-mat repo.
    """
    students = get_json(STUDENTS_URL)
    file_urls = [x["download_url"] for x in students]
    markdown_urls = [x for x in file_urls if x.endswith('.md')]
    for markdown_url in markdown_urls:
        resp = requests.get(markdown_url)
        assert resp.status_code == 200, resp.status_code
        metadata, _ = frontmatter.parse(resp.content)
        if 'orcid_id' in metadata:
            yield metadata['orcid_id']


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    for orcid_id in students_orcid_ids_gen():
        with open(OUTPUT_DIR / (orcid_id + '.md'), 'w') as f:
            for citation in citations_gen(orcid_id):
                print(citation, file=f)
