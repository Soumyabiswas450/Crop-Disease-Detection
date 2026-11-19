const input = document.getElementById('fileInput');
const dropzone = document.getElementById('dropzone');
const preview = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const selectedFile = document.getElementById('selectedFile');
const dropTitle = document.getElementById('dropTitle');
const dropSubtitle = document.getElementById('dropSubtitle');
const removeButton = document.getElementById('removeFile');
const form = document.getElementById('uploadForm');
const submitButton = document.getElementById('submitButton');
let previewUrl = null;

function showFile(file) {
  if (!file) return;
  const allowed = ['image/png', 'image/jpeg'];
  if (!allowed.includes(file.type)) {
    alert('Please choose a PNG, JPG or JPEG image.');
    input.value = '';
    return;
  }
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(file);
  preview.src = previewUrl;
  preview.hidden = false;
  dropzone.classList.add('has-preview');
  dropTitle.textContent = file.name;
  dropSubtitle.textContent = 'Image selected · ready to analyse';
  fileName.textContent = `${file.name} · ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
  selectedFile.hidden = false;
}

input.addEventListener('change', () => showFile(input.files[0]));
['dragenter', 'dragover'].forEach(eventName => dropzone.addEventListener(eventName, event => {
  event.preventDefault(); dropzone.classList.add('dragover');
}));
['dragleave', 'drop'].forEach(eventName => dropzone.addEventListener(eventName, event => {
  event.preventDefault(); dropzone.classList.remove('dragover');
}));
dropzone.addEventListener('drop', event => {
  const file = event.dataTransfer.files[0];
  if (!file) return;
  const transfer = new DataTransfer();
  transfer.items.add(file);
  input.files = transfer.files;
  showFile(file);
});
removeButton.addEventListener('click', () => {
  input.value = '';
  preview.hidden = true;
  preview.removeAttribute('src');
  dropzone.classList.remove('has-preview');
  dropTitle.textContent = 'Drop your image here';
  dropSubtitle.innerHTML = 'or <u>browse files</u> from your device';
  selectedFile.hidden = true;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
});
form.addEventListener('submit', event => {
  if (!input.files.length) {
    event.preventDefault();
    alert('Please select a rice leaf image first.');
    return;
  }
  submitButton.disabled = true;
  submitButton.querySelector('span:first-child').textContent = 'Analysing image…';
  submitButton.querySelector('.button-arrow').textContent = '◌';
});

// After a Flask POST, bring the result panel into view.
if (window.location.hash === '#results') {
  document.getElementById('results')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
