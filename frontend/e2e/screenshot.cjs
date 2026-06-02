const { execSync } = require('child_process');
const fs = require('fs');

const BASE_URL = 'http://192.168.5.55:8501';
const CHROME = '/home/.cache/puppeteer/chrome-headless-shell/linux-148.0.7778.97/chrome-headless-shell-linux64/chrome-headless-shell';

const screenshots = [
  { url: BASE_URL, output: '/tmp/desktop.png', w: 1920, h: 1080, name: 'Desktop' },
  { url: BASE_URL, output: '/tmp/mobile.png', w: 375, h: 812, name: 'Mobile' }
];

console.log('📸 Memory Viewer Screenshot\n');
console.log('='.repeat(50));

for (const s of screenshots) {
  try {
    console.log(`  Capturing ${s.name} (${s.w}x${s.h})...`);
    execSync(`${CHROME} --headless --disable-gpu --screenshot=${s.output} --viewport-width=${s.w} --viewport-height=${s.h} ${s.url}`, { stdio: 'pipe' });
    const size = fs.statSync(s.output).size;
    console.log(`  ✅ ${s.output}: ${size} bytes`);
  } catch (e) {
    console.log(`  ❌ ${e.message}`);
  }
}

console.log('\n' + '='.repeat(50));
