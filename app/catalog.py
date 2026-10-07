"""Every artist style, in the order the UI lists them."""

from app.artists import ARTISTS as POP_ARTISTS
from app.masters import MASTERS

ARTISTS = {**POP_ARTISTS, **MASTERS}
