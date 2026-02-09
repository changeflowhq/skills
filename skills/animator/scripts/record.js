#!/usr/bin/env node
// Frame-by-frame animation recorder using Playwright + ffmpeg
// Usage: node record.js <input.html> <output.mp4> [--fps 30] [--width 1280] [--height 720]

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

function parseArgs(args) {
  const opts = { fps: 30, width: 1280, height: 720 };
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--fps':    opts.fps = parseInt(args[++i]); break;
      case '--width':  opts.width = parseInt(args[++i]); break;
      case '--height': opts.height = parseInt(args[++i]); break;
      default:         positional.push(args[i]);
    }
  }

  if (positional.length < 2) {
    console.error('Usage: node record.js <input.html> <output.mp4> [--fps 30] [--width 1280] [--height 720]');
    process.exit(1);
  }

  opts.input = path.resolve(positional[0]);
  opts.output = path.resolve(positional[1]);

  if (!fs.existsSync(opts.input)) {
    console.error(`Input file not found: ${opts.input}`);
    process.exit(1);
  }

  return opts;
}

async function record(opts) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'animator-'));
  console.log(`Recording: ${opts.input}`);
  console.log(`Output:    ${opts.output}`);
  console.log(`Settings:  ${opts.width}x${opts.height} @ ${opts.fps}fps`);
  console.log(`Temp dir:  ${tmpDir}`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: opts.width, height: opts.height },
    deviceScaleFactor: 2,
  });

  // Load the HTML file
  await page.goto(`file://${opts.input}`, { waitUntil: 'networkidle' });

  // Read animation config from the page
  const config = await page.evaluate(() => {
    if (typeof window.ANIMATION === 'undefined') {
      return null;
    }
    return {
      fps: window.ANIMATION.fps || 30,
      totalFrames: window.ANIMATION.totalFrames || 150,
      duration: window.ANIMATION.duration || null,
    };
  });

  if (!config) {
    console.error('Error: page must define window.ANIMATION = { totalFrames, fps }');
    await browser.close();
    process.exit(1);
  }

  const totalFrames = config.totalFrames;
  const fps = opts.fps || config.fps;
  const durationSec = totalFrames / fps;

  console.log(`Animation: ${totalFrames} frames, ${durationSec.toFixed(1)}s at ${fps}fps`);

  // Pause all CSS animations and set them to the start
  await page.evaluate(() => {
    document.getAnimations().forEach(a => {
      a.pause();
      a.currentTime = 0;
    });
  });

  // Capture each frame
  const startTime = Date.now();
  for (let frame = 0; frame < totalFrames; frame++) {
    const timeMs = (frame / fps) * 1000;

    await page.evaluate(({ frame, totalFrames, timeMs }) => {
      // Step CSS animations
      document.getAnimations().forEach(a => {
        a.currentTime = timeMs;
      });

      // Step JS animation if renderFrame exists
      if (typeof window.renderFrame === 'function') {
        window.renderFrame(frame, totalFrames);
      }
    }, { frame, totalFrames, timeMs });

    // Small delay to let the browser render
    await page.evaluate(() => new Promise(r => requestAnimationFrame(r)));

    const framePath = path.join(tmpDir, `frame_${String(frame).padStart(5, '0')}.png`);
    await page.screenshot({ path: framePath });

    // Progress
    if (frame % 30 === 0 || frame === totalFrames - 1) {
      const pct = ((frame + 1) / totalFrames * 100).toFixed(0);
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`  Frame ${frame + 1}/${totalFrames} (${pct}%) - ${elapsed}s`);
    }
  }

  await browser.close();

  // Stitch with ffmpeg
  console.log('Stitching with ffmpeg...');
  const framePattern = path.join(tmpDir, 'frame_%05d.png');
  const ffmpegCmd = [
    'ffmpeg', '-y',
    '-framerate', String(fps),
    '-i', framePattern,
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '18',
    opts.output,
  ].join(' ');

  try {
    execSync(ffmpegCmd, { stdio: 'pipe' });
    console.log(`Done: ${opts.output}`);
  } catch (e) {
    console.error('ffmpeg failed:', e.stderr?.toString() || e.message);
    console.error(`Frames preserved at: ${tmpDir}`);
    process.exit(1);
  }

  // Clean up temp frames
  const frames = fs.readdirSync(tmpDir).filter(f => f.endsWith('.png'));
  frames.forEach(f => fs.unlinkSync(path.join(tmpDir, f)));
  fs.rmdirSync(tmpDir);

  // Report file size
  const stat = fs.statSync(opts.output);
  const sizeMB = (stat.size / (1024 * 1024)).toFixed(1);
  console.log(`File size: ${sizeMB} MB`);
}

const opts = parseArgs(process.argv.slice(2));
record(opts).catch(e => {
  console.error('Recording failed:', e);
  process.exit(1);
});
