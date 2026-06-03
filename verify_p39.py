"""P39 完整验证:
1. 5 个 P3 404 API 全部 200
2. Dashboard 数据展示完整 (无 0 中间态闪烁)
3. StatsBar 与 Dashboard summary 数字一致
4. 不破坏上轮 P38 修复 (sidebar-collapse-btn / 3 个 webhook 端点)
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900})
        await ctx.add_init_script("""
            try { localStorage.setItem('setup-wizard-done', 'true');
                  localStorage.setItem('memory-viewer-last-read-version', '2.2.0'); } catch(e){}
        """)
        page = await ctx.new_page()

        results = {}

        # === 1. 5 个 P3 API 200 ===
        await page.goto('http://192.168.5.55:8501/agentmemory', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        mid = await page.evaluate("""() => {
            const c = document.querySelector('.memory-card');
            return c?.querySelector('a[href^=\"/memory/\"]')?.getAttribute('href')?.replace('/memory/', '') || null;
        }""")
        if not mid:
            # fallback: 用 fetch api
            mid = await page.evaluate("""async () => {
                const r = await fetch('/api/agentmemory');
                const d = await r.json();
                return d.memories?.[0]?.id;
            }""")
        print(f'using memory id: {mid}')

        if mid:
            for ep, method in [
                (f'/api/agentmemory/{mid}/decay', 'GET'),
                (f'/api/agentmemory/{mid}/health', 'GET'),
                (f'/api/agentmemory/{mid}/recommendations?limit=5', 'GET'),
                (f'/api/memories/{mid}/suggest-tags', 'POST'),
                (f'/api/memories/{mid}/summarize', 'POST'),
            ]:
                code = await page.evaluate(f"""async () => {{
                    const r = await fetch('{ep}', {{ method: '{method}' }});
                    return r.status;
                }}""")
                results[f'1. P3 API: {ep.split("/")[-1]}'] = code

        # === 2. Dashboard StatsBar + summary 数字一致 ===
        await page.goto('http://192.168.5.55:8501/dashboard', wait_until='networkidle')
        # 关键: 等 1500ms 让 fetch + count-up 完成
        await page.wait_for_timeout(2500)
        data = await page.evaluate("""() => {
            const stats = Array.from(document.querySelectorAll('.stat-item')).map(el => ({
                label: el.querySelector('span')?.textContent.trim(),
                value: el.querySelector('strong')?.textContent.trim()
            }));
            const summary = Array.from(document.querySelectorAll('.summary-card')).map(el => ({
                label: el.querySelector('.summary-label')?.textContent.trim(),
                value: el.querySelector('.summary-value')?.textContent.trim()
            }));
            return { stats, summary };
        }""")
        results['2. StatsBar'] = str(data['stats'])
        results['3. Dashboard summary'] = str(data['summary'])
        # 校验: total 数字应一致
        stats_total = next((s['value'] for s in data['stats'] if 'AgentMemory' in s['label']), '0')
        summary_total = next((s['value'] for s in data['summary'] if '总记忆数' in s['label']), '0')
        results['4. 一致性校验'] = f'StatsBar total={stats_total} vs Summary total={summary_total} → {"✓" if stats_total == summary_total else "✗"}'

        # === 5. 上轮 P38 修复没破坏 ===
        collapse = await page.evaluate("() => document.querySelectorAll('.sidebar-collapse-btn').length")
        results['5. P38 sidebar-collapse-btn = 0'] = str(collapse)

        webhook_codes = []
        for ep in ['/api/metrics/heatmap/summary?metric=created&days=7', '/api/webhook/config', '/api/notifications/feishu/config']:
            code = await page.evaluate(f"async () => (await fetch('{ep}')).status")
            webhook_codes.append((ep, code))
        results['6. P38 webhook/heatmap API 200'] = '; '.join(f'{ep}={c}' for ep, c in webhook_codes)

        # 输出
        print('='*60)
        for k, v in results.items():
            print(f'{k}: {v}')
        print('='*60)

        # 截图
        await page.screenshot(path='/tmp/p39_dashboard.png', full_page=False)
        await page.goto(f'http://192.168.5.55:8501/agentmemory', wait_until='networkidle')
        await page.wait_for_timeout(2500)
        await page.screenshot(path='/tmp/p39_agentmemory.png', full_page=False)
        await b.close()

asyncio.run(main())
