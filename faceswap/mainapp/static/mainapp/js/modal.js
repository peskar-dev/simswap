// (() => {

//   // ==================================Модалка с загрузкой============================

//   const uploadBtn = document.querySelector('.upload-btn');
//   const fileInput = document.getElementById('file-input');
//   const progressModal = document.querySelector('.progress-modal');
//   const progressText = document.querySelector('.progress-text');
//   const modal = document.querySelector('.modal');
//   const progressBar = document.querySelector('.progress');

//   uploadBtn.addEventListener('click', () => {
//     fileInput.click();
//   });

//   fileInput.addEventListener('change', () => {
//     const file = fileInput.files[0];
//     modal.classList.add('hidden');

//     if (file) {
//       showProgressModal();
//       let progress = 0;
//       const interval = setInterval(() => {

//         progress += 1;
//         progressText.textContent = `${progress}%`;

//         progressModal.classList.remove('hidden');
//         progress += 1;
//         progressBar.style.width = `${progress}%`;

//         if (progress === 100) {
//           clearInterval(interval);
//           progressModal.classList.add('hidden');

//           setTimeout(() => {
//             window.location.href = "/result";
//           }, 0);
//         }
//       }, 70);
//     }
//   });

//   function showProgressModal() {
//     progressModal.classList.remove('hidden');
//   }

// })()

// (() => {
//   const uploadBtn = document.querySelector('.upload-btn');
//   const fileInput = document.getElementById('file-input');
//   const form = document.getElementById('upload-form');
//   const progressModal = document.querySelector('.progress-modal');
//   const progressText = document.querySelector('.progress-text');
//   const progressBar = document.querySelector('.progress');

//   uploadBtn.addEventListener('click', () => {
//     fileInput.click(); // Эмулируем клик на файловый инпут
//   });

//   fileInput.addEventListener('change', () => {
//     if (fileInput.files.length > 0) {
//       form.submit(); // Отправляем форму, когда файл выбран
//     }
//   });

//   form.addEventListener('submit', (e) => {
//     e.preventDefault(); // Предотвращаем обычную отправку формы
//     const formData = new FormData(form);
//     const xhr = new XMLHttpRequest();
//     xhr.open('POST', form.action); // Используем URL из атрибута action формы

//     // Отслеживаем прогресс загрузки
//     xhr.upload.onprogress = function(event) {
//       if (event.lengthComputable) {
//         const percentComplete = (event.loaded / event.total) * 100;
//         progressBar.style.width = percentComplete + '%';
//         progressText.textContent = Math.round(percentComplete) + '%';
//       }
//     };

//     // Обработка завершения запроса
//     xhr.onload = function() {
//       if (xhr.status === 200) {
//         window.location.href = "/result"; // Переход, если загрузка успешна
//       } else {
//         alert('Произошла ошибка при загрузке файла: ' + xhr.statusText);
//       }
//       progressModal.classList.add('hidden');
//     };

//     // Обработка ошибок запроса
//     xhr.onerror = function() {
//       alert('Произошла ошибка при отправке запроса');
//       progressModal.classList.add('hidden');
//     };

//     progressModal.classList.remove('hidden');
//     xhr.send(formData); // Отправляем форму при помощи AJAX
//   });
// })();

;(() => {
  const uploadBtn = document.querySelector('.upload-btn')
  const fileInput = document.getElementById('file-input')
  const form = document.getElementById('upload-form')
  const progressModal = document.querySelector('.progress-modal') // Получаем модальное окно
  const progressBar = document.querySelector('.progress') // Получаем элемент прогресс-бара
  const progressText = document.querySelector('.progress-text') // Получаем элемент текста прогресса

  uploadBtn.addEventListener('click', () => {
    fileInput.click()
  })

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      // Показываем модалку с прогрессом перед началом загрузки
      progressModal.classList.remove('hidden')
      form.submit()
    }
  })

  form.addEventListener('submit', (e) => {
    e.preventDefault() // Предотвращаем стандартное поведение формы

    progressModal.classList.remove('hidden')
  })
})()
