import { expect, test } from '@playwright/test';

test.describe('인증 및 기본 내비게이션', () => {
  test('비로그인 사용자는 로그인 화면과 회원가입 화면에 접근할 수 있다', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /로그인/i })).toBeVisible();

    await page.goto('/signup');
    await expect(page).toHaveURL(/\/signup/);
    await expect(page.getByRole('heading', { name: /회원가입/i })).toBeVisible();
  });

  test('보호 화면은 인증이 없을 때 로그인 흐름으로 안내한다', async ({ page }) => {
    await page.goto('/notifications');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /로그인/i })).toBeVisible();
  });
});
