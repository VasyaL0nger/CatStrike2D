import streamlit as st
import streamlit.components.v1 as components
import time

# Настройка страницы шутера
st.set_page_config(page_title="CatStrike 2D", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; text-align: center; }
    .rank-box { background-color: #0f172a; border: 2px solid #22c55e; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Инициализация вашей кастомной экономики
if 'food' not in st.session_state: st.session_state.food = 0
if 'current_rank' not in st.session_state: st.session_state.current_rank = "начальный"

# Сетка рангов, которую вы придумали
RANKS_DICT = {
    "начальный": 0,
    "котенок": 5000,
    "кот": 10000,
    "питомец": 15000,
    "любимец": 20000,
    "томас": 25000,
    "рыжик": 30000,
    "буля": 35000,
    "мурка": 40000,
    "вася": 50000
}

# Определение множителя скорости врагов (сложности) на основе ранга
rank_index = list(RANKS_DICT.keys()).index(st.session_state.current_rank)
difficulty_speed_bonus = rank_index * 0.4  # Чем выше ранг, тем быстрее враги в JS

st.title("🐱 CatStrike 2D 🔫")

# Боковая панель управления
st.sidebar.markdown(f"## 🍖 Баланс: `{st.session_state.food}` еды")
st.sidebar.markdown(f"## 🎖️ Ваш Ранг: **{st.session_state.current_rank.upper()}**")

# Кнопка ручной прокачки ранга за еду
st.sidebar.write("---")
st.sidebar.subheader("Повышение звания")
rank_list = list(RANKS_DICT.keys())
current_idx = rank_list.index(st.session_state.current_rank)

if current_idx < len(rank_list) - 1:
    next_rank = rank_list[current_idx + 1]
    cost_next = RANKS_DICT[next_rank]
    st.sidebar.write(f"Следующий ранг: **{next_rank.upper()}**")
    st.sidebar.write(f"Стоимость: `{cost_next}` еды")
    if st.sidebar.button("🎖️ ПОВЫСИТЬ РАНГ"):
        # ИСПРАВЛЕНО: Заменили сломанную переменную на правильную cost_next
        if st.session_state.food < cost_next:
            st.sidebar.error("Не хватает еды для апгрейда ранга!")
        else:
            st.session_state.food -= cost_next
            st.session_state.current_rank = next_rank
            st.sidebar.success(f"Ранг повышен до {next_rank.upper()}!")
            st.rerun()
else:
    st.sidebar.success("👑 ВЫ ДОСТИГЛИ МАКСИМАЛЬНОГО РАНГА: ВАСЯ!")

# Главные вкладки хаба
tab_game, tab_profile = st.tabs(["🎮 Арена Боя", "👤 Профиль и Ранги"])

# ================= ВКЛАДКА 1: МАТЧ И АРЕНА =================
with tab_game:
    st.write("Цель матча: набрать **1000 очков**. За каждый выход или проигрыш выдается **100 еды**!")
    
    # Ловим результаты из JavaScript-игры
    query_params = st.query_params
    if "end_match" in query_params:
        st.session_state.food += 100
        st.query_params.clear()
        st.success("Матч завершен! Вам начислено 🍖 100 еды в инвентарь!")
        st.balloons()
        st.rerun()

    # Встраиваем игровой движок с учетом бонуса сложности от ранга
    game_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #020617; color: white; font-family: Arial, sans-serif; text-align: center; overflow: hidden; }}
            canvas {{ background-color: #090d16; border: 3px solid #22c55e; border-radius: 8px; display: block; margin: 5px auto; }}
            .menu-box {{ max-width: 500px; margin: 10px auto; background: #0f172a; padding: 15px; border-radius: 12px; border: 2px solid #22c55e; }}
            .btn {{ background: #1e293b; color: white; border: 1px solid #475569; padding: 10px; margin: 5px; border-radius: 6px; cursor: pointer; text-align: left; width: 95%; font-size: 14px; }}
            .btn:hover {{ background: #16a34a; border-color: #4ade80; }}
        </style>
    </head>
    <body>
        <div id="charMenu" class="menu-box">
            <h3>ВЫБЕРИТЕ КОТА (Сложность: +{difficulty_speed_bonus:.1f} скор.):</h3>
            <button class="btn" onclick="start('Vasya', '🐱', 3.5, 150)">🐱 <b>Vasya</b> — Твой штурмовик. 150 HP.</button>
            <button class="btn" onclick="start('Bulya', '🐱', 4, 100)">🐱 <b>Bulya</b> — Белая, нежная. 100 HP.</button>
            <button class="btn" onclick="start('Murka', '🐱', 4.5, 110)">🐱 <b>Murka</b> — Черная, боевая. 110 HP.</button>
            <button class="btn" onclick="start('Rizyk', '🐱', 6, 90)">🐱 <b>Rizyk</b> — Рыжий. Быстрый. 90 HP.</button>
            <button class="btn" onclick="start('Tomas', '🐱', 5, 120)">🐱 <b>Tomas</b> — Полосатый друг Рыжика. 120 HP.</button>
        </div>

        <canvas id="arena" width="680" height="360" style="display:none;"></canvas>

        <script>
            const canvas = document.getElementById("arena");
            const ctx = canvas.getContext("2d");
            let p = {{ x: 100, y: 180, size: 30, emoji: '🐱', speed: 4, name: '', hp: 100, maxHp: 100 }};
            let keys = {{}}; let bullets = []; let enemies = []; let score = 0; let isPlay = false;
            
            let speedBonus = {difficulty_speed_bonus}; 

            function start(name, emoji, speed, hp) {{
                document.getElementById("charMenu").style.display = "none";
                canvas.style.display = "block";
                p.name = name; p.emoji = emoji; p.speed = speed; p.hp = hp; p.maxHp = hp;
                isPlay = true; loop();
            }}

            window.addEventListener("keydown", (e) => {{ keys[e.code] = true; if(e.code === "Space") shoot(); }});
            window.addEventListener("keyup", (e) => {{ keys[e.code] = false; }});
            canvas.addEventListener("mousedown", shoot);

            function shoot() {{ if (!isPlay) return; bullets.push({{ x: p.x + 15, y: p.y + 8, speed: 10, size: 6 }}); }}

            function finishMatch() {{
                isPlay = false;
                window.parent.location.search = "?end_match=1";
            }}

            function loop() {{
                if (!isPlay) return;
                requestAnimationFrame(loop);
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (keys["KeyW"] || keys["ArrowUp"]) p.y -= p.speed;
                if (keys["KeyS"] || keys["ArrowDown"]) p.y += p.speed;
                if (keys["KeyA"] || keys["ArrowLeft"]) p.x -= p.speed;
                if (keys["KeyD"] || keys["ArrowRight"]) p.x += p.speed;

                p.x = Math.max(10, Math.min(canvas.width - 40, p.x));
                p.y = Math.max(10, Math.min(canvas.height - 40, p.y));

                ctx.font = p.size + "px Arial";
                ctx.fillText(p.emoji, p.x, p.y);

                bullets.forEach((b, bIdx) => {{
                    b.x += b.speed;
                    ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2); ctx.fillStyle = "#22c55e"; ctx.fill();
                    if (b.x > canvas.width) bullets.splice(bIdx, 1);
                }});

                if (Math.random() < 0.025) {{
                    enemies.push({{ x: canvas.width, y: Math.random() * (canvas.height - 50) + 10, speed: (Math.random() * 1.5 + 2) + speedBonus, size: 28 }});
                }}

                enemies.forEach((e, eIdx) => {{
                    e.x -= e.speed;
                    ctx.font = e.size + "px Arial"; ctx.fillText("🐀", e.x, e.y);

                    bullets.forEach((b, bIdx) => {{
                        if (b.x > e.x && b.x < e.x + 30 && b.y > e.y && b.y < e.y + 30) {{
                            bullets.splice(bIdx, 1); enemies.splice(eIdx, 1);
                            score += 10;
                            if (score >= 1000) finishMatch();
                        }}
                    }});

                    if (e.x < p.x + 25 && e.x + 25 > p.x && e.y < p.y + 25 && e.y + 25 > p.y) {{
                        enemies.splice(eIdx, 1);
                        p.hp -= 20;
                        if (p.hp <= 0) finishMatch();
                    }}
                    if (e.x < -30) enemies.splice(eIdx, 1);
                }});

                ctx.fillStyle = "white"; ctx.font = "bold 16px Arial";
                ctx.fillText(`Кот: ${{p.name}}  |  ❤️ HP: ${{p.hp}}/${{p.maxHp}}  |  🎯 Очки: ${{score}} / 1000`, 15, 25);
            }}
        </script>
    </body>
    </html>
    """
    components.html(game_html, height=410)

# ================= ВКЛАДКА 2: ТАБЛИЦА РАНГОВ =================
with tab_profile:
    st.header("🎖️ Твоя карьерная лестница в CatStrike 2D")
    st.write("Собирай еду в боях и повышай статус своей кошачьей банды:")
    
    for r_name, r_cost in RANKS_DICT.items():
        is_current = "👈 ТЕКУЩИЙ РАНГ" if st.session_state.current_rank == r_name else ""
        st.markdown(f"""
            <div class="rank-box">
                <h3 style='margin: 0; color: #4ade80;'>{r_name.upper()} {is_current}</h3>
                <p style='margin: 5px 0 0 0; color: #94a3b8;'>Стоимость активации: {r_cost} еды</p>
            </div>
        """, unsafe_allow_html=True)

# Кнопка читерского теста для начисления еды
if st.sidebar.button("🧪 Тест: Выдать +5000 еды"):
    st.session_state.food += 5000
    st.rerun()

