"""Resolve the KMDStudio Design Language from the validated brief."""

DEFAULT_COLORS = {
    "primary": "173B55", "secondary": "3A5061", "accent": "125D68",
    "surface": "ECF3F6", "background": "FFFFFF", "text": "202B36",
    "muted": "4E606F", "border": "BCCBD3", "on_primary": "FFFFFF",
    "code_background": "F1F4F8", "code_text": "253244", "syntax_keyword": "573B8A",
    "syntax_string": "126348", "syntax_number": "934214", "syntax_comment": "4F5965",
    "syntax_operator": "4A5264", "info": "205C78", "success": "196049", "warning": "83450E",
}
DEFAULT_TYPE = {
    "heading_font": "Arial", "body_font": "Arial", "caption_font": "Arial",
    "monospace_font": "Consolas", "display_pt": 39, "heading_pt": 26,
    "subheading_pt": 17, "body_pt": 11, "caption_pt": 10, "code_pt": 10,
    "display_weight": "bold", "heading_weight": "bold", "subheading_weight": "bold",
    "body_weight": "regular", "caption_weight": "regular", "code_weight": "regular",
    "display_line_percent": 110, "heading_line_percent": 116, "body_line_percent": 128,
    "code_line_percent": 124,
}
EDITORIAL_TYPE = {
    "display_font", "metadata_font", "metadata_pt", "metadata_weight", "caption_line_percent",
    "metadata_line_percent", "display_tracking_twips", "heading_tracking_twips",
    "metadata_tracking_twips", "display_align", "metadata_align",
}
EDITORIAL_MODES = {"creative", "hybrid"}
FONT_FALLBACKS = {
    "Manrope": "Arial", "Inter": "Arial", "Golos Text": "Arial", "Onest": "Arial",
    "IBM Plex Sans": "Arial", "Literata": "Georgia", "JetBrains Mono": "Consolas",
}
DENSITIES = {
    "compact": {"margin_mm": 22, "paragraph_pt": 6, "component_pt": 8, "cell_pt": 5},
    "balanced": {"margin_mm": 22, "paragraph_pt": 8, "component_pt": 12, "cell_pt": 6},
    "spacious": {"margin_mm": 24, "paragraph_pt": 10, "component_pt": 16, "cell_pt": 7},
}
PROFILES = {
    "soft-education": {
        "colors": {"primary": "22463D", "secondary": "39564D", "accent": "12634E",
                   "surface": "EBF5ED", "border": "AFC9B7", "info": "235C6A"},
        "typography": {"heading_font": "Georgia", "display_pt": 43},
        "composition": {"cover": "panel", "heading_rule": False},
    },
    "technical-modern": {
        "colors": {"primary": "16364C", "accent": "075E66", "surface": "E8F3F3",
                   "code_background": "EAF0F7", "border": "ACBFC9"},
        "typography": {"display_pt": 40, "heading_pt": 27},
        "composition": {"cover": "panel", "heading_rule": True},
    },
    "bold-editorial": {
        "colors": {"primary": "532244", "secondary": "634357", "accent": "8B2D4E",
                   "surface": "F7EDF1", "border": "D4ADBD", "muted": "62505C"},
        "typography": {"heading_font": "Georgia", "body_font": "Georgia", "display_pt": 47,
                       "heading_pt": 29, "body_line_percent": 135},
        "composition": {"cover": "rule", "heading_rule": True},
        "density": "spacious",
    },
    "business-premium": {
        "colors": {"primary": "203950", "accent": "2E526A", "surface": "EEF2F5",
                   "border": "B9C7D1"},
        "typography": {"heading_font": "Georgia", "display_pt": 35, "heading_pt": 24,
                       "subheading_pt": 16, "body_line_percent": 121},
        "composition": {"cover": "plain", "heading_rule": True},
        "density": "compact",
    },
    "creative-playful": {
        "colors": {"primary": "482765", "secondary": "534163", "accent": "7D3B21",
                   "surface": "F4ECFA", "border": "CCB5DD", "success": "2A614D"},
        "typography": {"display_pt": 44, "heading_pt": 28, "body_pt": 12},
        "composition": {"cover": "panel", "heading_rule": False},
    },
    "swiss-minimal": {
        "colors": {"primary": "22282B", "secondary": "3C484D", "accent": "444F54",
                   "surface": "F1F3F3", "border": "BFC5C7"},
        "typography": {"display_pt": 38, "display_weight": "regular", "heading_pt": 25},
        "composition": {"cover": "plain", "heading_rule": False},
        "density": "spacious",
    },
}


