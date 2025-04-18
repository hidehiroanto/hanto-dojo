const input = document.querySelector('input');
const span = document.querySelector('span');

input.addEventListener('input', function (event) {
    span.innerHTML = '&nbsp;&nbsp;' + this.value.replace(/\s/g, '&nbsp;') + '&nbsp;&nbsp;';
    this.style.width = span.offsetWidth + 'px';
});