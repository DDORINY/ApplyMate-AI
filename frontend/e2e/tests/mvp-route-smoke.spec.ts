import { expect, test } from '@playwright/test';

const routes = [
  { path: '/dashboard', label: '대시보드', protected: false },
  { path: '/jobs', label: '공고', protected: true },
  { path: '/resumes', label: '이력서', protected: true },
  { path: '/documents', label: '지원 문서', protected: true },
  { path: '/applications', label: '지원 현황', protected: false },
  { path: '/calendar', label: '일정', protected: false },
  { path: '/recommendations', label: '추천', protected: false },
  { path: '/notifications', label: '알림', protected: true },
  { path: '/settings/integrations', label: '연동', protected: false },
  { path: '/settings/security', label: '보안', protected: false },
];

test.describe('MVP 주요 화면 라우트 smoke', () => {
  for (const route of routes) {
    test(`${route.label} 화면은 렌더링 실패 없이 응답한다`, async ({ page }) => {
      await page.goto(route.path);
      await expect(page.locator('body')).toBeVisible();
      const escaped = route.path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const expected = route.protected ? new RegExp(`(${escaped}|/login)`) : new RegExp(escaped);
      await expect(page).toHaveURL(expected);
    });
  }
});
