const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Открываем страницу
    console.log('Открываем страницу...');
    await page.goto('http://127.0.0.1:8080/catalog/mini-loaders/kovsh-osnovnoj/');
    await page.waitForLoadState('networkidle');

    // Прокручиваем до фильтра
    console.log('Прокручиваем до фильтра...');
    const brandFilter = page.locator('#brand-filter');
    await brandFilter.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    // Находим первый бренд с моделями
    console.log('Открываем dropdown...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').first();
    const brandName = await brandWithModels.getAttribute('title');
    console.log(`Выбран бренд: ${brandName}`);

    // Кликаем на бренд
    await brandWithModels.click();
    await page.waitForTimeout(300);

    // Проверяем что dropdown открылся
    const dropdown = page.locator('#brandDropdown');
    await dropdown.waitFor({ state: 'visible', timeout: 5000 });

    // Делаем скриншот с открытым dropdown
    console.log('Создаем скриншот...');
    await page.screenshot({
      path: 'docs/dropdown-screenshot.png',
      fullPage: false
    });
    console.log('✅ Скриншот сохранен: docs/dropdown-screenshot.png');

    // Дополнительно: кликаем на модель и делаем скриншот с тегом
    const firstModel = page.locator('.brand-dropdown__item').first();
    await firstModel.click();
    await page.waitForTimeout(500);

    await page.screenshot({
      path: 'docs/dropdown-with-chip.png',
      fullPage: false
    });
    console.log('✅ Скриншот с тегом сохранен: docs/dropdown-with-chip.png');

  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    await browser.close();
  }
})();
