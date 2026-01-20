// ---------- AI Prediction ----------
function predict(){
    fetch("/ai-predict")
    .then(r => r.json())
    .then(d => {
        document.getElementById("ai").innerText =
        d.trend + " (" + d.confidence + "%)";
    });
}

// ---------- Market Trend Chart (IMPROVED) ----------
fetch("/chart-data")
.then(r => r.json())
.then(d => {

    let prices = d.prices;
    let trend = d.trend;

    let canvas = document.getElementById("chart");
    let ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // ----- Background -----
    ctx.fillStyle = "#020617";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // ----- Grid Lines -----
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 6; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * 50);
        ctx.lineTo(canvas.width, i * 50);
        ctx.stroke();
    }

    // ----- Trend Line -----
    ctx.beginPath();
    ctx.lineWidth = 3;
    ctx.strokeStyle = trend === "UP" ? "#22c55e" : "#ef4444";

    prices.forEach((price, i) => {
        let x = i * 22;
        let y = canvas.height - (price - 82) * 50;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.stroke();

    // ----- Data Points -----
    prices.forEach((price, i) => {
        let x = i * 22;
        let y = canvas.height - (price - 82) * 50;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#38bdf8";
        ctx.fill();
    });

    // ----- Last Price Label -----
    let lastPrice = prices[prices.length - 1];
    ctx.fillStyle = "#facc15";
    ctx.font = "14px Segoe UI";
    ctx.fillText("Last Price: " + lastPrice, 520, 30);

    // ----- Trend Indicator -----
    ctx.font = "16px Segoe UI";
    ctx.fillStyle = trend === "UP" ? "#22c55e" : "#ef4444";
    ctx.fillText("Market Trend: " + trend, 20, 30);
});

// ---------- Currency Converter ----------
function convert(){
    let from = document.getElementById("from").value;
    let to = document.getElementById("to").value;
    let amount = document.getElementById("amount").value;

    fetch(`/convert-currency?from=${from}&to=${to}&amount=${amount}`)
    .then(r => r.json())
    .then(d => {
        document.getElementById("result").innerText =
        `${d.amount} ${d.from} = ${d.converted} ${d.to}`;
    });
}
