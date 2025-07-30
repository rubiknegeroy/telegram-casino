
document.addEventListener("DOMContentLoaded", () => {
    const casesContainer = document.getElementById("cases-container");
    const roulette = document.getElementById("roulette");
    const result = document.getElementById("result");
    const balanceEl = document.getElementById("balance");

    let balance = 100; 
    balanceEl.textContent = balance;

    const gifts = [
        { name: "Медвежонок", rarity: "common", icon: "🐻" },
        { name: "Кольцо", rarity: "rare", icon: "💍" },
        { name: "Машина", rarity: "legendary", icon: "🚗" },
        { name: "Телефон", rarity: "common", icon: "📱" },
        { name: "Дом", rarity: "legendary", icon: "🏠" }
    ];

    const cases = [
        { id: 1, name: "Bronze", price: 1 },
        { id: 2, name: "Silver", price: 5 },
        { id: 3, name: "Gold", price: 10 }
    ];

    casesContainer.innerHTML = cases.map(c =>
        `<div class="case" data-id="${c.id}" data-price="${c.price}">
            <p>${c.name} – ${c.price} ⭐</p>
        </div>`
    ).join("");

    document.querySelectorAll(".case").forEach(caseEl => {
        caseEl.addEventListener("click", () => {
            const price = parseInt(caseEl.dataset.price);
            if (balance < price) {
                alert("Недостаточно звёзд!");
                return;
            }
            balance -= price;
            balanceEl.textContent = balance;
            startRoulette();
        });
    });

    function startRoulette() {
        roulette.innerHTML = "";
        result.textContent = "";

        const spinItems = [];
        for (let i = 0; i < 30; i++) {
            const randomGift = gifts[Math.floor(Math.random() * gifts.length)];
            const item = document.createElement("div");
            item.className = `gift ${randomGift.rarity}`;
            item.textContent = `${randomGift.icon} ${randomGift.name}`;
            roulette.appendChild(item);
            spinItems.push(randomGift);
        }

        let position = 0;
        const spinInterval = setInterval(() => {
            roulette.scrollLeft = position;
            position += 20;
            if (position >= roulette.scrollWidth - roulette.clientWidth) {
                clearInterval(spinInterval);
                const winGift = spinItems[Math.floor(Math.random() * spinItems.length)];
                result.textContent = `Вы выиграли: ${winGift.icon} ${winGift.name}!`;
            }
        }, 100);
    }
});
