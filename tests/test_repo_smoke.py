"""Repository smoke tests for the one-python-craftsman content tree."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ZH_CN_DIR = REPO_ROOT / "zh_CN"
README_PATH = REPO_ROOT / "README.md"

EXPECTED_ARTICLE_COUNT = 16
ARTICLE_FILENAME_PATTERN = re.compile(r"^\d+-.+\.md$")


@pytest.fixture(scope="module")
def readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def test_license_present() -> None:
    assert (REPO_ROOT / "LICENSE").is_file()


def test_zh_cn_directory_has_sixteen_articles() -> None:
    articles = sorted(ZH_CN_DIR.glob("*.md"))
    assert len(articles) == EXPECTED_ARTICLE_COUNT, (
        f"expected {EXPECTED_ARTICLE_COUNT} articles, found {len(articles)}: "
        f"{[p.name for p in articles]}"
    )


def test_article_filenames_follow_numbered_pattern() -> None:
    for path in sorted(ZH_CN_DIR.glob("*.md")):
        assert ARTICLE_FILENAME_PATTERN.match(path.name), path.name


def _has_markdown_heading(text: str) -> bool:
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{1,6}\s+\S", line):
            return True
    return False


@pytest.mark.parametrize(
    "path",
    sorted(ZH_CN_DIR.glob("*.md")),
    ids=lambda p: p.name,
)
def test_article_has_title_and_body(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert len(text.strip()) > 200, f"{path.name} looks too short"
    assert _has_markdown_heading(text), f"{path.name} should contain a markdown heading"


def test_readme_local_markdown_links_resolve(readme_text: str) -> None:
    links = re.findall(r"\]\((zh_CN/[^)]+\.md)\)", readme_text)
    assert links, "README should link to at least one zh_CN article"
    missing = [link for link in sorted(set(links)) if not (REPO_ROOT / link).is_file()]
    assert not missing, f"broken README links: {missing}"


def test_readme_links_cover_all_articles(readme_text: str) -> None:
    linked = set(re.findall(r"\]\((zh_CN/[^)]+\.md)\)", readme_text))
    on_disk = {f"zh_CN/{path.name}" for path in sorted(ZH_CN_DIR.glob("*.md"))}
    not_linked = sorted(on_disk - linked)
    assert not not_linked, f"articles not linked from README: {not_linked}"
