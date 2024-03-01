(() => {

  // ==================================Модалка с загрузкой============================

  const uploadBtn = document.querySelector('.upload-btn');
  const fileInput = document.getElementById('file-input');
  const progressModal = document.querySelector('.progress-modal');
  const progressText = document.querySelector('.progress-text');
  const modal = document.querySelector('.modal');
  const progressBar = document.querySelector('.progress');

  uploadBtn.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    modal.classList.add('hidden');

    if (file) {
      showProgressModal();
      let progress = 0;
      const interval = setInterval(() => {

        progress += 1;
        progressText.textContent = `${progress}%`;

        progressModal.classList.remove('hidden');
        progress += 1;
        progressBar.style.width = `${progress}%`;



        if (progress === 100) {
          clearInterval(interval);
          progressModal.classList.add('hidden');



          setTimeout(() => {
            window.location.href = "/result";
          }, 0);
        }
      }, 70);
    }
  });


  function showProgressModal() {
    progressModal.classList.remove('hidden');
  }

})()