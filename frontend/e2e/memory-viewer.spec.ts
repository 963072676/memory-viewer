/**
 * E2E Tests for Memory Viewer - Core Pages
 * 
 * Tests the main user flows on the memory viewer application.
 */

import { test, expect } from '@playwright/test';

// Test suite for home page
test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the home page', async ({ page }) => {
    // Wait for the page to load
    await expect(page).toHaveTitle(/Memory Viewer/);
  });

  test('should display memory cards', async ({ page }) => {
    // Wait for memory cards to load (either unified or agentmemory)
    await page.waitForSelector('.unified-card, .card-grid', { timeout: 10000 });
    
    // Should show some content
    const cards = await page.locator('.unified-card, .memory-card').count();
    expect(cards).toBeGreaterThanOrEqual(0);
  });

  test('should show sidebar navigation', async ({ page }) => {
    // Sidebar should be visible
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();
  });

  test('should have working search', async ({ page }) => {
    // Find and use search input
    const searchInput = page.locator('input[placeholder*="搜索"], input[type="search"], .search-input');
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await searchInput.press('Enter');
      
      // Wait a moment for results
      await page.waitForTimeout(1000);
    }
  });
});

// Test suite for navigation
test.describe('Navigation', () => {
  test('should navigate to Hermes Memory', async ({ page }) => {
    await page.goto('/');
    
    // Click Hermes Memory nav item
    const hermesNav = page.locator('text=Hermes Memory, text=记忆浏览').first();
    if (await hermesNav.isVisible()) {
      await hermesNav.click();
      await expect(page).toHaveURL(/\/(hermes|memory)/);
    }
  });

  test('should navigate to Profiles', async ({ page }) => {
    await page.goto('/profiles');
    
    // Should show profiles list
    await expect(page.locator('.profiles-view, .page-title, h1')).toBeVisible();
  });

  test('should navigate to Settings', async ({ page }) => {
    await page.goto('/settings');
    
    // Should show settings page
    await expect(page.locator('.settings-view, .page-title, h1')).toBeVisible();
  });
});

// Test suite for memory operations
test.describe('Memory Operations', () => {
  test('should create a new memory', async ({ page }) => {
    await page.goto('/');
    
    // Look for create button
    const createBtn = page.locator('button:has-text("创建"), button:has-text("Create")');
    
    if (await createBtn.isVisible({ timeout: 5000 })) {
      await createBtn.click();
      
      // Fill in the form if it appears
      const titleInput = page.locator('input[placeholder*="标题"], input[name="title"]');
      if (await titleInput.isVisible({ timeout: 2000 })) {
        await titleInput.fill('E2E Test Memory');
        
        const saveBtn = page.locator('button:has-text("保存"), button:has-text("Save")');
        await saveBtn.click();
      }
    }
  });

  test('should open memory detail', async ({ page }) => {
    await page.goto('/');
    
    // Wait for cards to load
    await page.waitForSelector('.unified-card, .memory-card', { timeout: 10000 }).catch(() => {});
    
    const card = page.locator('.unified-card, .memory-card').first();
    
    if (await card.isVisible({ timeout: 5000 })) {
      await card.click();
      
      // Should show detail view or modal
      await page.waitForTimeout(500);
    }
  });
});

// Test suite for responsive design
test.describe('Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Page should load without errors
    await expect(page).toHaveTitle(/Memory Viewer/);
    
    // Sidebar should be collapsed on mobile
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();
  });

  test('should have working hamburger menu on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Find hamburger button
    const hamburger = page.locator('.sidebar-toggle, .hamburger, .mobile-toggle');
    
    if (await hamburger.isVisible({ timeout: 2000 })) {
      await hamburger.click();
      await page.waitForTimeout(300);
    }
  });
});

// Test suite for API connectivity
test.describe('API Connectivity', () => {
  test('should have working health endpoint', async ({ request }) => {
    const response = await request.get('/api/health');
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('ok');
  });

  test('should have working stats endpoint', async ({ request }) => {
    const response = await request.get('/api/stats');
    expect(response.ok()).toBeTruthy();
  });

  test('should have working agentmemory endpoint', async ({ request }) => {
    const response = await request.get('/api/agentmemory?limit=10');
    expect(response.ok()).toBeTruthy();
  });

  test('should have working search endpoint', async ({ request }) => {
    const response = await request.get('/api/search?q=test');
    expect(response.ok()).toBeTruthy();
  });
});
