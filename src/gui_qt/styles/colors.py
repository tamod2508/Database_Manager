"""
Professional Blue Gradient Color Palette
Classic corporate blue scheme with proper contrast
"""

# Main Color Palette (Light to Dark Blues)
TRUE_BLUE = "#0466c8"        # Brightest - primary actions, accents
SAPPHIRE = "#0353a4"         # Bright - secondary actions
YALE_BLUE = "#023e7d"        # Medium - info actions, borders
OXFORD_BLUE_1 = "#002855"    # Dark - containers
OXFORD_BLUE_2 = "#001845"    # Darker - deep containers  
OXFORD_BLUE_3 = "#001233"    # Darkest - deep backgrounds

# Supporting Grays (Blue-tinted)
DELFT_BLUE = "#33415c"       # Blue-gray containers, sidebar
PAYNE_GRAY = "#5c677d"       # Medium blue-gray, borders
SLATE_GRAY = "#7d8597"       # Light blue-gray, hover states
COOL_GRAY = "#979dac"        # Lightest blue-gray, text

# Extended Palette (hover/active states)
TRUE_BLUE_LIGHT = "#0f85fa"      # Hover states
TRUE_BLUE_LIGHTER = "#4ba3fb"    # Active/pressed states

SAPPHIRE_LIGHT = "#0576e8"       # Hover states
SAPPHIRE_LIGHTER = "#3698fb"     # Active/pressed states

YALE_BLUE_LIGHT = "#0363c9"      # Hover states  
YALE_BLUE_LIGHTER = "#1d89fc"    # Active/pressed states

DELFT_BLUE_LIGHT = "#4d628b"     # Hover states
DELFT_BLUE_LIGHTER = "#7186b1"   # Active/pressed states

# Background Colors
BACKGROUND_MAIN = "#2a2d35"      # Main background (dark gray, not black)
BACKGROUND_CARD = "#33415c"      # Card/container backgrounds
BACKGROUND_DEEP = "#1a1d22"      # Deep backgrounds (text areas)

# Text Colors
TEXT_PRIMARY = "#ffffff"         # Main text - pure white
TEXT_SECONDARY = "#eaebee"       # Secondary text - very light gray
TEXT_MUTED = "#d5d7dd"          # Muted text - light gray
TEXT_DISABLED = "#979dac"        # Disabled text - cool gray

# Usage Guide:
# Background hierarchy: BACKGROUND_MAIN → BACKGROUND_CARD → elements
# Button hierarchy: TRUE_BLUE (primary) → SAPPHIRE (secondary) → YALE_BLUE (info) → DELFT_BLUE (neutral)
# Text hierarchy: TEXT_PRIMARY → TEXT_SECONDARY → TEXT_MUTED → TEXT_DISABLED

# Button Color Mapping:
# - Primary (Update Data): TRUE_BLUE - vibrant corporate blue
# - Secondary (Full Refresh): SAPPHIRE - professional blue (attention)  
# - Info (Refresh View): YALE_BLUE - trustworthy blue
# - Neutral (Check Plan): DELFT_BLUE - subtle blue-gray
