function checkCongestion() {
    fetch('/api/cars').then(resp=>{
        resp.json().then(data => {
            console.log(data)
            updateOnScreen(data)
        })
    }).catch(err => {
        console.error(err)
    })
}

function updateOnScreen(data) {
    const congestion = data.congestion.toLowerCase();
    document.getElementById('congestion-counter').innerHTML = data.count; 
    document.getElementById('congestion-counter').setAttribute("class", `congestion-counter congestion-${congestion}`)
    document.getElementById('congestion-label').innerHTML = data.congestion;
    document.getElementById('congestion-label').setAttribute("class", `congestion-label congestion-${congestion}`)
}

setInterval(checkCongestion, 500)