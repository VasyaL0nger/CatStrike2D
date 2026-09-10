import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы шутера
st.set_page_config(page_title="CatStrike 2D", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("CatStrike 2D")
st.write("Свободное перемещение, стрельба в реальном времени и стикеры на арене.")
st.write("Управление: **WASD / Стрелочки** — движение. **Пробел / Клик мыши** — стрельба. Наберите **500 очков** для победы!")

# Полный HTML5/JavaScript код игры, который встраивается прямо в Streamlit
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background-color: #020617; color: white; font-family: Arial, sans-serif; text-align: center; overflow: hidden; }
        canvas { background-color: #090d16; border: 3px solid #22c55e; border-radius: 8px; display: block; margin: 10px auto; }
        .menu-box { max-width: 500px; margin: 20px auto; background: #0f172a; padding: 20px; border-radius: 12px; border: 2px solid #22c55e; }
        .btn { background: #1e293b; color: white; border: 1px solid #475569; padding: 12px; margin: 6px; border-radius: 6px; cursor: pointer; text-align: left; width: 95%; font-size: 14px; }
        .btn:hover { background: #16a34a; border-color: #4ade80; }
        .win-screen { display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(15, 23, 42, 0.95); padding: 40px; border: 4px solid #eab308; border-radius: 16px; color: #eab308; }
    </style>
</head>
<body>

    <!-- ЭКРАН ВЫБОРА КОТА -->
    <div id="charMenu" class="menu-box">
        <h3>ВЫБЕРИТЕ БОЕВОГО КОТА:</h3>
        <button class="btn" onclick="start('Vasya', '🐱', 3.5, 150)">🐱 <b>Vasya</b> — Ленивый король. Штурмовик. Высокое здоровье.</button>
        <button class="btn" onclick="start('Bulya', '🐱', 4, 100)">🐱✨ <b>Bulya</b> — Белая и нежная кошка. Любит обниматься.</button>
        <button class="btn" onclick="start('Murka', '🥷', 4.5, 110)">🥷 <b>Murka</b> — Черная кошка. Любит царапаться и играться.</button>
        <button class="btn" onclick="start('Rizyk', '🦁', 6, 90)">🦁 <b>Rizyk</b> — Рыжий кот. Очень быстрый и опасный.</button>
        <button class="btn" onclick="start('Tomas', '🐯', 5, 120)">🐯 <b>Tomas</b> — Полосатый друг Рыжика. Штурмовик.</button>
    </div>

    <!-- ПОБЕДНЫЙ ЭКРАН -->
    <div id="winScreen" class="win-screen">
        <h1 style="font-size: 48px; margin: 0;">🏆 ПОБЕДА! 🏆</h1>
        <p style="font-size: 20px; color: white; margin: 15px 0;">Вы успешно набрали 500 очков в CatStrike 2D!</p>
        <button class="btn" onclick="location.reload()" style="text-align: center; background: #eab308; color: black; font-weight: bold;">Играть еще раз</button>
    </div>

    <canvas id="arena" width="700" height="400" style="display:none;"></canvas>

    <script>
        const canvas = document.getElementById("arena");
        const ctx = canvas.getContext("2d");

        let p = { x: 100, y: 200, size: 30, emoji: '🐱', speed: 4, name: '', hp: 100, maxHp: 100 };
        let keys = {};
        let bullets = [];
        let enemies = [];
        let score = 0;
        let isPlay = false;

        function start(name, emoji, speed, hp) {
            document.getElementById("charMenu").style.display = "none";
            canvas.style.display = "block";
            p.name = name; p.emoji = emoji; p.speed = speed; p.hp = hp; p.maxHp = hp;
            isPlay = true;
            loop();
        }

        window.addEventListener("keydown", (e) => { keys[e.code] = true; if(e.code === "Space") shoot(); });
        window.addEventListener("keyup", (e) => { keys[e.code] = false; });
        canvas.addEventListener("mousedown", shoot);

        function shoot() {
            if (!isPlay) return;
            bullets.push({ x: p.x + 15, y: p.y + 8, speed: 10, size: 6 });
        }

        function loop() {
            if (!isPlay) return;
            requestAnimationFrame(loop);
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. Свободное управление котиком (WASD / Стрелочки)
            if (keys["KeyW"] || keys["ArrowUp"]) p.y -= p.speed;
            if (keys["KeyS"] || keys["ArrowDown"]) p.y += p.speed;
            if (keys["KeyA"] || keys["ArrowLeft"]) p.x -= p.speed;
            if (keys["KeyD"] || keys["ArrowRight"]) p.x += p.speed;

            // Ограничения границ арены
            p.x = Math.max(10, Math.min(canvas.width - 40, p.x));
            p.y = Math.max(10, Math.min(canvas.height - 40, p.y));

            // Рисуем стикер кота на арене
            ctx.font = p.size + "px Arial";
            ctx.textAlign = "left";
            ctx.textBaseline = "top";
            ctx.fillText(p.emoji, p.x, p.y);

            // 2. Полет и отрисовка лазерных пуль
            bullets.forEach((b, bIdx) => {
                b.x += b.speed;
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                ctx.fillStyle = "#22c55e"; // Зеленый лазер
                ctx.fill();
                ctx.closePath();
                if (b.x > canvas.width) bullets.splice(bIdx, 1);
            });

            // 3. Спавн и набег врагов (стикеры крыс)
            if (Math.random() < 0.025) {
                enemies.push({ x: canvas.width, y: Math.random() * (canvas.height - 50) + 10, speed: Math.random() * 1.5 + 2, size: 28 });
            }

            enemies.forEach((e, eIdx) => {
                e.x -= e.speed;
                ctx.font = e.size + "px Arial";
                ctx.fillText("🐀", e.x, e.y); // Стикер врага на арене

                // Столкновение пули с крысой
                bullets.forEach((b, bIdx) => {
                    if (b.x > e.x && b.x < e.x + 30 && b.y > e.y && b.y < e.y + 30) {
                        bullets.splice(bIdx, 1);
                        enemies.splice(eIdx, 1);
                        score += 10;
                        
                        // Проверка условия победы на 500 очков!
                        if (score >= 500) {
                            isPlay = false;
                            document.getElementById("winScreen").style.display = "block";
                        }
                    }
                });

                // Укус врага (урон коту)
                if (e.x < p.x + 25 && e.x + 25 > p.x && e.y < p.y + 25 && e.y + 25 > p.y) {
                    enemies.splice(eIdx, 1);
                    p.hp -= 20;
                    if (p.hp <= 0) {
                        alert("Ваш кот погиб в бою! Попробуйте снова.");
                        location.reload();
                    }
                }

                if (e.x < -30) enemies.splice(eIdx, 1);
            });

            // Игровой интерфейс шутера
            ctx.fillStyle = "white";
            ctx.font = "bold 16px Arial";
            ctx.fillText(`Кот: ${p.name}  |  ❤️ HP: ${p.hp}/${p.maxHp}  |  🎯 Очки: ${score} / 500`, 15, 20);
        }
    </script>
</body>
</html>
"""

# Встраиваем HTML5 арену внутрь Streamlit с фиксацией размеров окна
components.html(game_html, height=500)
