/* ====== Выпадающее меню каталога ====== */

/* Когда пользователь нажимает на кнопку, переключается между скрытием и отображением выпадающего контента */
function myFunction() {
	document.getElementById("navcatalog").classList.toggle("dropdown--show");
	var element = document.body;
	element.classList.toggle("open");
}

/* Когда пользователь нажимает на кнопку склада № 1, переключается между скрытием и отображением выпадающего контента */
function toggleОne() {
	document.getElementById("blockinfone").classList.toggle("blockinfone--show");
	var element = document.body;
	element.classList.toggle("openone");
}

/* Когда пользователь нажимает на кнопку склада № 1, переключается между скрытием и отображением выпадающего контента */
function toggleSec() {
	document.getElementById("blockinfsecond").classList.toggle("blockinfsecond--show");
	var element = document.body;
	element.classList.toggle("opensecond");
}

// Вкладки в меню каталога
function showTab(elTabBtn) {
	const elTab = elTabBtn.closest('.nav-catalog__tab');
	if (elTabBtn.classList.contains('nav-catalog__tabbtn--active')) {
		return;
	}
	const targetId = elTabBtn.dataset.targetId;
	const elTabPane = elTab.querySelector(`.nav-catalog__tabcontent[data-id="${targetId}"]`);
	if (elTabPane) {
		const elTabBtnActive = elTab.querySelector('.nav-catalog__tabbtn--active');
		elTabBtnActive.classList.remove('nav-catalog__tabbtn--active');
		const elTabPaneShow = elTab.querySelector('.nav-catalog__tabcontent--show');
		elTabPaneShow.classList.remove('nav-catalog__tabcontent--show');
		elTabBtn.classList.add('nav-catalog__tabbtn--active');
		elTabPane.classList.add('nav-catalog__tabcontent--show');
	}
}

document.addEventListener('click', (e) => {
	if (e.target && !e.target.closest('.nav-catalog__tabbtn')) {
		return;
	}
	const elTabBtn = e.target.closest('.nav-catalog__tabbtn');
	showTab(elTabBtn);
});

// кнопка боковой панели
document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.querySelector('.aside-sidebar');
  const toggle = document.querySelector('.sidebar-toggle');

  if (sidebar && toggle) {
    toggle.addEventListener('click', function() {
      sidebar.classList.toggle('open-aside');
    });
  }
});

// кнопка бургер главного меню в мобильной версии
$(function () {
	$('#icon-burger').on('click', function () {
		$('body').toggleClass('open-main-menu');
	});
});

// Кастомизировать скроллбар в таблицу характеристик
document.addEventListener('DOMContentLoaded', function () {
	const setups = [
		{
			containerClass: 'scrollbar-box__container',
			scrollbarClass: 'scrollbar',
			thumbClass: 'thumb'
		},
		{
			containerClass: 'scrollbar-box__container2',
			scrollbarClass: 'scrollbar2',
			thumbClass: 'thumb2'
		}
	];

	setups.forEach((setup) => {
		const tableContainer = document.querySelector(`.${setup.containerClass}`);
		const scrollbar = document.querySelector(`.${setup.scrollbarClass}`);
		const thumb = document.querySelector(`.${setup.scrollbarClass} .${setup.thumbClass}`);

		if (!tableContainer || !scrollbar || !thumb) {
			return; // Прекращаем выполнение текущей итерации, если один из элементов не найден
		}

		const updateScrollbar = () => {
			const containerWidth = tableContainer.clientWidth;
			const contentWidth = tableContainer.scrollWidth;
			const scrollbarWidth = scrollbar.clientWidth;

			// Вычисляем ширину и позицию ползунка
			const thumbWidth = Math.max((containerWidth / contentWidth) * scrollbarWidth, 30);
			const thumbLeft = (tableContainer.scrollLeft / (contentWidth - containerWidth)) * (scrollbarWidth - thumbWidth);

			thumb.style.width = `${thumbWidth}px`;
			thumb.style.transform = `translateX(${thumbLeft}px)`;

			if (contentWidth <= containerWidth) {
				scrollbar.style.display = 'none';
			} else {
				scrollbar.style.display = 'block';
			}
		};

		tableContainer.addEventListener('scroll', updateScrollbar);
		window.addEventListener('resize', updateScrollbar);

		let isDragging = false;
		let startX;

		thumb.addEventListener('mousedown', (e) => {
			isDragging = true;
			startX = e.clientX - thumb.getBoundingClientRect().left;
			document.body.style.userSelect = 'none'; // Отключаем выделение текста
		});

		document.addEventListener('mousemove', (e) => {
			if (isDragging) {
				const deltaX = e.clientX - startX;
				const maxLeft = scrollbar.clientWidth - thumb.clientWidth;
				const thumbLeft = Math.min(Math.max(0, deltaX), maxLeft);
				const scrollPercent = thumbLeft / maxLeft;

				tableContainer.scrollLeft = scrollPercent * (tableContainer.scrollWidth - tableContainer.clientWidth);
				thumb.style.transform = `translateX(${thumbLeft}px)`;
			}
		});

		document.addEventListener('mouseup', () => {
			isDragging = false;
			document.body.style.userSelect = ''; // Включаем выделение текста
		});

		// Инициализация скроллбара
		updateScrollbar();
	});

	// Выстраивать контент в 4 строки
	const container = document.getElementById('scrollbar-box');
	if (container) {
		const maxLines = 4; // Устанавливаем количество строк на 4
		const button = container.querySelector('.btn-small');
		const buttonHeight = button ? button.offsetHeight + 10 : 0; // Высота кнопки плюс отступ
		const maxHeight = maxLines * buttonHeight;

		function adjustContainer() {
			if (!button) return;

			container.style.maxHeight = `${maxHeight}px`;

			// Начальная установка ширины
			let totalHeight = container.scrollHeight;
			let currentWidth = container.clientWidth;

			// Увеличиваем ширину до тех пор, пока все элементы не поместятся в 4 строки
			while (totalHeight > maxHeight) {
				currentWidth += 10; // Увеличиваем ширину на 10px
				container.style.width = `${currentWidth}px`;
				totalHeight = container.scrollHeight;
			}
		}

		adjustContainer();
		window.addEventListener('resize', adjustContainer);
	}
});

