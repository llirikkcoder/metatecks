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

	// Переносим dropdown в body, чтобы position:absolute работал от документа
	document.body.appendChild(dropdown);

	// Хранилище выбранных (ключ: "Бренд|Модель")
	const selected = new Map();

	// Синхронизация выбранных моделей с фильтром filter.js и запуск AJAX
	function syncModelsToFilter() {
		const pairs = [];
		for (const [key, val] of selected) {
			pairs.push(`${val.brand}|${val.model}`);
		}
		// _filter и loadProducts определены в filter.js (загружается после model_filter.js)
		if (typeof _filter !== 'undefined') {
			_filter['models'] = pairs;
		}
		if (typeof setOffset === 'function') { setOffset(0); }
		if (typeof loadProducts === 'function') { loadProducts(); }
	}

	// Открыть дропдаун у конкретной кнопки бренда
	function openDropdownForBrand(brandBtn) {
		const brand = (brandBtn.getAttribute('title') || brandBtn.textContent).trim();
		const brandId = brandBtn.dataset.value; // ID бренда из data-value

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
				item.dataset.brandId = brandId;
				item.setAttribute('role', 'option');
				const key = `${brand}|${model}`;
				if (selected.has(key)) item.setAttribute('aria-selected', 'true');
				ddList.appendChild(item);
			});
		}

		// Позиционирование (fixed — координаты viewport, работает всегда)
		const rect = brandBtn.getBoundingClientRect();
		dropdown.style.position = 'fixed';
		dropdown.style.left = Math.max(8, rect.left) + 'px';

		// временно покажем, чтобы узнать высоту
		dropdown.hidden = false;
		const ddH = dropdown.offsetHeight || 340;
		const belowTop = rect.bottom + 4;
		const aboveTop = rect.top - ddH - 4;
		const willOverflow = (belowTop + ddH) > window.innerHeight;
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
	function addChip(brand, model, brandId) {
		const key = `${brand}|${model}`;
		if (selected.has(key)) return;
		selected.set(key, { brand, model, brandId });

		const chip = document.createElement('div');
		chip.className = 'chip';
		chip.dataset.key = key;
		chip.innerHTML = `<span>${brand} ${model}</span>
          <button type="button" class="chip__remove" aria-label="Убрать ${brand} ${model}">×</button>`;
		selectedWrap.appendChild(chip);

		// Включаем бренд в фильтр (если ещё не выбран)
		if (brandId && typeof _filter !== 'undefined') {
			const bid = parseInt(brandId);
			if (_filter['brand'].indexOf(bid) === -1) {
				_filter['brand'].push(bid);
				_filter['brand'].sort();
			}
			// Визуально отмечаем кнопку бренда
			const btn = brandFilter.querySelector('.js-filter-option[data-value="' + bid + '"]');
			if (btn) btn.classList.add('btn--filtr--select');
		}

		syncModelsToFilter();
	}

	// Удалить чип
	function removeChipByKey(key) {
		const removed = selected.get(key);
		selected.delete(key);
		const chip = selectedWrap.querySelector('.chip[data-key="' + key + '"]');
		if (chip) {
			chip.remove();
		}

		// Если это был последний чип бренда — убираем бренд из фильтра
		if (removed && removed.brandId && typeof _filter !== 'undefined') {
			let hasOther = false;
			for (const [, v] of selected) {
				if (v.brandId === removed.brandId) { hasOther = true; break; }
			}
			if (!hasOther) {
				const bid = parseInt(removed.brandId);
				_filter['brand'] = _filter['brand'].filter(function(id) { return id !== bid; });
				const btn = brandFilter.querySelector('.js-filter-option[data-value="' + bid + '"]');
				if (btn) btn.classList.remove('btn--filtr--select');
			}
		}

		syncModelsToFilter();
	}

	// Клик по бренду - открыть dropdown (capture phase, но НЕ блокируем jQuery-фильтрацию)
	document.addEventListener('click', (e) => {
		const btn = e.target.closest('.js-filter-option');
		// Проверяем что клик был на кнопке бренда внутри brandFilter и есть data-models
		if (btn && btn.dataset.models && brandFilter.contains(btn)) {
			openDropdownForBrand(btn);
			// НЕ вызываем stopImmediatePropagation — пусть jQuery-обработчик
			// в filter.js тоже сработает и выполнит фильтрацию по бренду
		}
	}, true); // true = capture phase (срабатывает до bubbling)

	// Клик по кнопке закрытия dropdown
	ddClose.addEventListener('click', (e) => {
		closeDropdown();
		e.stopPropagation();
	});

	// Клик по модели в dropdown - добавить чип
	ddList.addEventListener('click', (e) => {
		const item = e.target.closest('.brand-dropdown__item');
		if (item && item.dataset.brand && item.dataset.model && !item.getAttribute('aria-disabled')) {
			addChip(item.dataset.brand, item.dataset.model, item.dataset.brandId);
			closeDropdown();
		}
	});

	// Клик по чипу - удалить
	selectedWrap.addEventListener('click', (e) => {
		const removeBtn = e.target.closest('.chip__remove');
		if (removeBtn) {
			const chip = removeBtn.closest('.chip');
			if (chip) {
				removeChipByKey(chip.dataset.key);
			}
			e.stopPropagation();
		}
	});

	// Кнопка сброса фильтра
	if (resetBtn) {
		resetBtn.addEventListener('click', () => {
			selected.clear();
			selectedWrap.innerHTML = '';
			// Очищаем models в _filter (loadProducts вызовет filter.js через jQuery-обработчик)
			if (typeof _filter !== 'undefined') {
				_filter['models'] = [];
			}
		});
	}

	// Закрыть dropdown при клике вне его
	document.addEventListener('click', (e) => {
		if (!dropdown.hidden && !dropdown.contains(e.target) && !brandFilter.contains(e.target)) {
			closeDropdown();
		}
	});

	// Закрыть dropdown при ESC
	document.addEventListener('keydown', (e) => {
		if (e.key === 'Escape' && !dropdown.hidden) {
			closeDropdown();
		}
	});

	// Закрыть dropdown при скролле (fixed-позиция не двигается со страницей)
	window.addEventListener('scroll', () => {
		if (!dropdown.hidden) closeDropdown();
	}, { passive: true });
});
