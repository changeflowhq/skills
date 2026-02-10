# Learned

## Glow Effects
- Don't use a blurred duplicate text element for glow - it creates a background blob, not a text glow. Use text-shadow layers instead, they hug the letterforms.
- For gleam/shine streaks over text, use `mix-blend-mode: screen` on the overlay - it only brightens light pixels (text) and is invisible on dark backgrounds. Without it you get a visible rectangle.
