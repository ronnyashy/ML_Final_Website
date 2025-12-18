async function calculateAI() {
    const year = document.getElementById('movieYear').value;
    const genre = document.getElementById('movieGenre').value;
    const popularity = document.getElementById('moviePop').value;
    const resDiv = document.getElementById('results');
    
    document.getElementById('score').innerText = "Calculating...";
    resDiv.style.display = "block";

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ year, genre, popularity })
        });

        const data = await response.json();
        if(data.status === "success") {
            document.getElementById('score').innerText = data.predicted_rating;
            document.getElementById('impact').innerText = data.business_impact;
        } else {
            alert("Model Error: " + data.error);
        }
    } catch (e) {
        console.error("Link to AI server failed.");
    }
}