const form = document.querySelector('form');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        let isUploading = false;

        form.addEventListener('submit', (event) => {
            event.preventDefault();

            progressBar.value = 0;
            progressText.textContent = 'Загрузка...';
            isUploading = true;

            const formData = new FormData(form);

            fetch('/downloader/', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
              .then(data => {
                if (data.success) {
                    progressText.textContent = 'Загрузка завершена';
                    isUploading = false;
                } else {
                    progressText.textContent = 'Ошибка загрузки';
                    isUploading = false;
                }
              })
              .catch(error => {
                progressText.textContent = 'Ошибка загрузки';
                isUploading = false;
              });

            const updateProgress = () => {
                if (isUploading) {
                    fetch('/progress/')
                      .then(response => response.json())
                      .then(data => {
                          if (data.percent) {
                              progressBar.value = data.percent;
                              progressText.textContent = `Загрузка... ${data.percent}%`;
                          }
                          if (data.finished) {
                              progressText.textContent = 'Загрузка завершена';
                          }
                      });
                }
            };

            const interval = setInterval(updateProgress, 1000);

            updateProgress();
        });

    document.addEventListener("DOMContentLoaded", function () {
        const downloadPathInput = document.querySelector("#id_download_path");
        const filePickerBtn = document.createElement("button");
        filePickerBtn.innerHTML = "Выбрать папку";
        filePickerBtn.className = "btn btn-secondary";

        filePickerBtn.addEventListener("click", function () {
            const {remote} = require("electron"); // Import remote module
            const dialog = remote.dialog;
            const selectedPaths = dialog.showOpenDialogSync({properties: ["openDirectory"]});
            if (selectedPaths && selectedPaths.length > 0) {
                downloadPathInput.value = selectedPaths[0];
            }
        });

        downloadPathInput.insertAdjacentElement("afterend", filePickerBtn);
    });


