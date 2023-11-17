document.getElementById('upload-button').addEventListener('click', function() {
    const fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    // Handle the response from the server
    xhr.onload = function () {
        if (xhr.status === 200) {
            document.getElementById('upload-status').textContent = 'File uploaded successfully';
        } else {
            document.getElementById('upload-status').textContent = 'Upload failed';
        }
    };

    xhr.send(formData);
});