from __future__ import annotations

from dataclasses import dataclass, field, replace

from .types import InterfaceLanguage, PlatformName, SymbolKind, TokenKind


_DECLARATION_WORD_TOKENS = {
    TokenKind.KEYWORD,
    TokenKind.IDENTIFIER,
    TokenKind.TYPE_IDENTIFIER,
    TokenKind.GENERIC_PARAMETER,
    TokenKind.INTERNAL_PARAM,
    TokenKind.EXTERNAL_PARAM,
}


def _is_identifier_character(character: str) -> bool:
    return character.isalnum() or character == "_"


@dataclass
class Token:
    kind: TokenKind
    text: str
    precise_identifier: str | None = None
    identifier: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> Token:
        return cls(
            kind=TokenKind(data["kind"]),
            text=data.get("text", ""),
            precise_identifier=data.get("preciseIdentifier"),
            identifier=data.get("identifier"),
        )


@dataclass
class Declaration:
    tokens: list[Token]
    languages: list[str]
    platforms: list[str]

    @classmethod
    def from_api(cls, data: dict) -> Declaration:
        return cls(
            tokens=[Token.from_api(t) for t in data.get("tokens", [])],
            languages=data.get("languages", []),
            platforms=data.get("platforms", []),
        )

    def render(self) -> str:
        if InterfaceLanguage.OBJC.value not in self.languages:
            return "".join(token.text for token in self.tokens)

        # DocC can omit whitespace between distinct C or Objective-C words.
        parts: list[str] = []
        previous_ends_word = False
        for token in self.tokens:
            if not token.text:
                continue
            is_word = token.kind in _DECLARATION_WORD_TOKENS
            if previous_ends_word and is_word and _is_identifier_character(token.text[0]):
                parts.append(" ")
            parts.append(token.text)
            previous_ends_word = is_word and _is_identifier_character(token.text[-1])
        return "".join(parts)


@dataclass
class PlatformAvailability:
    platform: PlatformName
    introduced_at: str | None = None
    deprecated_at: str | None = None
    unavailable: bool = False
    beta: bool = False

    @classmethod
    def from_api(cls, data: dict) -> PlatformAvailability | None:
        platform = PlatformName.from_api(data.get("name", ""))
        if platform is None:
            return None
        return cls(
            platform=platform,
            introduced_at=data.get("introducedAt"),
            deprecated_at=data.get("deprecatedAt"),
            unavailable=data.get("unavailable", False),
            beta=data.get("beta", False),
        )


@dataclass
class Relationship:
    kind: str  # "inheritsFrom", "inheritedBy", "conformsTo"
    identifiers: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> Relationship:
        return cls(
            kind=data.get("type", ""),
            identifiers=data.get("identifiers", []),
        )


@dataclass
class Symbol:
    identifier: str
    title: str
    kind: SymbolKind
    usr: str | None = None
    framework: str | None = None
    parent_identifier: str | None = None

    swift_declaration: Declaration | None = None
    objc_declaration: Declaration | None = None

    availability: list[PlatformAvailability] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    children: list[str] = field(default_factory=list)

    role: str = ""
    role_heading: str = ""
    objc_declarations: list[Declaration] = field(default_factory=list)
    memberwise_fields: tuple[str, ...] = ()
    objc_kind: SymbolKind | None = None
    objc_title: str | None = None
    objc_children: list[str] | None = None

    def for_objc(self) -> Symbol:
        return replace(
            self,
            kind=self.objc_kind or self.kind,
            title=self.objc_title or self.title,
            children=self.children if self.objc_children is None else self.objc_children,
        )

    def for_platform(self, platform: PlatformName) -> Symbol:
        if not self.objc_declarations:
            return self
        declaration = next(
            (decl for decl in self.objc_declarations if platform.value in decl.platforms),
            None,
        )
        if declaration is None:
            declaration = next((decl for decl in self.objc_declarations if not decl.platforms), None)
        return replace(self, objc_declaration=declaration)

    @property
    def is_objc(self) -> bool:
        return self.objc_declaration is not None

    @property
    def is_swift(self) -> bool:
        return self.swift_declaration is not None

    @property
    def objc_name(self) -> str:
        if self.usr:
            # Extract class name from USR like c:objc(cs)NSString
            if "(cs)" in self.usr:
                return self.usr.split("(cs)")[-1].split("(")[0]
            if "(pl)" in self.usr:
                return self.usr.split("(pl)")[-1].split("(")[0]
            if "@E@" in self.usr:
                return self.usr.split("@E@")[-1].split("@")[0]
            if "@T@" in self.usr:
                return self.usr.split("@T@")[-1].split("@")[0]
            if "@F@" in self.usr:
                return self.usr.split("@F@")[-1]
        return self.title

    def superclass_usr(self) -> str | None:
        for rel in self.relationships:
            if rel.kind == "inheritsFrom":
                for ident in rel.identifiers:
                    if "objc(cs)" in ident or "c:objc(cs)" in ident:
                        # Extract USR from doc:// identifier
                        if ident.startswith("doc://com.externally.resolved.symbol/"):
                            return ident.split("/", 3)[-1]
                        return ident
        return None
