
/* === ДОПОЛНЕНИЯ В ФИЛЬТР === */

// Весь код запускаем после построения DOM
document.addEventListener('DOMContentLoaded', () => {
	// Узлы
	const brandFilter = document.getElementById('brand-filter');
	const dropdown = document.getElementById('brandDropdown');
	const ddTitle = document.getElementById('brandDropdownTitle');
	const ddList = document.getElementById('brandDropdownList');
	const ddClose = document.getElementById('brandDropdownClose');
	const selectedWrap = document.getElementById('selected-models');
	const resetBtn = document.getElementById('reset-filters');

	if (!brandFilter || !dropdown || !ddList) {
		console.error('Не найдены ключевые узлы фильтра.');
		return;
	}

	// Хранилище выбранных (ключ: "Бренд|Модель")
	const selected = new Map();

	// Открыть дропдаун у конкретной кнопки бренда
	function openDropdownForBrand(brandBtn) {
		const brand = (brandBtn.getAttribute('title') || brandBtn.textContent).trim();

		// Модели берём ТОЛЬКО из data-models у кнопки
		let models = [];
		const raw = brandBtn.dataset.models;
		if (raw) {
			try { models = JSON.parse(raw); }
			catch (e) { console.warn('Некорректный JSON в data-models у бренда', brand, e); models = []; }
		}

		// Заголовок
		ddTitle.textContent = `Модели ${brand}`;

		// Контент
		ddList.innerHTML = '';
		if (!Array.isArray(models) || models.length === 0) {
			const empty = document.createElement('div');
			empty.className = 'brand-dropdown__item';
			empty.textContent = 'Нет предустановленных моделей';
			empty.setAttribute('aria-disabled', 'true');
			ddList.appendChild(empty);
		} else {
			models.forEach(model => {
				const item = document.createElement('button');
				item.type = 'button';
				item.className = 'brand-dropdown__item';
				item.textContent = model;
				item.dataset.brand = brand;
				item.dataset.model = model;
				item.setAttribute('role', 'option');
				const key = `${brand}|${model}`;
				if (selected.has(key)) item.setAttribute('aria-selected', 'true');
				ddList.appendChild(item);
			});
		}

		// Позиционирование: ниже кнопки, если не влезает — выше
		const rect = brandBtn.getBoundingClientRect();
		const scrollY = window.scrollY || document.documentElement.scrollTop;
		const scrollX = window.scrollX || document.documentElement.scrollLeft;
		dropdown.style.left = Math.max(8, rect.left + scrollX) + 'px';

		// временно покажем, чтобы узнать высоту
		dropdown.hidden = false;
		const ddH = dropdown.offsetHeight || 340;
		const belowTop = rect.bottom + scrollY + 8;
		const aboveTop = rect.top + scrollY - ddH - 8;
		const viewportBottom = window.innerHeight + scrollY;
		const willOverflow = belowTop + ddH > viewportBottom;
		dropdown.style.top = (willOverflow && aboveTop > 0 ? aboveTop : belowTop) + 'px';

		// Подсветка активной кнопки
		document.querySelectorAll('#brand-filter .btn-small.is-open').forEach(b => b.classList.remove('is-open'));
		brandBtn.classList.add('is-open');
	}

	// Закрыть дропдаун
	function closeDropdown() {
		dropdown.hidden = true;
		document.querySelectorAll('#brand-filter .btn-small.is-open').forEach(b => b.classList.remove('is-open'));
	}

	// Добавить чип (выбранную модель)
	function addChip(brand, model) {
		const key = `${brand}|${model}`;
		if (selected.has(key)) return;
		selected.set(key, { brand, model });

		const chip = document.createElement('div');
		chip.className = 'chip';
		chip.dataset.key = key;
		chip.innerHTML = `<span>${brand} ${model}</span>
          <button type="button" class="chip__remove" aria-label="Убрать ${brand} ${model}">×</button>`;
		selectedWrap.appendChild(chip);
	}

	// Удалить чип
	function removeChipByKey(key) {
		selected.delete(key);
		// простая выборка без экранирования, т.к. ключ формируем сами
		const chip = selectedWrap.querySelector('.chip[data-key="' + key.replace(/"/g, '\\"') + '"]');
		if (chip) chip.remove();
	}

	// Делегирование кликов по брендам
	brandFilter.addEventListener('click', (e) => {
		const btn = e.target.closest('.btn-small');
		if (!btn) return;
		e.preventDefault();                 // отключаем переход по "#"
		openDropdownForBrand(btn);
	});

	// Клик по модели
	ddList.addEventListener('click', (e) => {
		const item = e.target.closest('.brand-dropdown__item');
		if (!item || item.getAttribute('aria-disabled') === 'true') return;
		const { brand, model } = item.dataset;
		addChip(brand, model);
		closeDropdown();
	});

	// Закрытия
	ddClose.addEventListener('click', closeDropdown);
	document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDropdown(); });
	document.addEventListener('click', (e) => {
		if (dropdown.hidden) return;
		const isInside = e.target.closest('#brandDropdown') || e.target.closest('#brand-filter');
		if (!isInside) closeDropdown();
	});

	// Удаление чипов
	selectedWrap.addEventListener('click', (e) => {
		const rm = e.target.closest('.chip__remove');
		if (!rm) return;
		const chip = rm.closest('.chip');
		const key = chip.dataset.key;
		removeChipByKey(key);
	});

	// Сброс
	resetBtn.addEventListener('click', () => {
		selected.clear();
		selectedWrap.innerHTML = '';
		closeDropdown();
	});

	// Мелочь: не скроллить страницу по клику на "#" ссылки
	document.querySelectorAll('.filtr-block a[href="#"]').forEach(a => {
		a.addEventListener('click', (e) => e.preventDefault());
	});
});