from __future__ import annotations

import asyncio
import logging
from copy import deepcopy

from .client import APIClient
from .symbol import _apply_variant_overrides
from .technologies import FrameworkInfo

logger = logging.getLogger(__name__)

# Apple's CoreGraphics CGGeometry and transform topics link to these C
# declarations in the CoreFoundation documentation collection.
_CG_GEOMETRY_TOPICS = tuple(
    f"/documentation/corefoundation/{name}"
    for name in ("cgpoint", "cgsize", "cgrect", "cgrectedge", "cgvector",
                 "cgaffinetransform", "cgaffinetransformcomponents")
)


def _topic_paths(data: dict) -> list[str]:
    paths: list[str] = []
    references = data.get("references", {})
    for section in data.get("topicSections", []):
        for identifier in section.get("identifiers", []):
            ref = references.get(identifier, {})
            url = ref.get("url", "")
            if not url or url.startswith("http"):
                continue
            role = ref.get("role")
            if role in ("collectionGroup", "collection") or (role == "symbol" and ref.get("kind") == "symbol"):
                paths.append(url)
    return paths


async def crawl_framework_symbols(
    client: APIClient,
    framework: FrameworkInfo,
) -> list[str]:
    """Recursively discover all symbol doc paths for a framework.

    Returns list of doc paths like '/documentation/foundation/nsstring'.
    """
    symbol_paths_set: set[str] = set()
    visited: set[str] = set()
    queue: list[str] = [framework.doc_path]
    roots = (framework.doc_path.lower().rstrip("/"),)
    if roots[0] == "/documentation/coregraphics":
        roots += _CG_GEOMETRY_TOPICS
        queue.extend(_CG_GEOMETRY_TOPICS)

    async def process_page(doc_path: str) -> list[str]:
        data = await client.fetch_doc(doc_path)
        if data is None:
            return []

        kind = data.get("metadata", {}).get("symbolKind", "")
        role = data.get("metadata", {}).get("role", "")

        # If this is an actual symbol (not a collection/group), record it
        if role == "symbol" and kind != "module":
            symbol_paths_set.add(doc_path)

        # Objective-C topic overrides can expose symbols absent from the default view.
        paths = _topic_paths(data)
        if framework.has_objc and data.get("variantOverrides"):
            objc_data = _apply_variant_overrides(deepcopy(data), "occ")
            paths.extend(_topic_paths(objc_data))
        # A topic can link to a symbol owned by a foreign framework. Its
        # declaration and exports belong to that framework's own crawl.
        return list(dict.fromkeys(
            path for path in paths
            if any(path.lower() == root or path.lower().startswith(root + "/") for root in roots)
        ))

    # BFS through the framework's documentation tree
    while queue:
        # Deduplicate the queue against visited before processing
        batch: list[str] = []
        remaining: list[str] = []
        for path in queue:
            if path not in visited:
                visited.add(path)
                batch.append(path)
                if len(batch) >= 50:
                    remaining = queue[queue.index(path) + 1:]
                    break
        else:
            remaining = []
        queue = remaining

        if not batch:
            continue

        tasks = [process_page(path) for path in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.warning("Error crawling page: %s", result)
                continue
            queue.extend(result)

    symbol_paths = sorted(symbol_paths_set)
    logger.info(
        "Framework %s: discovered %d symbols (visited %d pages)",
        framework.name, len(symbol_paths), len(visited),
    )
    return symbol_paths
