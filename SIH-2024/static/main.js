const mainhead = document.querySelector('.main-head');
const showcase = document.querySelector('.showcase');
const toggler = document.querySelector('.toggler');

toggler.addEventListener('click',function(){
    mainhead.classList.toggle('active');
    showcase.classList.toggle('width');
});

