const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1200 }
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
    await brandFilter.scrollIntoViewIfNeeded({ block: 'center' });
    await page.waitForTimeout(500);

    // Кликаем на бренд
    console.log('Открываем dropdown...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').first();
    const brandName = await brandWithModels.getAttribute('title');
    console.log(`Выбран бренд: ${brandName}`);

    await brandWithModels.click();
    await page.waitForTimeout(800);

    // Проверяем что dropdown видим
    const dropdown = page.locator('#brandDropdown');
    await dropdown.waitFor({ state: 'visible', timeout: 5000 });
    console.log('Dropdown открыт');

    // Скроллим dropdown в центр экрана
    await dropdown.evaluate((el) => {
      el.scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await page.waitForTimeout(300);

    // Делаем скриншот вьюпорта
    console.log('Создаем скриншот вьюпорта...');
    await page.screenshot({
      path: 'docs/dropdown-viewport.png',
      fullPage: false
    });
    console.log('✅ Скриншот вьюпорта: docs/dropdown-viewport.png');

    // Делаем полный скриншот страницы
    console.log('Создаем полный скриншот...');
    await page.screenshot({
      path: 'docs/dropdown-fullpage.png',
      fullPage: true
    });
    console.log('✅ Полный скриншот: docs/dropdown-fullpage.png');

  } catch (error) {
    console.error('Ошибка:', error);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
})();
