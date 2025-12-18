async function calculateAI() {
    const year = document.getElementById('movieYear').value;
    const genre = document.getElementById('movieGenre').value;
    const resDiv = document.getElementById('results');
    document.getElementById('score').innerText = "...";
    resDiv.style.display = "block";

    const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year, genre, popularity: 5000 })
    });
    const data = await response.json();
    document.getElementById('score').innerText = data.predicted_rating;
    document.getElementById('impact').innerText = data.impact;
}

async function fetchPersonalized() {
    const uid = document.getElementById('userId').value;
    const grid = document.getElementById('userResults');
    grid.innerHTML = "<p>Analyzing your taste profile...</p>";

    try {
        const response = await fetch(`/api/user-recommend/${uid}`);
        const movies = await response.json();
        
        grid.innerHTML = "";
        movies.forEach(m => {
            grid.innerHTML += `
                <div class="data-card" style="margin-bottom: 10px; padding: 15px; background: #1e293b; border-radius: 8px;">
                    <div style="color: #38bdf8; font-weight: bold;">Match: ${m.score} ★</div>
                    <div style="font-size: 1.1rem; margin: 5px 0;">${m.title}</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">${m.genres}</div>
                </div>
            `;
        });
    } catch (e) {
        grid.innerHTML = "Error loading recommendations.";
    }
}