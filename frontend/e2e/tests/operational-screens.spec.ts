import { expect, test } from '@playwright/test';

test.describe('운영 안정화 화면', () => {
  test('알림 설정 화면은 직접 접근 가능한 라우트로 유지된다', async ({ page }) => {
    await page.goto('/settings/notifications');
    await expect(page).toHaveURL(/\/settings\/notifications/);
    await expect(page.getByText(/알림/i).first()).toBeVisible();
  });
});
