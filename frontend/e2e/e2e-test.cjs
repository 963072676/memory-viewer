/**
 * E2E Tests for Memory Viewer
 */
const https = require('https');
const http = require('http');

const BASE_URL = 'http://192.168.5.55:8501';

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

async function runTests() {
  console.log('🧪 Memory Viewer E2E Tests\n');
  console.log('='.repeat(50));
  
  for (const t of tests) {
    try {
      process.stdout.write(`  ${t.name}... `);
      await t.fn();
      console.log('✅');
      passed++;
    } catch (err) {
      console.log(`❌ (${err.message})`);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  console.log(`\n📊 Results: ${passed} passed, ${failed} failed\n`);
  process.exit(failed > 0 ? 1 : 0);
}

function httpGet(path) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const client = url.protocol === 'https:' ? https : http;
    const req = client.get(url, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, data });
        }
      });
    });
    req.on('error', reject);
    req.setTimeout(5000, () => reject(new Error('Timeout')));
  });
}

// API Tests
test('API: Health endpoint returns OK', async () => {
  const res = await httpGet('/api/health');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (res.data.status !== 'ok') throw new Error(`Status is ${res.data.status}`);
});

test('API: Stats endpoint works', async () => {
  const res = await httpGet('/api/stats');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (!res.data.agentmemory) throw new Error('Missing agentmemory stats');
});

test('API: AgentMemory list works', async () => {
  const res = await httpGet('/api/agentmemory?limit=10');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (!Array.isArray(res.data.memories)) throw new Error('Missing memories array');
});

test('API: Search endpoint works', async () => {
  const res = await httpGet('/api/search?q=test');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (typeof res.data.total !== 'number') throw new Error('Missing total');
});

test('API: Hermes Memory endpoint works', async () => {
  const res = await httpGet('/api/hermes-memory');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (!res.data.profiles) throw new Error('Missing profiles');
});

test('API: Profiles endpoint works', async () => {
  const res = await httpGet('/api/profiles');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

// Frontend Tests
test('Frontend: Main page loads', async () => {
  const res = await httpGet('/');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('Frontend: CSS/JS assets accessible', async () => {
  const res = await httpGet('/');
  if (!res.data.includes('script') && !res.data.includes('<div')) {
    throw new Error('Invalid HTML response');
  }
});

// CRUD Tests
test('CRUD: Create memory', async () => {
  const payload = JSON.stringify({
    title: 'E2E Test Memory',
    content: 'Test content for E2E testing',
    type: 'pattern',
    concepts: ['e2e', 'test'],
    strength: 5
  });
  
  return new Promise((resolve, reject) => {
    const url = new URL('/api/agentmemory', BASE_URL);
    const req = http.request({
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    }, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try {
          const d = JSON.parse(data);
          if (!d.success || !d.memory) reject(new Error('Create failed'));
          resolve();
        } catch { reject(new Error('Invalid response')); }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
});

test('CRUD: Read memory', async () => {
  const res = await httpGet('/api/agentmemory');
  if (!res.data.memories || res.data.memories.length === 0) {
    throw new Error('No memories to read');
  }
});

// UI Endpoint Tests
test('UI: Collections endpoint accessible', async () => {
  const res = await httpGet('/api/collections');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Compare profiles list accessible', async () => {
  const res = await httpGet('/api/compare/profiles/list');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Sources endpoint accessible', async () => {
  const res = await httpGet('/api/sources');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Dashboard presets accessible', async () => {
  const res = await httpGet('/api/dashboard/presets');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Dashboard layout accessible', async () => {
  const res = await httpGet('/api/dashboard/layout');
  if (![200, 404].includes(res.status)) throw new Error(`Status ${res.status}`);
});

test('UI: Favorites endpoint accessible', async () => {
  const res = await httpGet('/api/favorites');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Config endpoint accessible', async () => {
  const res = await httpGet('/api/config');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
  if (!res.data.features) throw new Error('Missing features');
});

test('UI: Tags endpoint accessible', async () => {
  const res = await httpGet('/api/tags');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

test('UI: Changelog endpoint accessible', async () => {
  const res = await httpGet('/api/changelog');
  if (res.status !== 200) throw new Error(`Status ${res.status}`);
});

runTests().catch(err => {
  console.error('❌ Test runner error:', err);
  process.exit(1);
});
