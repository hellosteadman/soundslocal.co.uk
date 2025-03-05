(() => {
    const ws = new WebSocket('ws://localhost:5678')

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.action === 'reload') {
            console.log('Hot-reloading CSS:', data.file)
            // document.querySelectorAll('link[rel="stylesheet"]').forEach((link) => {
            //     const newLink = link.cloneNode()
            //     newLink.href = link.href.split("?")[0] + "?v=" + new Date().getTime()
            //     link.parentNode.replaceChild(newLink, link)
            // })
        }
    }

    ws.onerror = (err) => console.error('WebSocket error', err)
})()
