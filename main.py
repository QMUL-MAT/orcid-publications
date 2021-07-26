"""
This script fetches ORCID IDs from the students' profiles on
github.com/QMUL-MAT/gatsby-mat and for each student generates
a bibtex file with their publications. Output is written to
a `public` directory at the current working directory.
"""
import pathlib
from typing import Generator, List, Tuple

import frontmatter
import requests

STUDENTS_URL = "https://api.github.com/repos/QMUL-MAT/gatsby-mat/contents/src/content/students"
ORCID_BASE_URL = "http://orcid.org"
ORCID_HEADERS = {"Accept": "application/orcid+json"}
OUTPUT_DIR = pathlib.Path("public")


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


def extract_slug(url: str) -> str:
    _, filename = url.rsplit("/", maxsplit=1)
    return filename.split(".", maxsplit=1)[0]


def students_gen() -> Generator[dict, None, None]:
    """Yield students' metadata (frontmatter) from the gatsby-mat repo."""
    students = get_json(STUDENTS_URL)
    file_urls = [x["download_url"] for x in students]
    markdown_urls = [x for x in file_urls if x.endswith(".md")]
    for markdown_url in markdown_urls:
        resp = requests.get(markdown_url)
        assert resp.status_code == 200, resp.status_code
        metadata, _ = frontmatter.parse(resp.content)
        metadata["slug"] = extract_slug(markdown_url)
        yield metadata


def index_content(output_dir):
    """Generate an index.html file."""
    parts = [
        "<h1>MAT students' publications</h1>",
        "<ul>"
    ]
    for filename in output_dir.iterdir():
        if filename.name != 'index.html':
            parts.append(
                f"<li><a href={filename.name}>{filename.name}</a></li>"
            )
    parts.append("</ul>")
    return '\n'.join(parts)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    for student in students_gen():
        if "orcid_id" in student:
            with open(OUTPUT_DIR / (student["slug"] + ".bib"), "w") as f:
                for citation in citations_gen(student["orcid_id"]):
                    print(citation, file=f)
    with open(OUTPUT_DIR / 'index.html', 'w') as f:
        f.write(index_content(OUTPUT_DIR))