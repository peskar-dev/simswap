(() => {
  // ==================================Бургер============================
  document.addEventListener('click', burgerInit)
  function burgerInit(e) {
      const burgerIcon = e.target.closest('.burger-icon')
      const burgerNavLink = e.target.closest('.header__nav-link')
      if (!burgerIcon && !burgerNavLink) return
      if (document.documentElement.clientWidth > 1000) return
      if (!document.body.classList.contains('body--opened-menu')) {
          document.body.classList.add('body--opened-menu')
      } else {
          document.body.classList.remove('body--opened-menu')
      }
  }

  // ==================================Модалка 1============================

  document.addEventListener('click', modalInit)
  function modalInit(e) {
      const modalOpen = e.target.closest('.button-upload-photo')
      const modal = e.target.classList.contains('modal')
      if (!modalOpen && !modal) return
      if (!document.body.classList.contains('body--modal-opened') && e.target.closest('.button-upload-photo')) {
          document.body.classList.add('body--modal-opened')
      } else if (e.target && e.target.classList.contains('modal') && document.body.classList.contains('body--modal-opened')) {
          document.body.classList.remove('body--modal-opened')
      }
  }
  document.addEventListener('keydown', modalClose)
  function modalClose(e) {
      if (e.code === 'Escape' && document.body.classList.contains('body--modal-opened')) {
          document.body.classList.remove('body--modal-opened')
      }
  }


  // ==================================Модалка просмотр фотографии============================

  document.addEventListener('click', modalViewing)
  function modalViewing(e) {
      const modalOpen = e.target.closest('.button-viewing')
      const modalCloseButton = e.target.closest('.modal__cancel')
      const modalClose = e.target.closest('.button-download')
      const modal = e.target.classList.contains('modal')
      const modalWindowClose = e.target.classList.contains('modal__window-viewing')
      if (!modalOpen && !modal && !modalClose && !modalCloseButton && !modalWindowClose) return
      if (!document.body.classList.contains('body--modal-opened') && e.target.closest('.button-viewing')) {
          document.body.classList.add('body--modal-opened')
          document.querySelector('.modal__video').setAttribute('autoplay', '')
      } else if (e.target && e.target.classList.contains('modal__window-viewing') || e.target.closest('.button-download') || e.target.closest('.modal__cancel') || e.target && e.target.classList.contains('modal') && document.body.classList.contains('body--modal-opened')) {
          document.body.classList.remove('body--modal-opened')
          document.querySelector('.modal__video').removeAttribute('autoplay')
      }
  }
  document.addEventListener('keydown', modalClose)
  function modalClose(e) {
      if (e.code === 'Escape' && document.body.classList.contains('body--modal-opened')) {
          document.body.classList.remove('body--modal-opened')
      }
  }



})()