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
    const filterSection = page.locator('.filtr-block__column-brends');
    await filterSection.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    // Находим первый бренд с моделями
    console.log('Открываем dropdown...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').first();
    const brandName = await brandWithModels.getAttribute('title');
    console.log(`Выбран бренд: ${brandName}`);

    // Кликаем на бренд
    await brandWithModels.click();
    await page.waitForTimeout(500);

    // Проверяем что dropdown открылся
    const dropdown = page.locator('#brandDropdown');
    await dropdown.waitFor({ state: 'visible', timeout: 5000 });
    console.log('Dropdown открыт');

    // Делаем скриншот только области фильтра
    console.log('Создаем скриншот фильтра...');
    const filterBlock = page.locator('.filtr-block__tabl');
    await filterBlock.screenshot({
      path: 'docs/dropdown-filter-area.png'
    });
    console.log('✅ Скриншот области фильтра: docs/dropdown-filter-area.png');

    // Также делаем полный скриншот страницы
    await page.screenshot({
      path: 'docs/dropdown-full-page.png',
      fullPage: false
    });
    console.log('✅ Полный скриншот: docs/dropdown-full-page.png');

    // Выбираем модель и делаем скриншот с чипом
    console.log('Выбираем модель...');
    const firstModel = page.locator('.brand-dropdown__item').first();
    const modelName = await firstModel.textContent();
    console.log(`Выбрана модель: ${modelName}`);
    await firstModel.click();
    await page.waitForTimeout(800);

    // Проверяем что чип появился
    const chip = page.locator('.chip').first();
    await chip.waitFor({ state: 'visible', timeout: 3000 });
    console.log('Чип появился');

    // Скриншот с чипом
    await filterBlock.screenshot({
      path: 'docs/dropdown-with-tag.png'
    });
    console.log('✅ Скриншот с тегом: docs/dropdown-with-tag.png');

  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    await browser.close();
  }
})();
