from __future__ import annotations

import asyncio
import logging

from .client import APIClient
from .technologies import FrameworkInfo

logger = logging.getLogger(__name__)


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

    async def process_page(doc_path: str) -> list[str]:
        data = await client.fetch_doc(doc_path)
        if data is None:
            return []

        child_paths: list[str] = []
        kind = data.get("metadata", {}).get("symbolKind", "")
        role = data.get("metadata", {}).get("role", "")

        # If this is an actual symbol (not a collection/group), record it
        if role == "symbol" and kind != "module":
            symbol_paths_set.add(doc_path)

        # Expand topicSections to find child symbols
        for section in data.get("topicSections", []):
            for identifier in section.get("identifiers", []):
                ref = data.get("references", {}).get(identifier, {})
                ref_kind = ref.get("kind", "")
                ref_role = ref.get("role", "")
                ref_url = ref.get("url", "")

                if not ref_url:
                    continue

                # Skip external references
                if ref_url.startswith("http"):
                    continue

                if ref_kind == "symbol" and ref_role == "symbol":
                    child_paths.append(ref_url)
                elif ref_role in ("collectionGroup", "collection"):
                    child_paths.append(ref_url)

        return child_paths

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
