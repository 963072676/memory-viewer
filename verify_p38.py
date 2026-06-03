"""
P38 完整验证 — 5 个修复:
1. WEB 端无 sidebar-collapse-btn
2. 3 个 404 API 端点全部 200
3. memory-card select-checkbox 不遮挡 card-title
4. profile 链接带 ?profile=xxx
5. 菜单点击不跳转 — chunk 全部 200
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

        # === #1: 桌面端无 sidebar-collapse-btn ===
        await page.goto('http://192.168.5.55:8501/dashboard', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        collapse_count = await page.evaluate("() => document.querySelectorAll('.sidebar-collapse-btn').length")
        results['1. WEB端无 sidebar-collapse-btn'] = f'count={collapse_count} (期望 0)'

        # === #2: 3 个 API 端点 ===
        apis = [
            ('/api/metrics/heatmap/summary?metric=created&days=365', 'GET'),
            ('/api/webhook/config', 'GET'),
            ('/api/notifications/feishu/config', 'GET'),
        ]
        api_results = []
        for url, method in apis:
            r = await page.evaluate(f"""async () => {{
                const r = await fetch('{url}', {{ method: '{method}' }});
                return r.status;
            }}""")
            api_results.append(f'{url}={r}')
        results['2. 3 个 404 API 已修复'] = '; '.join(api_results)

        # === #3: memory-card select-checkbox 不遮挡 title ===
        # 去 agentmemory 看 memory-card
        await page.goto('http://192.168.5.55:8501/agentmemory', wait_until='networkidle')
        await page.wait_for_timeout(2500)
        # 找第一个 memory-card
        card_info = await page.evaluate("""() => {
            const card = document.querySelector('.memory-card');
            if (!card) return { found: false };
            const checkbox = card.querySelector('.select-checkbox');
            const titleRow = card.querySelector('.card-title-row');
            const title = card.querySelector('.card-title');
            if (!checkbox || !titleRow || !title) return { found: false, why: 'missing elements' };
            const cbRect = checkbox.getBoundingClientRect();
            const tRect = title.getBoundingClientRect();
            return {
                found: true,
                checkbox_right: cbRect.right,
                title_left: tRect.left,
                title_text: title.textContent.trim().substring(0, 30),
                title_row_padding_left: getComputedStyle(titleRow).paddingLeft,
                ok: cbRect.right <= tRect.left + 2  // checkbox 不应压到 title
            };
        }""")
        results['3. memory-card checkbox 不遮挡 title'] = str(card_info)

        # === #4: profile 链接带 query ===
        await page.goto('http://192.168.5.55:8501/profiles', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        links = await page.evaluate("() => Array.from(document.querySelectorAll('a.profile-link')).map(a => a.getAttribute('href'))")
        all_have_query = all('?profile=' in l for l in links) and len(links) >= 5
        results['4. profile 链接带 query'] = f'all_have_query={all_have_query}, links={links}'

        # === #5: 菜单点击跳转 + chunk 200 ===
        bad_responses = []
        page.on('response', lambda r: bad_responses.append((r.status, r.url)) if r.status >= 400 and '/assets/' in r.url else None)
        # 在 / 页面,直接 router.push 到每个 path 验证 chunk 200,然后用 url 验证 SPA 切换
        await page.goto('http://192.168.5.55:8501/', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        nav_paths = ['/agentmemory', '/hermes', '/profiles', '/dashboard', '/collections', '/compare', '/sources', '/settings']
        nav_results = []
        for path in nav_paths:
            # 点 sidebar 内 href 包含该 path 的 nav-item
            try:
                link = await page.query_selector(f'.nav-item[href$="{path}"]')
                if link:
                    await link.click()
                    await page.wait_for_timeout(1200)
                    cur = page.url.replace('http://192.168.5.55:8501', '').rstrip('/')
                    target = path.rstrip('/')
                    ok = cur == target
                    nav_results.append(f'{path}→{cur} {"✓" if ok else "✗"}')
                else:
                    nav_results.append(f'{path} not-found')
            except Exception as e:
                nav_results.append(f'{path} ERR: {str(e)[:60]}')
        results['5. 全部菜单跳转'] = f'chunk 404 数: {len(bad_responses)}; nav: {nav_results}'

        # 输出
        print('='*60)
        for k, v in results.items():
            print(f'{k}: {v}')
        print('='*60)

        # 截图
        await page.goto('http://192.168.5.55:8501/agentmemory', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/tmp/p38_agentmemory.png', full_page=False)
        await page.goto('http://192.168.5.55:8501/dashboard', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/tmp/p38_dashboard.png', full_page=False)

        await b.close()

asyncio.run(main())
