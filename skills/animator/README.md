# animator

Create short mp4 videos from HTML/CSS/JS animations. Frame-by-frame capture using Playwright + ffmpeg. Deterministic, smooth, pixel-perfect 30fps output.

<video src="demo.mp4" autoplay loop muted playsinline></video>

Write CSS animations normally - the recorder pauses all animations and steps `currentTime` per frame. Easing, delays, fill-mode all work. JS-driven animation is also supported via a `renderFrame()` callback.

## Quick Start

```bash
# Check everything is installed
node scripts/doctor.js

# Record an animation
node scripts/record.js animation.html output.mp4

# With custom settings
node scripts/record.js animation.html output.mp4 --fps 60 --width 1920 --height 1080
```

## Installation

### Dependencies

| Dependency | Install | Required for |
|------------|---------|-------------|
| Node.js | [nodejs.org](https://nodejs.org) | Everything |
| Playwright | `npm install` (in skill directory) | Browser rendering |
| ffmpeg | `brew install ffmpeg` | Stitching frames into mp4 |

Run `node scripts/doctor.js` to check what's installed and what's missing.

### Setup

```bash
cd skills/animator
npm install
```

This installs Playwright and downloads Chromium. First run may take a minute.

## How It Works

1. Playwright launches headless Chromium and loads your HTML file
2. All CSS animations are paused at frame 0
3. For each frame, the recorder advances `currentTime` by `1/fps` seconds
4. If your page defines `window.renderFrame(frame, totalFrames)`, that's called too
5. Each frame is screenshotted as a 2x retina PNG
6. ffmpeg stitches the PNGs into an mp4 (h264, yuv420p, CRF 18)

CSS and JS animation can coexist - the recorder steps both to the same point in time.

## Writing Animations

Start from the boilerplate template:

```bash
cp templates/boilerplate.html my-animation.html
```

### Requirements

Your HTML page must:

1. **Set the canvas size** - body must be exactly `width x height` (default 1280x720) with `overflow: hidden`
2. **Define config** - `window.ANIMATION = { fps: 30, totalFrames: N }`
3. **totalFrames / fps = duration** - 90 frames at 30fps = 3 seconds

### CSS Animations

Write them normally. The recorder handles the rest.

```css
.item {
  animation: fadeSlideIn 0.5s ease-out forwards;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

Tips:
- `animation-fill-mode: forwards` to hold final state
- `animation-delay` to sequence elements
- `cubic-bezier()` easing renders perfectly frame-by-frame
- `clip-path`, `filter`, `backdrop-filter`, transforms all work

### JS Animations

For anything CSS can't do (typewriters, counters, data-driven visuals), define `renderFrame`:

```js
window.renderFrame = function(frame, totalFrames) {
  const progress = frame / totalFrames; // 0 to 1
  document.getElementById('counter').textContent = Math.floor(progress * 100);
};
```

### Common Patterns

**Staggered entrance:**
```css
.item:nth-child(1) { animation: fadeIn 0.5s 0.0s forwards; }
.item:nth-child(2) { animation: fadeIn 0.5s 0.2s forwards; }
.item:nth-child(3) { animation: fadeIn 0.5s 0.4s forwards; }
```

**Scene transitions:**
```css
.scene-1 { animation: fadeOut 0.3s 2s forwards; }
.scene-2 { animation: fadeIn 0.3s 2.3s forwards; opacity: 0; }
```

**Typewriter (JS):**
```js
window.renderFrame = function(frame, total) {
  const text = "Hello, world";
  const chars = Math.floor((frame / total) * text.length);
  document.getElementById('typed').textContent = text.slice(0, chars);
};
```

### What To Avoid

- `requestAnimationFrame` loops - use `renderFrame()` instead
- `setInterval`/`setTimeout` - they won't sync with frame capture
- External fonts without embedding (use base64 or system fonts)
- Very long animations - 300 frames (10s) takes ~60s to render

## Output

| Property | Value |
|----------|-------|
| Format | mp4 (h264, yuv420p) |
| Quality | CRF 18 (high quality, reasonable size) |
| Resolution | 2x deviceScaleFactor for crisp text |
| Typical size | 1-5 MB for 3-10 seconds |

## Options

```
node scripts/record.js <input.html> <output.mp4> [options]

--fps N       Frame rate (default: 30)
--width N     Viewport width (default: 1280)
--height N    Viewport height (default: 720)
```

## License

MIT
