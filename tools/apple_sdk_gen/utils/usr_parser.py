from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class TBDSymbolKind(Enum):
    SYMBOL = "symbol"
    OBJC_CLASS = "objc-class"
    OBJC_IVAR = "objc-ivar"
    OBJC_EHTYPE = "objc-eh-type"


@dataclass
class TBDSymbol:
    name: str
    kind: TBDSymbolKind


def usr_to_tbd_symbols(usr: str) -> list[TBDSymbol]:
    if not usr:
        return []

    # ObjC class: c:objc(cs)NSString
    m = re.match(r"c:objc\(cs\)(\w+)$", usr)
    if m:
        cls_name = m.group(1)
        return [TBDSymbol(cls_name, TBDSymbolKind.OBJC_CLASS)]

    # ObjC class with method: c:objc(cs)NSString(im)initWithString:
    m = re.match(r"c:objc\(cs\)(\w+)\((im|cm)\).+", usr)
    if m:
        # Methods don't produce separate TBD symbols, they're part of the class
        return []

    # ObjC class with property: c:objc(cs)NSString(py)length
    m = re.match(r"c:objc\(cs\)(\w+)\(py\).+", usr)
    if m:
        return []

    # ObjC protocol: c:objc(pl)NSCoding
    m = re.match(r"c:objc\(pl\)(\w+)$", usr)
    if m:
        return []  # Protocols don't have TBD symbols directly

    # ObjC protocol method: c:objc(pl)NSCoding(im)encodeWithCoder:
    m = re.match(r"c:objc\(pl\)\w+\((im|cm)\).+", usr)
    if m:
        return []

    # C function: c:@F@NSLog
    m = re.match(r"c:@F@(\w+)$", usr)
    if m:
        func_name = m.group(1)
        return [TBDSymbol(f"_{func_name}", TBDSymbolKind.SYMBOL)]

    # C global variable: c:@NSFoundationVersionNumber
    m = re.match(r"c:@(\w+)$", usr)
    if m:
        var_name = m.group(1)
        return [TBDSymbol(f"_{var_name}", TBDSymbolKind.SYMBOL)]

    # Enum: c:@E@NSComparisonResult
    m = re.match(r"c:@E@(\w+)$", usr)
    if m:
        return []  # Enum type itself doesn't produce TBD symbols

    # Enum constant: c:@E@NSComparisonResult@NSOrderedAscending
    m = re.match(r"c:@E@\w+@(\w+)$", usr)
    if m:
        const_name = m.group(1)
        return [TBDSymbol(f"_{const_name}", TBDSymbolKind.SYMBOL)]

    # Typedef: c:@T@NSInteger
    m = re.match(r"c:@T@(\w+)$", usr)
    if m:
        return []  # Typedefs don't produce TBD symbols

    # Struct: c:@S@CGPoint
    m = re.match(r"c:@S@(\w+)$", usr)
    if m:
        return []  # Structs don't produce TBD symbols

    # Struct field: c:@S@CGPoint@FI@x
    m = re.match(r"c:@S@\w+@FI@.+", usr)
    if m:
        return []

    # ObjC category: c:objc(cy)NSString@Category
    m = re.match(r"c:objc\(cy\)(\w+)@.+", usr)
    if m:
        return []

    # ObjC exception type
    m = re.match(r"c:objc\(cs\)(\w+)$", usr)
    if m:
        return [TBDSymbol(m.group(1), TBDSymbolKind.OBJC_CLASS)]

    return []


@dataclass
class FrameworkTBDSymbols:
    symbols: list[str] = field(default_factory=list)
    objc_classes: list[str] = field(default_factory=list)

    def add(self, tbd_sym: TBDSymbol) -> None:
        if tbd_sym.kind == TBDSymbolKind.OBJC_CLASS:
            if tbd_sym.name not in self.objc_classes:
                self.objc_classes.append(tbd_sym.name)
        elif tbd_sym.kind == TBDSymbolKind.SYMBOL:
            if tbd_sym.name not in self.symbols:
                self.symbols.append(tbd_sym.name)

    def add_from_usr(self, usr: str) -> None:
        for sym in usr_to_tbd_symbols(usr):
            self.add(sym)

    @property
    def is_empty(self) -> bool:
        return not self.symbols and not self.objc_classes
