"""Standalone RPP documents; no host or audio dependencies."""

from .parser import Document, Element, Line, RPPParseError, parse, emit
from .model import (
    Project,
    Track,
    Item,
    Take,
    FX,
    FXChain,
    Envelope,
    Source,
    MidiSource,
    FieldValue,
)

__version__ = "0.1.0a1"
__all__ = [
    "Document",
    "Element",
    "Line",
    "RPPParseError",
    "parse",
    "emit",
    "Project",
    "Track",
    "Item",
    "Take",
    "FX",
    "FXChain",
    "Envelope",
    "Source",
    "MidiSource",
    "FieldValue",
]
