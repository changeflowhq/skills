# Learned

## Glow Effects
- Don't use a blurred duplicate text element for glow - it creates a background blob, not a text glow
- `text-shadow` doesn't work when `color: transparent` (needed for `background-clip: text`) - the shadow renders from the transparent color, so it's invisible
- For glow + background-clip text combo: wrap in a div and use `filter: drop-shadow()` on the wrapper - drop-shadow works on rendered pixels, not the color property
- `mix-blend-mode: screen` for gleam overlays doesn't work on near-dark backgrounds - the gradient is still visible as a rectangle

## Gleam/Shine Effects
- Best technique: use `background-clip: text` with a moving gradient as the gleam, layered on top of a base gradient fill. Impossible to leak outside letterforms.
- For gleam on colored (non-transparent) text: use a separate identical text element with `background-clip: text` and `color: transparent` positioned on top, with only the gleam gradient
- Animate `background-position` to sweep the gleam across

## Animation Timing
- Google Fonts load fine from `file://` URLs in Playwright
- `filter: drop-shadow()` is expensive to render per frame - expect 3-4x slower capture vs simple text
- Orbitron is a good cinematic/techy display font for title cards