// Скроллер-бар с годами
document.addEventListener('DOMContentLoaded', function() {
    const yearsContainer = document.querySelector('.nav-years');
    const yearsWrapper = document.querySelector('.nav-years__wrapp');
    const leftArrow = document.querySelector('.nav-years__arrow.years-arrow-left');
    const rightArrow = document.querySelector('.nav-years__arrow.years-arrow-right');

    if (yearsContainer && yearsWrapper && leftArrow && rightArrow) {
        const updateArrowsVisibility = () => {
            requestAnimationFrame(() => {
                leftArrow.classList.toggle('hidden', yearsWrapper.scrollLeft === 0);
                rightArrow.classList.toggle('hidden', yearsWrapper.scrollWidth <= yearsWrapper.clientWidth + yearsWrapper.scrollLeft);
            });
        };

        leftArrow.addEventListener('click', () => {
            yearsWrapper.scrollBy({ left: -200, behavior: 'smooth' });
        });

        rightArrow.addEventListener('click', () => {
            yearsWrapper.scrollBy({ left: 200, behavior: 'smooth' });
        });

        window.addEventListener('resize', updateArrowsVisibility);
        yearsWrapper.addEventListener('scroll', updateArrowsVisibility);

        updateArrowsVisibility();

        // Touch scroll (для мобильных устройств)
        yearsWrapper.addEventListener('touchstart', (e) => {
            isDown = true;
            startX = e.touches[0].pageX - yearsWrapper.offsetLeft;
            scrollLeft = yearsWrapper.scrollLeft;
            document.body.style.userSelect = 'none'; // Запрещаем выделение текста
        });

        yearsWrapper.addEventListener('touchend', () => {
            isDown = false;
            document.body.style.userSelect = ''; // Включаем выделение текста
        });

        yearsWrapper.addEventListener('touchmove', (e) => {
            if (!isDown) return;
            const x = e.touches[0].pageX - yearsWrapper.offsetLeft;
            const walk = (x - startX) * 1.5; // множитель прокрутки
            yearsWrapper.scrollLeft = scrollLeft - walk;
        });

        // Обновляем видимость стрелок после загрузки
        updateArrowsVisibility();
    }
});

// Бегущая строка
document.addEventListener('DOMContentLoaded', () => {
  const marqueeContainers = document.querySelectorAll('.scrolling-track');

  marqueeContainers.forEach(marqueeInner => {
    const marqueeItems = marqueeInner.querySelectorAll('.scrolling-item');

    // Клонируем элементы, чтобы заполнить бегущую строку
    marqueeItems.forEach(item => {
      const clone = item.cloneNode(true);
      marqueeInner.appendChild(clone);
    });
  });
});
document.addEventListener('DOMContentLoaded', () => {
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            item.classList.toggle('accordion--item--active');

            // Закрытие других вкладок
            accordionHeaders.forEach(h => {
                if (h !== header && h.parentElement.classList.contains('accordion--item--active')) {
                    h.parentElement.classList.remove('accordion--item--active');
                }
            });

            // Прокрутка к верху открытого блока
            if (item.classList.contains('accordion--item--active')) {
                item.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});


// Выделение города в модальном окне
$(function () {
    const $warehouses = $('input[name="warehouse"]');

    // пересчитываем все <dl>
    function updateState() {
        $('dl.warehouse-city').each(function () {
            $(this).toggleClass('has-checked',
                $(this).find('input[name="warehouse"]:checked').length > 0
            );
        });
    }

    // первый запуск – отмечаем то, что уже выбрано при загрузке
    updateState();
    // при каждом переключении
    $warehouses.on('change', updateState);
});
