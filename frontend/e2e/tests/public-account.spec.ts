import { expect, test } from '@playwright/test';

test.describe('공개 계정 화면', () => {
  test('비밀번호 재설정 요청 화면에 접근할 수 있다', async ({ page }) => {
    await page.goto('/forgot-password');
    await expect(page.locator('body')).toBeVisible();
    await expect(page).toHaveURL(/\/forgot-password/);
  });

  test('이메일 인증 화면에 접근할 수 있다', async ({ page }) => {
    await page.goto('/verify-email');
    await expect(page.locator('body')).toBeVisible();
    await expect(page).toHaveURL(/\/verify-email/);
  });
});
