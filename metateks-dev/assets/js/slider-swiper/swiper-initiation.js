
// Слайдер рекламного баннера

var swiper = new Swiper(".slider-advertising", {

	// Количество слайдов для показа
	slidesPerView: 1,

	// Отступ между слайдами
	spaceBetween: 30,



	// Количество пролистываемых слайдов
	slidesPerGroup: 1,

	// Отключение функционала
	// если слайдов меньше чем нужно
	watchOverflow: true,

	// ==== Автопрокрутка
	autoplay: {
		delay: 4000,

		// Закончить на последнем слайде
		stopOnLastSlide: false,

		// Отключить после ручного переключения
		disableOnInteraction: true,
	},

	/*
	modifier: 1,
	shortSwipes: true,
	*/

	// Бесконечный слайдер
	loop: true,
	loopFillGroupWithBlank: true,

	//  === Эффекты переключения слайдов.
	// Cмена прозрачности*/
	effect: 'fade',

	// Дополнение к fade
	fadeEffect: {
		// Параллельная
		// смена прозрачности
		crossFade: true
	},


	// Отключить предзагрузка картинок
	preloadImages: false,
	// Lazy Loading
	// (подгрузка картинок)
	lazy: {
		// Подгружать на старте
		// переключения слайда
		loadOnTransitionStart: false,
		// Подгрузить предыдущую
		// и следующую картинки
		loadPrevNext: false,
	},


	// Обновить свайпер
	// при изменении элементов слайдера
	observer: true,

	// Обновить свайпер
	// при изменении родительских
	// элементов слайдера
	observeParents: true,

	// Обновить свайпер
	// при изменении дочерних
	// элементов слайда
	observeSlideChildren: true,


	

	// Управление клавиатурой
	keyboard: {
		// Включить\выключить
		enabled: true,
		// Включить\выключить
		// только когда слайдер
		// в пределах вьюпорта
		onlyInViewport: true,
		// Включить\выключить
		// управление клавишами
		// pageUp, pageDown
		pageUpDown: true,
	},



	// Автовысота
	autoHeight: false,



	//  === Навигация 
	// Буллеты, текущее положение, прогрессбар
	pagination: {
		el: '.swiper-pagination',
		clickable: true,
	},

	// Стрелки
	navigation: {
		nextEl: '.swiper-button-next',
		prevEl: '.swiper-button-prev',
	},
});


// Слайдер карточек товара

var swiper = new Swiper(".slider-products", {

	// Количество слайдов для показа
	slidesPerView: 4,

	breakpoints: {
		120: {
			slidesPerView: 1,
		},
		576: {
			slidesPerView: 2,
		},
		768: {
			slidesPerView: 3,
		},
		1200: {
			slidesPerView: 4,
		},
	},



	// Отступ между слайдами
	spaceBetween: 20,


	// Количество пролистываемых слайдов
	slidesPerGroup: 1,

	// Отключение функционала
	// если слайдов меньше чем нужно
	watchOverflow: true,


	// Отключить предзагрузка картинок
	preloadImages: false,
	// Lazy Loading
	// (подгрузка картинок)
	lazy: {
		// Подгружать на старте
		// переключения слайда
		loadOnTransitionStart: false,
		// Подгрузить предыдущую
		// и следующую картинки
		loadPrevNext: false,
	},


	// Обновить свайпер
	// при изменении элементов слайдера
	observer: true,

	// Обновить свайпер
	// при изменении родительских
	// элементов слайдера
	observeParents: true,

	// Обновить свайпер
	// при изменении дочерних
	// элементов слайда
	observeSlideChildren: true,


	// Бесконечный слайдер
	loop: true,
	loopFillGroupWithBlank: true,


	// Управление клавиатурой
	keyboard: {
		// Включить\выключить
		enabled: true,
		// Включить\выключить
		// только когда слайдер
		// в пределах вьюпорта
		onlyInViewport: true,
		// Включить\выключить
		// управление клавишами
		// pageUp, pageDown
		pageUpDown: true,
	},



	// Автовысота
	autoHeight: false,



	//  === Навигация 
	// Буллеты, текущее положение, прогрессбар
	pagination: {
		el: '.swiper-pagination',
		clickable: true,
	},

	// Стрелки
	navigation: {
		nextEl: '.swiper-button-next',
		prevEl: '.swiper-button-prev',
	},
});





// Слайдер брендов 

var swiper = new Swiper(".slider-brands", {

	// Количество слайдов для показа
	slidesPerView: 4,

	breakpoints: {
		120: {
			slidesPerView: 1,
			grid: {       //сетка
				rows: 2,
			},    
		},
		576: {
			slidesPerView: 2,
			grid: {       //сетка
				rows: 2,
			},    
		},
		768: {
			slidesPerView: 3,
			grid: {       //сетка
				rows: 2,
			},    
		},
		1200: {
			slidesPerView: 5,
			grid: {       //сетка
				rows: 2,
			},    
		},
	},





	// Отступ между слайдами
	spaceBetween: 3,


	// Количество пролистываемых слайдов
	slidesPerGroup: 1,

	// Отключение функционала
	// если слайдов меньше чем нужно
	watchOverflow: true,


	// Отключить предзагрузка картинок
	preloadImages: false,
	// Lazy Loading
	// (подгрузка картинок)
	lazy: {
		// Подгружать на старте
		// переключения слайда
		loadOnTransitionStart: false,
		// Подгрузить предыдущую
		// и следующую картинки
		loadPrevNext: false,
	},


	// Обновить свайпер
	// при изменении элементов слайдера
	observer: true,

	// Обновить свайпер
	// при изменении родительских
	// элементов слайдера
	observeParents: true,

	// Обновить свайпер
	// при изменении дочерних
	// элементов слайда
	observeSlideChildren: true,


	// Бесконечный слайдер
	loop: true,
	loopFillGroupWithBlank: true,


	// Управление клавиатурой
	keyboard: {
		// Включить\выключить
		enabled: true,
		// Включить\выключить
		// только когда слайдер
		// в пределах вьюпорта
		onlyInViewport: true,
		// Включить\выключить
		// управление клавишами
		// pageUp, pageDown
		pageUpDown: true,
	},



	// Автовысота
	autoHeight: false,



	//  === Навигация 
	// Буллеты, текущее положение, прогрессбар
	pagination: {
		el: '.swiper-pagination',
		clickable: true,
	},

	// Стрелки
	navigation: {
		nextEl: '.swiper-button-next',
		prevEl: '.swiper-button-prev',
	},
});







// === 4 слайдeр с превью

var swiper = new Swiper(".slider-product__preview", {
	spaceBetween: 0,
	//slidesPerView: 3,
	freeMode: true,
	watchSlidesProgress: true,

	breakpoints: {
		120: {
			slidesPerView: 5,

		},
		576: {
			slidesPerView: 5,

		},
		768: {
			slidesPerView: 1,

		},

	},



});
var swiper2 = new Swiper(".largeimage", {
	spaceBetween: 0,
	navigation: {
		nextEl: ".swiper-button-next",
		prevEl: ".swiper-button-prev",
	},
	thumbs: {
		swiper: swiper,
	},
});







