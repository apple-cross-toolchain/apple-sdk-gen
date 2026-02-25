from __future__ import annotations

import logging

from .client import APIClient
from ..models.symbol import (
    Declaration,
    PlatformAvailability,
    Relationship,
    Symbol,
)
from ..models.types import SymbolKind

logger = logging.getLogger(__name__)


def _apply_variant_overrides(data: dict, language: str) -> dict:
    """Apply JSON Patch operations from variantOverrides for the given language."""
    for variant in data.get("variantOverrides", []):
        traits = variant.get("traits", [])
        if any(t.get("interfaceLanguage") == language for t in traits):
            for op in variant.get("patch", []):
                if op.get("op") != "replace":
                    continue
                path = op.get("path", "")
                value = op.get("value")
                if value is None:
                    continue
                _apply_json_path(data, path, value)
            break
    return data


def _apply_json_path(data: dict, path: str, value: object) -> None:
    """Apply a single JSON Patch replace operation."""
    parts = path.strip("/").split("/")
    current: object = data
    for part in parts[:-1]:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return
        else:
            return

    if current is None:
        return

    last = parts[-1]
    if isinstance(current, dict):
        current[last] = value
    elif isinstance(current, list):
        try:
            current[int(last)] = value
        except (ValueError, IndexError):
            pass


def _extract_declarations(data: dict, language: str) -> Declaration | None:
    """Extract declaration for the given language from primaryContentSections."""
    for section in data.get("primaryContentSections", []):
        if section.get("kind") != "declarations":
            continue
        for decl_data in section.get("declarations", []):
            langs = decl_data.get("languages", [])
            if language in langs:
                return Declaration.from_api(decl_data)
    return None


async def parse_symbol(
    client: APIClient,
    doc_path: str,
    framework_name: str,
) -> Symbol | None:
    """Fetch and parse a symbol page into a Symbol dataclass."""
    data = await client.fetch_doc(doc_path)
    if data is None:
        return None

    metadata = data.get("metadata", {})
    kind_str = metadata.get("symbolKind", "unknown")
    role = metadata.get("role", "")

    if role != "symbol":
        return None

    identifier = data.get("identifier", {}).get("url", doc_path)
    title = metadata.get("title", "")
    usr = metadata.get("externalID")

    # Parse availability
    availability = []
    for plat_data in metadata.get("platforms", []):
        avail = PlatformAvailability.from_api(plat_data)
        if avail is not None:
            availability.append(avail)

    # Parse relationships
    relationships = []
    for rel_section in data.get("relationshipsSections", []):
        relationships.append(Relationship.from_api(rel_section))

    # Extract Swift declaration (default language in the API)
    swift_decl = _extract_declarations(data, "swift")

    # Extract ObjC declaration by applying variant overrides
    import copy
    objc_data = copy.deepcopy(data)
    _apply_variant_overrides(objc_data, "occ")
    objc_decl = _extract_declarations(objc_data, "occ")

    # Collect child symbol identifiers from topicSections
    children: list[str] = []
    for section in data.get("topicSections", []):
        for ident in section.get("identifiers", []):
            ref = data.get("references", {}).get(ident, {})
            if ref.get("kind") == "symbol" and ref.get("role") == "symbol":
                child_url = ref.get("url", "")
                if child_url:
                    children.append(child_url)

    symbol = Symbol(
        identifier=identifier,
        title=title,
        kind=SymbolKind.from_api(kind_str),
        usr=usr,
        framework=framework_name,
        swift_declaration=swift_decl,
        objc_declaration=objc_decl,
        availability=availability,
        relationships=relationships,
        children=children,
        role=role,
        role_heading=metadata.get("roleHeading", ""),
    )

    return symbol