def contrast(a, b):
    def luminance(rgb):
        srgb = [int(rgb[index:index + 2], 16) / 255 for index in (0, 2, 4)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
        return sum(c * weight for c, weight in zip(linear, (.2126, .7152, .0722), strict=True))

    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


def check_contrast(colors):
    body = ("primary", "secondary", "accent", "text", "muted", "info", "success", "warning")
    pairs = [(role, bg) for role in body for bg in ("background", "surface", "paper")]
    pairs += [(role, "code_background") for role in colors
              if role == "code_text" or role.startswith("syntax_")]
    pairs.append(("on_primary", "primary"))
    colors = colors | {"paper": "FFFFFF"}
    for fg, bg in pairs:
        ratio = contrast(colors[fg], colors[bg])
        if ratio < 4.5:
            raise ValueError(f"color {fg} on {bg} requires 4.5:1 contrast (got {ratio:.2f}:1)")


def font_substitutions(design, available_fonts):
    typography = design.get("tokens", {}).get("typography", {})
    return {font: FONT_FALLBACKS[font] for key, font in typography.items()
            if key.endswith("_font") and font in FONT_FALLBACKS and font not in available_fonts}


def resolve_design(design, mode="structured", available_fonts=()):
    editorial = mode in EDITORIAL_MODES
    if "palette" in design:
        if editorial:
            raise ValueError("creative and hybrid modes require KDL tokens")
        # Preserve the v1 controls and their original contrast contract.
        colors = {key: value.upper() for key, value in design["palette"].items()}
        for role in ("ink", "muted", "accent"):
            if any(contrast(colors[role], bg) < 4.5 for bg in ("FFFFFF", colors["tint"])):
                raise ValueError(f"palette {role} requires 4.5:1 contrast on white and tint")
        fonts, spacing = design["typography"], design["spacing"]
        return {
            "colors": DEFAULT_COLORS | {
                "primary": colors["ink"], "secondary": colors["muted"], "accent": colors["accent"],
                "text": colors["ink"], "muted": colors["muted"], "surface": colors["tint"],
                "border": colors["muted"],
                **dict.fromkeys(("info", "success", "warning"), colors["accent"]),
            },
            "typography": DEFAULT_TYPE | {
                "heading_font": fonts["title_font"], "body_font": fonts["body_font"],
                "caption_font": fonts["body_font"], "monospace_font": fonts["code_font"],
                "display_pt": fonts["title_pt"], "body_pt": fonts["body_pt"],
                "heading_pt": 23, "subheading_pt": 14, "body_line_percent": spacing["line_percent"],
            },
            "spacing": DENSITIES["balanced"] | {
                "margin_mm": spacing["margin_mm"], "paragraph_pt": spacing["paragraph_pt"],
            },
            "composition": {"cover": "plain", "heading_rule": False},
        }
    if not editorial and "profile" not in design:
        raise ValueError("structured KDL design requires a profile")
    profile = PROFILES[design["profile"]] if "profile" in design else {
        "colors": {}, "typography": {}, "composition": {"cover": "plain", "heading_rule": False},
    }
    tokens = design.get("tokens", {})
    density = design.get("density", profile.get("density", "balanced"))
    colors = DEFAULT_COLORS | profile["colors"] | tokens.get("colors", {})
    colors = {role: value.upper() for role, value in colors.items()}
    check_contrast(colors)
    typography = DEFAULT_TYPE | profile["typography"] | tokens.get("typography", {})
    if editorial:
        typography.setdefault("display_font", typography["heading_font"])
        typography.setdefault("metadata_font", typography["caption_font"])
        typography.setdefault("metadata_pt", typography["caption_pt"])
        typography.setdefault("metadata_weight", "bold")
        if typography["display_font"] == "Arial Black" and typography["display_weight"] != "regular":
            raise ValueError("Arial Black requires regular to select its native heavy face")
        substitutions = font_substitutions(design, available_fonts)
        typography = {key: substitutions.get(value, value) if key.endswith("_font") else value
                      for key, value in typography.items()}
    elif EDITORIAL_TYPE & typography.keys() or typography["display_pt"] > 49:
        raise ValueError("editorial typography requires creative or hybrid mode")
    roles = ("display_pt", "heading_pt", "subheading_pt", "body_pt", "caption_pt")
    sizes = [typography[role] for role in roles]
    if any(larger <= smaller for larger, smaller in zip(sizes, sizes[1:])):
        raise ValueError("type sizes must descend from display to heading, subheading, body and caption")
    return {
        "colors": colors,
        "typography": typography,
        "spacing": DENSITIES[density] | tokens.get("spacing", {}),
        "composition": profile["composition"] | tokens.get("composition", {}),
    }
