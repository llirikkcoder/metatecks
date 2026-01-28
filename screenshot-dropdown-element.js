const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1200 }
  });
  const page = await context.newPage();

  try {
    console.log('Открываем страницу...');
    await page.goto('http://127.0.0.1:8080/catalog/mini-loaders/kovsh-osnovnoj/');
    await page.waitForLoadState('networkidle');

    console.log('Прокручиваем до фильтра...');
    const brandFilter = page.locator('#brand-filter');
    await brandFilter.scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);

    // Получаем координаты фильтра ДО открытия dropdown
    const filterBox = await brandFilter.boundingBox();
    console.log('Позиция фильтра:', filterBox);

    console.log('Открываем dropdown...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').first();
    const brandName = await brandWithModels.getAttribute('title');
    console.log(`Выбран бренд: ${brandName}`);

    await brandWithModels.click();
    await page.waitForTimeout(500);

    const dropdown = page.locator('#brandDropdown');
    await dropdown.waitFor({ state: 'visible', timeout: 5000 });
    console.log('Dropdown открыт');

    // Делаем скриншот самого dropdown элемента
    console.log('Скриншот dropdown элемента...');
    await dropdown.screenshot({
      path: 'docs/dropdown-element.png'
    });
    console.log('✅ Скриншот dropdown: docs/dropdown-element.png');

    // Также делаем скриншот без прокрутки
    console.log('Скриншот вьюпорта (без прокрутки)...');
    await page.screenshot({
      path: 'docs/dropdown-view.png',
      fullPage: false
    });
    console.log('✅ Скриншот вьюпорта: docs/dropdown-view.png');

    // Выбираем модель
    console.log('Выбираем модель...');
    const firstModel = page.locator('.brand-dropdown__item').first();
    await firstModel.click();
    await page.waitForTimeout(500);

    // Ждем появления чипа
    const chip = page.locator('.chip').first();
    await chip.waitFor({ state: 'visible', timeout: 3000 });
    console.log('Чип появился');

    // Скриншот фильтра с чипом
    const filterSection = page.locator('.filtr-block__tabl');
    await filterSection.screenshot({
      path: 'docs/filter-with-chip.png'
    });
    console.log('✅ Скриншот с чипом: docs/filter-with-chip.png');

  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    await browser.close();
  }
})();
