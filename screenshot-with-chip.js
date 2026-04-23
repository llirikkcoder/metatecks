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

    console.log('Открываем dropdown и выбираем модель...');
    const brandWithModels = page.locator('a.js-filter-option[data-models]').first();
    await brandWithModels.click();
    await page.waitForTimeout(500);

    const firstModel = page.locator('.brand-dropdown__item').first();
    await firstModel.click();
    await page.waitForTimeout(500);

    // Ждем появления чипа
    const chip = page.locator('.chip').first();
    await chip.waitFor({ state: 'visible', timeout: 3000 });
    console.log('Чип появился');

    // Скриншот чипа
    await chip.screenshot({
      path: 'docs/chip-element.png'
    });
    console.log('✅ Скриншот чипа: docs/chip-element.png');

    // Скриншот блока selected-models
    const selectedBlock = page.locator('#selected-models');
    await selectedBlock.screenshot({
      path: 'docs/selected-models-block.png'
    });
    console.log('✅ Скриншот блока с чипами: docs/selected-models-block.png');

    // Выбираем еще одну модель
    console.log('Выбираем еще модели...');
    const brands = page.locator('a.js-filter-option[data-models]');
    await brands.nth(1).click();
    await page.waitForTimeout(500);
    await page.locator('.brand-dropdown__item').first().click();
    await page.waitForTimeout(300);

    await brands.nth(2).click();
    await page.waitForTimeout(500);
    await page.locator('.brand-dropdown__item').nth(1).click();
    await page.waitForTimeout(500);

    // Скриншот с несколькими чипами
    await selectedBlock.screenshot({
      path: 'docs/multiple-chips.png'
    });
    console.log('✅ Скриншот с несколькими чипами: docs/multiple-chips.png');

  } catch (error) {
    console.error('Ошибка:', error);
  } finally {
    await browser.close();
  }
})();
