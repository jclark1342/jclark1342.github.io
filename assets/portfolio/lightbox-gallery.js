(() => {
  const galleries = [...document.querySelectorAll("[data-lightbox-gallery]")];

  if (!galleries.length) {
    return;
  }

  const lightbox = document.createElement("div");
  lightbox.className = "gallery-lightbox";
  lightbox.setAttribute("aria-hidden", "true");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-label", "Expanded gallery image");
  lightbox.innerHTML = `
    <button class="lightbox-nav lightbox-nav-prev" type="button" aria-label="Previous image">←</button>
    <button class="lightbox-nav lightbox-nav-next" type="button" aria-label="Next image">→</button>
    <button class="gallery-lightbox-close" type="button" aria-label="Close full screen image">Close</button>
    <p class="lightbox-counter" aria-live="polite"></p>
    <img alt="">
  `;
  document.body.append(lightbox);

  const lightboxImage = lightbox.querySelector("img");
  const counter = lightbox.querySelector(".lightbox-counter");
  const closeButton = lightbox.querySelector(".gallery-lightbox-close");
  const prevButton = lightbox.querySelector(".lightbox-nav-prev");
  const nextButton = lightbox.querySelector(".lightbox-nav-next");

  let activeGallery = [];
  let activeIndex = -1;
  let activeTile = null;
  let pointerStartX = null;

  function getGalleryItems(gallery) {
    const selector = gallery.dataset.lightboxItem;
    return selector
      ? [...gallery.querySelectorAll(selector)]
      : [...gallery.children].filter((item) => item.querySelector("img"));
  }

  function showImage(index) {
    if (!activeGallery.length) {
      return;
    }

    activeIndex = (index + activeGallery.length) % activeGallery.length;
    activeTile = activeGallery[activeIndex];
    const image = activeTile.querySelector("img");

    lightboxImage.src = image.currentSrc || image.src;
    lightboxImage.alt = image.alt;
    counter.textContent = `${activeIndex + 1} / ${activeGallery.length}`;
    lightbox.setAttribute("aria-hidden", "false");
    lightbox.classList.add("is-open");
    document.body.classList.add("is-lightbox-open");
  }

  function openLightbox(gallery, tile) {
    activeGallery = getGalleryItems(gallery);
    showImage(activeGallery.indexOf(tile));
    closeButton.focus();
  }

  function closeLightbox() {
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.classList.remove("is-lightbox-open");
    lightboxImage.removeAttribute("src");
    lightboxImage.alt = "";
    counter.textContent = "";

    if (activeTile) {
      activeTile.focus();
    }

    activeGallery = [];
    activeIndex = -1;
    activeTile = null;
  }

  function showPreviousImage() {
    showImage(activeIndex - 1);
  }

  function showNextImage() {
    showImage(activeIndex + 1);
  }

  galleries.forEach((gallery) => {
    getGalleryItems(gallery).forEach((tile) => {
      const image = tile.querySelector("img");

      tile.classList.add("lightbox-gallery-item");
      tile.setAttribute("role", "button");
      tile.setAttribute("tabindex", "0");
      tile.setAttribute("aria-label", `Open ${image.alt} full screen`);

      tile.addEventListener("click", () => openLightbox(gallery, tile));
      tile.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openLightbox(gallery, tile);
        }
      });
    });
  });

  closeButton.addEventListener("click", closeLightbox);
  prevButton.addEventListener("click", showPreviousImage);
  nextButton.addEventListener("click", showNextImage);

  lightbox.addEventListener("pointerdown", (event) => {
    pointerStartX = event.clientX;
  });

  lightbox.addEventListener("pointerup", (event) => {
    if (pointerStartX === null) {
      return;
    }

    const swipeDistance = event.clientX - pointerStartX;
    pointerStartX = null;

    if (Math.abs(swipeDistance) < 54) {
      return;
    }

    if (swipeDistance > 0) {
      showPreviousImage();
    } else {
      showNextImage();
    }
  });

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) {
      closeLightbox();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!lightbox.classList.contains("is-open")) {
      return;
    }

    if (event.key === "Escape") {
      closeLightbox();
    }

    if (event.key === "ArrowLeft") {
      event.preventDefault();
      showPreviousImage();
    }

    if (event.key === "ArrowRight") {
      event.preventDefault();
      showNextImage();
    }
  });
})();
