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
    await brandFilter.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);

    // Кликаем на бренд
    console.log('Открываем dropdown...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').nth(1); // Берем второй бренд
    const brandName = await brandWithModels.getAttribute('title');
    console.log(`Выбран бренд: ${brandName}`);

    await brandWithModels.click();
    await page.waitForTimeout(500);

    // Проверяем что dropdown видим
    const dropdown = page.locator('#brandDropdown');
    await dropdown.waitFor({ state: 'visible', timeout: 5000 });

    const isVisible = await dropdown.isVisible();
    console.log('Dropdown видим:', isVisible);

    // Получаем позицию dropdown
    const box = await dropdown.boundingBox();
    console.log('Позиция dropdown:', box);

    // Делаем скриншот всего вьюпорта
    console.log('Создаем скриншот...');
    await page.screenshot({
      path: 'docs/dropdown-opened.png',
      fullPage: false
    });
    console.log('✅ Скриншот сохранен: docs/dropdown-opened.png');

    // Делаем clip screenshot вокруг dropdown
    if (box) {
      const clipBox = {
        x: Math.max(0, box.x - 50),
        y: Math.max(0, box.y - 100),
        width: box.width + 100,
        height: box.height + 150
      };

      await page.screenshot({
        path: 'docs/dropdown-closeup.png',
        clip: clipBox
      });
      console.log('✅ Крупный план dropdown: docs/dropdown-closeup.png');
    }

  } catch (error) {
    console.error('Ошибка:', error);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
})();
