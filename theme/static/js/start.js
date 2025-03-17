import {} from 'bootstrap'
import AOS from 'aos'
import imagesLoaded from 'imagesloaded'

window.addEventListener('click',
    (e) => {
        const el = e.target.matches('.navbar-toggler') ? e.target : e.target.closest('.navbar-toggler')

        if (!el) {
            return
        }

        if (el) {
            document.body.classList.toggle('main-menu-open')
        }
    },
    false
)

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

document.querySelectorAll('.accordion').forEach(
    (accordion) => {
        accordion.querySelectorAll('a.accordion-header').forEach(
            (a) => {
                const li = a.closest('li.accordion-item')

                a.addEventListener('click',
                    (e) => {
                        const active = li.classList.contains('active')

                        e.preventDefault()
                        accordion.querySelectorAll('li.accordion-item.active').forEach(
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

                            li.querySelectorAll('.accordion-content').forEach(
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

imagesLoaded(
    document.body,
    () => {
        AOS.init(
            {
                offset: 80,
                duration: 1000,
                once: true,
                easing: 'ease'
            }
        )
    }
)
