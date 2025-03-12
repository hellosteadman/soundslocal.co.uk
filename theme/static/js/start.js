import {} from 'bootstrap'
import AOS from 'aos'

document.querySelectorAll('.section.timeline-section ol').forEach(
    (ol) => {
        ol.querySelectorAll('li').forEach(
            (li, i) => {
                if (i % 2 == 0) {
                    li.setAttribute('data-aos', 'fade-right')
                } else {
                    li.setAttribute('data-aos', 'fade-left')
                }

                li.setAttribute('data-aos-delay', 300)
            }
        )
    }
)

document.querySelectorAll('.carousel').forEach(
    (carousel) => {
        carousel.querySelectorAll('a.carousel-header').forEach(
            (a) => {
                const li = a.closest('li.carousel-item')

                a.addEventListener('click',
                    (e) => {
                        const active = li.classList.contains('active')

                        e.preventDefault()
                        carousel.querySelectorAll('li.carousel-item.active').forEach(
                            (other) => {
                                if (other !== li) {
                                    other.classList.remove('active')
                                }
                            }
                        )

                        if (active) {
                            li.classList.remove('active')
                        } else {
                            li.classList.add('active')

                            li.querySelectorAll('.carousel-content').forEach(
                                (content) => {
                                    if (typeof (content.scrollIntoView) === 'function') {
                                        setTimeout(
                                            () => {
                                                content.scrollIntoView(
                                                    {
                                                        behavior: 'smooth',
                                                        block: 'center',
                                                        inline: 'center'
                                                    }
                                                )
                                            },
                                            333
                                        )
                                    }
                                }
                            )
                        }
                    }
                )
            }
        )
    }
)

AOS.init(
    {
        offset: 80,
        duration: 1000,
        once: true,
        easing: 'ease'
    }
)
