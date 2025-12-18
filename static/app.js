async function calculateAI() {
    const year = document.getElementById('movieYear').value;
    const genre = document.getElementById('movieGenre').value;
    const popularity = document.getElementById('moviePop').value;
    const resDiv = document.getElementById('results');
    
    document.getElementById('score').innerText = "...";
    resDiv.style.display = "block";

    const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year, genre, popularity })
    });
    const data = await response.json();
    document.getElementById('score').innerText = data.predicted_rating;
    document.getElementById('impact').innerText = data.impact;
}

async function fetchPersonalized() {
    const uid = document.getElementById('userId').value;
    const grid = document.getElementById('userResults');
    
    if (!uid) { alert("Please enter a User ID"); return; }
    
    grid.innerHTML = "<p style='color: #38bdf8;'>Querying SVD Model for unique taste profile...</p>";

    try {
        const response = await fetch(`/api/user-recommend/${uid}`);
        const movies = await response.json();
        
        grid.innerHTML = "";
        movies.forEach(m => {
            grid.innerHTML += `
                <div class="data-card" style="margin-bottom: 15px; padding: 20px; background: #1e293b; border-radius: 8px; border-left: 4px solid #38bdf8;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.2rem; font-weight: bold; color: white;">${m.title}</span>
                        <span style="color: #38bdf8; font-weight: bold;">${m.score} ★</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 5px;">Genres: ${m.genres}</div>
                </div>
            `;
        });
    } catch (e) {
        grid.innerHTML = "<p style='color: #ef4444;'>Failed to load personalized recommendations.</p>";
    }
}