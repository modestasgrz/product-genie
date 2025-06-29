import re


class ColorUtils:
    """Utility class for color format conversions."""

    @staticmethod
    def to_hex(color_str: str) -> str:
        """
        Convert a color string to 6-digit hex format (#rrggbb).

        Accepts:
        - Hex: "#abc", "abc", "#aabbcc", "aabbcc" (3- or 6-digit)
        - RGB: "rgb(255, 0, 128)" or with floats "rgb(255.0,128.5,0)"
        - RGBA: "rgba(255,0,128,0.5)" (alpha ignored)

        Args:
            color_str: Color string in various formats

        Returns:
            Hex color string in format #rrggbb

        Raises:
            ValueError: If color format is not recognized
        """
        s = color_str.strip()

        # Handle hex input
        hex_match = re.fullmatch(r"#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})", s)
        if hex_match:
            h = hex_match.group(1)
            if len(h) == 3:
                # Expand "abc" -> "aabbcc"
                h = "".join(ch * 2 for ch in h)
            return "#" + h.lower()

        # Handle rgb/rgba
        rgb_match = re.fullmatch(
            r"rgba?\(\s*([0-9]*\.?[0-9]+)\s*,\s*"
            r"([0-9]*\.?[0-9]+)\s*,\s*"
            r"([0-9]*\.?[0-9]+)(?:\s*,\s*[0-9]*\.?[0-9]+)?\s*\)",
            s,
            re.IGNORECASE,
        )
        if rgb_match:
            channels = []
            for group in rgb_match.groups()[:3]:
                val = float(group)
                i = int(round(val))
                # Clamp to [0,255]
                i = max(0, min(255, i))
                channels.append(i)
            return "#{:02x}{:02x}{:02x}".format(*channels)

        raise ValueError(f"Unrecognized color format: {color_str!r}")
