/**
 * UI Screenshot Tests for Memory Viewer
 */
const { execSync } = require('child_process');
const fs = require('fs');
const http = require('http');

const BASE_URL = 'http://192.168.5.55:8501';
const CHROME = '/home/.cache/puppeteer/chrome-headless-shell/linux-148.0.7778.97/chrome-headless-shell-linux64/chrome-headless-shell';

const pages = [
  { path: '/', name: '01-home', w: 1920, h: 1080 },
  { path: '/hermes', name: '02-hermes-memory', w: 1920, h: 1080 },
  { path: '/profiles', name: '03-profiles', w: 1920, h: 1080 },
  { path: '/settings', name: '04-settings', w: 1920, h: 1080 },
  { path: '/collections', name: '05-collections', w: 1920, h: 1080 },
  { path: '/compare', name: '06-compare', w: 1920, h: 1080 },
  // Mobile
  { path: '/', name: '07-mobile-home', w: 375, h: 812 },
  { path: '/hermes', name: '08-mobile-hermes', w: 375, h: 812 },
];

function httpGet(path) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    http.get(url, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    }).on('error', reject);
  });
}

async function capture(page) {
  return new Promise((resolve, reject) => {
    const output = `/tmp/${page.name}.png`;
    const cmd = `${CHROME} --headless --disable-gpu --screenshot=${output} --viewport-width=${page.w} --viewport-height=${page.h} ${BASE_URL}${page.path}`;
    try {
      execSync(cmd, { stdio: 'pipe' });
      const size = fs.statSync(output).size;
      resolve(size);
    } catch (e) {
      reject(e);
    }
  });
}

async function main() {
  console.log('📸 Memory Viewer UI Screenshots\n');
  console.log('='.repeat(50));
  
  let passed = 0, failed = 0;
  
  for (const page of pages) {
    process.stdout.write(`  ${page.name} (${page.w}x${page.h})... `);
    try {
      const size = await capture(page);
      console.log(`✅ ${size} bytes`);
      passed++;
    } catch (e) {
      console.log(`❌ ${e.message}`);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);
  
  // Run E2E tests
  console.log('🧪 Running E2E Tests...\n');
  execSync('node e2e-test.cjs', { stdio: 'inherit', cwd: __dirname });
}

main().catch(e => {
  console.error('Error:', e);
  process.exit(1);
});
