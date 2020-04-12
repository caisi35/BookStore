var swiper = new Swiper('.swiper-container', {
    pagination: '.swiper-pagination',
    paginationClickable: true,
    loop: true,
    autoplay: 3000,


    speed: 1000,
    prevButton: '.swiper-button-prev',
    nextButton: '.swiper-button-next',
    effect: 'slide',//  effect: 'flip',effect: 'coverflow',slide', 'fade',cube,
    grabCursor: true,
    cube: {
        shadow: false,
        slideShadows: false,
        shadowOffset: 20,
        shadowScale: 0.94
    }
});

