const API_URL = "http://127.0.0.1:5000"; // 
let userId = null; // будет получен из Telegram WebApp
let cases = [];
let balance = 0;

const roulette = document.getElementById("roulette");
const resultDiv = document.getElementById("result");
const balanceSpan = document.getElementById("balance");

// === Получаем данные пользователя из Telegram ===
Telegram.WebApp.ready();
Telegram.WebApp.expand();
userId = Telegram.WebApp.initDataUnsafe.user.id;

// === Загружаем баланс ===
async function loadBalance() {
    const res = await fetch(`${API_URL}/get_balance/${userId}`);
    const data = await res.json();
    balance = data.balance;
    balanceSpan.textContent = balance;
}

// === Загружаем кейсы ===
async function loadCases() {
    const res = await fetch(`${API_URL}/get_cases`);
    cases = await res.json();

    const container = document.querySelector(".cases");
    container.innerHTML = "";

    cases.forEach(c => {
        const div = document.createElement("div");
        div.classList.add("case");
        div.innerHTML = `
            <img src="https://api.telegram.org/file/bot<7702115093:AAG33V5LgsgOXnwGAhP5MRmJa1jSj78PUwk>/${c.image}" alt="${c.name}">
            <p>${c.name} – ${c.price} ⭐</p>
        `;
        div.onclick = () => openCase(c.id);
        container.appendChild(div);
    });
}

// === Открытие кейса ===
async function openCase(caseId) {
    const res = await fetch(`${API_URL}/open_case`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, case_id: caseId })
    });
    const data = await res.json();

    if (data.status === "error") {
        return Telegram.WebApp.showAlert(data.message);
    }

    animateRoulette(data.gift);
    await loadBalance();
}

// === Анимация рулетки ===
function animateRoulette(gift) {
    roulette.innerHTML = "";
    resultDiv.textContent = "";

    const emojis = ["🎁", "🎉", "💎", "🧸", "📦", "⭐"];
    const animationLength = 20;
    let index = 0;

    const interval = setInterval(() => {
        roulette.textContent = emojis[index % emojis.length];
        index++;
        if (index > animationLength) {
            clearInterval(interval);
            roulette.textContent = gift.emoji;
            resultDiv.innerHTML = `🎉 Вы выиграли: <b>${gift.name}</b> (${gift.rarity})`;
        }
    }, 100);
}

// === Инициализация ===
loadBalance();
loadCases();
