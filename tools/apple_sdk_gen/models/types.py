from enum import Enum


class SymbolKind(Enum):
    MODULE = "module"
    CLASS = "class"
    STRUCT = "struct"
    ENUM = "enum"
    ENUM_CASE = "case"
    PROTOCOL = "protocol"
    INIT = "init"
    DEINIT = "deinit"
    METHOD = "method"
    PROPERTY = "property"
    SUBSCRIPT = "subscript"
    OPERATOR = "operator"
    FUNC = "func"
    VAR = "var"
    TYPEALIAS = "typealias"
    ASSOCIATION = "associatedtype"
    MACRO = "macro"
    UNION = "union"
    TYPEDEF = "typealias"
    UNKNOWN = "unknown"

    @classmethod
    def from_api(cls, value: str) -> "SymbolKind":
        mapping = {
            "module": cls.MODULE,
            "class": cls.CLASS,
            "struct": cls.STRUCT,
            "enum": cls.ENUM,
            "case": cls.ENUM_CASE,
            "protocol": cls.PROTOCOL,
            "init": cls.INIT,
            "deinit": cls.DEINIT,
            "method": cls.METHOD,
            "property": cls.PROPERTY,
            "subscript": cls.SUBSCRIPT,
            "operator": cls.OPERATOR,
            "func": cls.FUNC,
            "var": cls.VAR,
            "typealias": cls.TYPEALIAS,
            "associatedtype": cls.ASSOCIATION,
            "macro": cls.MACRO,
            "union": cls.UNION,
        }
        return mapping.get(value, cls.UNKNOWN)


class TokenKind(Enum):
    KEYWORD = "keyword"
    TEXT = "text"
    IDENTIFIER = "identifier"
    TYPE_IDENTIFIER = "typeIdentifier"
    GENERIC_PARAMETER = "genericParameter"
    INTERNAL_PARAM = "internalParam"
    EXTERNAL_PARAM = "externalParam"
    LABEL = "label"
    NUMBER = "number"
    STRING = "string"
    ATTRIBUTE = "attribute"


class PlatformName(Enum):
    IOS = "iOS"
    IPADOS = "iPadOS"
    MACOS = "macOS"
    TVOS = "tvOS"
    WATCHOS = "watchOS"
    VISIONOS = "visionOS"
    MAC_CATALYST = "Mac Catalyst"

    @classmethod
    def from_api(cls, value: str) -> "PlatformName | None":
        for member in cls:
            if member.value == value:
                return member
        return None


class InterfaceLanguage(Enum):
    SWIFT = "swift"
    OBJC = "occ"
