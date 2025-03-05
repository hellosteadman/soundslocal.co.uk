(
    () => {
        let timeout = 3000

        const getMessages = () => {
            fetch('/.well-known/reload-messages/').then(
                (response) => {
                    response.json().then(
                        (messages) => {
                            messages.forEach(
                                (message) => {
                                    if (message.action === 'reload') {
                                        if (message.full) {
                                            location.reload()
                                            return
                                        }

                                        if (message.css) {
                                            document.querySelectorAll(
                                                `link[rel="stylesheet"][href="${message.css}"]`
                                            ).forEach(
                                                (link) => {
                                                    link.parentNode.removeChild(link)
                                                }
                                            )

                                            const link = document.createElement('link')

                                            link.rel = 'stylesheet'
                                            link.href = message.css + '?_ts=' + new Date().getTime()
                                            document.head.appendChild(link)
                                        }
                                    }
                                }
                            )

                            setTimeout(getMessages, 300)
                        }
                    ).catch(
                        (err) => {
                            console.warn(err)
                            setTimeout(getMessages, 2000)
                        }
                    )
                }
            ).catch(
                (err) => {
                    console.warn(err)
                    setTimeout(getMessages, timeout)
                    timeout *= 2
                }
            )
        }

        getMessages()
    }
)()
