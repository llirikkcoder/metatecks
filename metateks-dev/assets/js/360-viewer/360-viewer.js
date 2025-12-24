		class Image360Viewer {
			constructor(options) {
				this.container = options.container;
				this.images = Array.from(this.container.querySelectorAll('img'));
				this.numImages = this.images.length;
				this.currentImage = 0;
				this.autoRotate = options.autoRotate || false;
				this.rotateInterval = options.rotateInterval || 100;
				this.scrollbar = options.scrollbar !== undefined ? options.scrollbar : true;
				this.navigationButtons = options.navigationButtons !== undefined ? options.navigationButtons : true;
				this.imagePath = options.imagePath || '';

				this.preloadImages().then(() => {
					this.initViewer();
				});
			}

			async preloadImages() {
				const promises = this.images.map(img => new Promise((resolve, reject) => {
					const image = new Image();
					image.src = img.src;
					image.onload = resolve;
					image.onerror = reject;
				}));
				await Promise.all(promises);
			}

			initViewer() {
				this.container.style.position = 'relative';
				this.container.style.overflow = 'hidden';
				this.container.style.width = '100%';
				//this.container.style.height = '100%';
				this.container.style.backgroundSize = 'cover';
				this.container.style.backgroundPosition = 'center';
				this.container.style.backgroundImage = `url(${this.images[0].src})`;

				this.container.innerHTML = ''; // Удаляем все изображения из контейнера

				if (this.navigationButtons) {
					this.createNavigation();
				}

				if (this.scrollbar) {
					this.createScrollbar();
				}

				this.container.addEventListener('mousedown', (e) => this.onDragStart(e));
				this.container.addEventListener('mousemove', (e) => this.onDragMove(e));
				this.container.addEventListener('mouseup', (e) => this.onDragEnd(e));
				this.container.addEventListener('mouseleave', (e) => this.onDragEnd(e));
				this.container.addEventListener('touchstart', (e) => this.onDragStart(e));
				this.container.addEventListener('touchmove', (e) => this.onDragMove(e));
				this.container.addEventListener('touchend', (e) => this.onDragEnd(e));

				window.addEventListener('keydown', (e) => this.onKeyDown(e));

				this.isDragging = false;
				this.startX = 0;

				if (this.autoRotate) {
					this.startAutoRotate();
				}
			}

			createNavigation() {
				const prevButton = document.createElement('button');
				prevButton.innerHTML = '◀';
				prevButton.className = 'nav-button prev-button';
				prevButton.addEventListener('click', () => this.showPreviousImage());

				const nextButton = document.createElement('button');
				nextButton.innerHTML = '▶';
				nextButton.className = 'nav-button next-button';
				nextButton.addEventListener('click', () => this.showNextImage());

				this.container.appendChild(prevButton);
				this.container.appendChild(nextButton);
			}

			createScrollbar() {
				const scrollbar = document.createElement('input');
				scrollbar.type = 'range';
				scrollbar.min = 0;
				scrollbar.max = this.numImages - 1;
				scrollbar.value = 0;
				scrollbar.className = 'image-scrollbar';

				scrollbar.addEventListener('input', (e) => {
					this.currentImage = parseInt(e.target.value);
					this.updateImage();
				});

				this.container.appendChild(scrollbar);
			}

			showPreviousImage() {
				this.currentImage = (this.currentImage - 1 + this.numImages) % this.numImages;
				this.updateImage();
			}

			showNextImage() {
				this.currentImage = (this.currentImage + 1) % this.numImages;
				this.updateImage();
			}

			updateImage() {
				this.container.style.backgroundImage = `url(${this.images[this.currentImage].src})`;
			}

			onDragStart(e) {
				this.isDragging = true;
				this.startX = e.clientX || e.touches[0].clientX;
			}

			onDragMove(e) {
				if (!this.isDragging) return;

				const clientX = e.clientX || e.touches[0].clientX;
				const dx = clientX - this.startX;
				const imageIndex = Math.floor((dx / this.container.clientWidth) * this.numImages);

				if (imageIndex !== 0) {
					this.currentImage = (this.currentImage + imageIndex) % this.numImages;
					if (this.currentImage < 0) this.currentImage += this.numImages;
					this.updateImage();
					this.startX = clientX;
				}
			}

			onDragEnd(e) {
				this.isDragging = false;
			}

			onKeyDown(e) {
				if (e.key === 'ArrowLeft') {
					this.showPreviousImage();
				} else if (e.key === 'ArrowRight') {
					this.showNextImage();
				}
			}

			startAutoRotate() {
				this.autoRotateInterval = setInterval(() => {
					this.showNextImage();
				}, this.rotateInterval);
			}

			stopAutoRotate() {
				clearInterval(this.autoRotateInterval);
			}
		}
