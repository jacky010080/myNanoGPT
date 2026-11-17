const generateButton = document.getElementById('generateButton');
const buttonLabel = document.getElementById('buttonLabel');
const modelSelect = document.getElementById('modelSelect');
const output = document.getElementById('output');
const result = document.getElementById('result');
const status = document.getElementById('status');
const emptyState = document.getElementById('emptyState');
const emptyTitle = document.getElementById('emptyTitle');

const modelPicker = document.getElementById('modelPicker');
const modelOptions = document.getElementById('modelOptions');
const modelValue = document.getElementById('modelValue');
const modelSize = document.getElementById('modelSize');
const options = Array.from(modelOptions.querySelectorAll('[role="option"]'));

function closeModelMenu() {
  modelOptions.hidden = true;
  modelSelect.setAttribute('aria-expanded', 'false');
}

function openModelMenu() {
  if (modelSelect.disabled) return;
  modelOptions.hidden = false;
  modelSelect.setAttribute('aria-expanded', 'true');
  options.find(option => option.dataset.value === modelSelect.value).focus();
}

modelSelect.onclick = function () {
  if (modelOptions.hidden) openModelMenu();
  else closeModelMenu();
};

for (const option of options) {
  option.onclick = function () {
    modelSelect.value = option.dataset.value;
    modelValue.textContent = option.querySelector('.option-name').textContent;
    modelSize.textContent = option.dataset.size;
    for (const item of options) {
      item.setAttribute('aria-selected', String(item === option));
    }
    closeModelMenu();
    modelSelect.focus();
  };
}

modelPicker.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    closeModelMenu();
    modelSelect.focus();
    event.preventDefault();
  } else if (event.key === 'Tab') {
    closeModelMenu();
    modelSelect.focus();
  } else if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
    event.preventDefault();
    if (modelOptions.hidden) {
      openModelMenu();
      return;
    }
    const current = options.indexOf(document.activeElement);
    let next = current;
    if (event.key === 'ArrowDown') next = (current + 1) % options.length;
    if (event.key === 'ArrowUp') next = (current - 1 + options.length) % options.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = options.length - 1;
    options[next].focus();
  }
});

document.addEventListener('click', function (event) {
  if (!modelPicker.contains(event.target)) closeModelMenu();
});

modelPicker.addEventListener('focusout', function (event) {
  if (!modelPicker.contains(event.relatedTarget)) closeModelMenu();
});

generateButton.onclick = async function () {
  const modelDisplayName = `${modelValue.textContent} (${modelSize.textContent})`;
  closeModelMenu();
  generateButton.disabled = true;
  modelSelect.disabled = true;
  buttonLabel.textContent = 'Generating…';
  result.dataset.state = 'loading';
  result.setAttribute('aria-busy', 'true');
  status.textContent = 'Writing with ' + modelDisplayName;
  emptyTitle.textContent = 'A new story is taking shape…';
  emptyState.hidden = false;
  output.hidden = true;

  try {
    const response = await fetch(`/generate?model=${encodeURIComponent(modelSelect.value)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Generation failed.');
    output.textContent = data.output;
    result.dataset.state = 'complete';
    status.textContent = 'Written by ' + modelDisplayName;
  } catch (error) {
    output.textContent = error.message;
    result.dataset.state = 'error';
    status.textContent = 'Please try again';
  } finally {
    emptyState.hidden = true;
    output.hidden = false;
    result.setAttribute('aria-busy', 'false');
    buttonLabel.textContent = 'Generate Text';
    generateButton.disabled = false;
    modelSelect.disabled = false;
  }
};
