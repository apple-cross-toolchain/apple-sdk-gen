from __future__ import annotations

import logging
from dataclasses import dataclass

from .client import APIClient, BASE_URL

logger = logging.getLogger(__name__)


@dataclass
class FrameworkInfo:
    name: str
    doc_uri: str
    languages: list[str]
    group: str

    @property
    def has_objc(self) -> bool:
        return "occ" in self.languages

    @property
    def has_swift(self) -> bool:
        return "swift" in self.languages

    @property
    def module_name(self) -> str:
        """Extract the actual module name from the doc URI.

        e.g. doc://com.apple.imageio/documentation/ImageIO -> ImageIO
             doc://com.apple.documentation/documentation/Foundation -> Foundation
        """
        if "/documentation/" in self.doc_uri:
            path = self.doc_uri.split("/documentation/", 1)[1]
            # Take the first path component (module root)
            return path.split("/")[0]
        return self.name

    @property
    def doc_path(self) -> str:
        # doc://com.apple.documentation/documentation/Foundation
        # -> /documentation/Foundation
        if "/documentation/" in self.doc_uri:
            return "/documentation/" + self.doc_uri.split("/documentation/", 1)[1]
        return self.doc_uri


async def fetch_technologies(client: APIClient) -> list[FrameworkInfo]:
    url = f"{BASE_URL}/documentation/technologies.json"
    data = await client.fetch_json(url)
    if data is None:
        logger.error("Failed to fetch technologies.json")
        return []

    frameworks: list[FrameworkInfo] = []
    seen = set()

    for section in data.get("sections", []):
        groups = section.get("groups", [])
        # Some sections have technologies at top level
        if not groups and "technologies" in section:
            groups = [{"name": section.get("name", ""), "technologies": section["technologies"]}]

        for group in groups:
            group_name = group.get("name", "")
            for tech in group.get("technologies", []):
                title = tech.get("title", "")
                dest = tech.get("destination", {})
                identifier = dest.get("identifier", "")
                languages = tech.get("languages", [])

                # Skip external links and entries without language support
                if identifier.startswith("http"):
                    continue
                if not languages:
                    continue
                # Skip non-doc:// identifiers
                if not identifier.startswith("doc://"):
                    continue
                # Skip duplicates
                if identifier in seen:
                    continue
                seen.add(identifier)

                frameworks.append(FrameworkInfo(
                    name=title,
                    doc_uri=identifier,
                    languages=languages,
                    group=group_name,
                ))

    logger.info("Found %d frameworks", len(frameworks))
    return frameworks


def filter_frameworks(
    frameworks: list[FrameworkInfo],
    include: set[str] | None = None,
    exclude: set[str] | None = None,
    objc_only: bool = False,
) -> list[FrameworkInfo]:
    from ..config import NON_FRAMEWORK_MODULES

    result = []
    for fw in frameworks:
        names = {fw.name, fw.module_name}
        # Skip documentation topics, REST APIs, JS libs, etc.
        if fw.module_name in NON_FRAMEWORK_MODULES:
            continue
        if include and not names.intersection(include):
            continue
        if exclude and names.intersection(exclude):
            continue
        if objc_only and not fw.has_objc:
            continue
        result.append(fw)
    return result
