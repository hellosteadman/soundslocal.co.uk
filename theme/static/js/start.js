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

AOS.init(
    {
        offset: 80,
        duration: 1000,
        once: true,
        easing: 'ease'
    }
)