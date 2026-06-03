"""
验证 3 个 P0 修复:
1. 移动端内容区不被顶栏遮挡
2. 顶栏菜单按钮点击可触发 bottom sheet
3. 底 Tab Bar 长 label 不换行，与 icon 对齐
"""
import asyncio, json
from playwright.async_api import async_playwright

PAGES = ['/', '/agentmemory', '/hermes', '/profiles', '/dashboard', '/collections', '/compare', '/sources', '/settings']

async def check(page, viewport, url):
    issues = []
    # 1) 顶栏 z-index 50 fixed，应在视口最上方 56px 区域
    header = await page.query_selector('.app-header')
    if header:
        box = await header.bounding_box()
        if box and box['y'] != 0 and viewport['width'] < 768:
            issues.append(f'顶栏 y={box["y"]:.0f} (应为 0，fixed)')
        if box and box['width'] > viewport['width'] + 1:
            issues.append(f'顶栏 width={box["width"]:.0f} > viewport')
    # 2) main-wrapper 应有 padding-top > 0
    main = await page.query_selector('.main-wrapper')
    if main:
        css = await main.evaluate("el => getComputedStyle(el).paddingTop")
        padding_top = float(css.replace('px','')) if css.endswith('px') else 0
        if viewport['width'] < 768 and padding_top < 50:
            issues.append(f'main-wrapper padding-top={padding_top:.0f} < 50 (顶栏 56px 留位)')
    # 3) 底 Tab Bar
    tabbar = await page.query_selector('.mobile-tab-bar')
    if viewport['width'] < 768:
        if not tabbar:
            issues.append('移动端缺 .mobile-tab-bar')
        else:
            box = await tabbar.bounding_box()
            if box:
                # 底 Tab Bar 应在视口底部
                if box['y'] + box['height'] < viewport['height'] - 5:
                    issues.append(f'底 Tab Bar 未贴底: bottom={box["y"]+box["height"]:.0f} < viewport {viewport["height"]}')
                # tab-item label 不换行
                labels = await page.query_selector_all('.tab-item .tab-label')
                for i, lab in enumerate(labels):
                    lab_box = await lab.bounding_box()
                    if not lab_box: continue
                    # 文字溢出检测:label 高度 < 16 表示单行
                    if lab_box['height'] > 18:
                        issues.append(f'tab[{i}] label 高度 {lab_box["height"]:.0f} > 18 (疑似换行)')
                    # label 宽度不应超出其 tab-item
                    parent = await lab.evaluate_handle("el => el.closest('.tab-item')")
                    parent_box = await parent.as_element().bounding_box()
                    if parent_box and lab_box['width'] > parent_box['width'] + 2:
                        issues.append(f'tab[{i}] label 宽 {lab_box["width"]:.0f} > tab {parent_box["width"]:.0f}')
    return issues

async def click_menu_check_sheet(page):
    """点顶栏菜单按钮 → 期望出现 bottom-sheet"""
    btn = await page.query_selector('.sidebar-toggle')
    if not btn: return 'no-button'
    await btn.click()
    await page.wait_for_timeout(500)
    sheet = await page.query_selector('.bottom-sheet')
    if sheet:
        visible = await sheet.is_visible()
        if visible:
            # 关闭
            overlay = await page.query_selector('.bottom-sheet-overlay')
            if overlay:
                await overlay.click()
            return 'opened'
        return 'sheet-not-visible'
    return 'no-sheet'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        results = {}
        # ===== Mobile 390 =====
        for w in [390, 1440]:
            ctx = await browser.new_context(viewport={'width': w, 'height': 844}, device_scale_factor=2)
            # 强制禁用 onboarding tour / setup wizard / whats-new
            await ctx.add_init_script("""
                try {
                    localStorage.setItem('memory-viewer-onboarding-done', 'true');
                    localStorage.setItem('memory-viewer-tour-skipped', 'true');
                    localStorage.setItem('onboarding-completed', 'true');
                    localStorage.setItem('setup-wizard-done', 'true');
                    localStorage.setItem('memory-viewer-last-read-version', '2.2.0');
                } catch (e) {}
            """)
            page = await ctx.new_page()
            console_errs = []
            page.on('console', lambda msg: console_errs.append(msg.text) if msg.type == 'error' else None)
            page.on('pageerror', lambda exc: console_errs.append(f'PAGEERROR: {exc}'))
            for path in PAGES:
                url = f'http://192.168.5.55:8501{path}'
                try:
                    await page.goto(url, wait_until='networkidle', timeout=15000)
                except Exception as e:
                    results[f'{w}|{path}'] = {'load': 'fail', 'err': str(e)[:100]}
                    continue
                await page.wait_for_timeout(800)
                issues = await check(page, {'width': w, 'height': 844}, url)
                results[f'{w}|{path}'] = {
                    'issues': issues,
                    'console_errors': console_errs.copy() if console_errs else [],
                }
                console_errs.clear()
            # 单独验证菜单按钮（仅 mobile）
            if w == 390:
                await page.goto('http://192.168.5.55:8501/', wait_until='networkidle')
                await page.wait_for_timeout(500)
                r = await click_menu_check_sheet(page)
                results['menu-click'] = r
            await ctx.close()
        await browser.close()
        # 打印
        bad = 0
        for k, v in results.items():
            if k == 'menu-click':
                ok = v == 'opened'
                print(f'{"✅" if ok else "❌"} {k}: {v}')
                if not ok: bad += 1
                continue
            if v.get('issues') or v.get('console_errors') or v.get('load') == 'fail':
                print(f'❌ {k}: {v}')
                bad += 1
            else:
                print(f'✅ {k}')
        print(f'\n=== {bad} bad / {len(results)} total ===')
        if bad:
            failed = {k:v for k,v in results.items()
                      if (k != 'menu-click' and (v.get('issues') or v.get('console_errors') or v.get('load') == 'fail'))
                      or (k == 'menu-click' and v != 'opened')}
            print(json.dumps(failed, indent=2, ensure_ascii=False))

asyncio.run(main())
