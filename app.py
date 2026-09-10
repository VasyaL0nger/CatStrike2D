import streamlit as st
import random
import time

# Настройка страницы игры
st.set_page_config(page_title="CatStrike 2D", page_icon="🔫", layout="centered")

# --- СТИЛИ ДЛЯ ИГРОВОГО ЭКРАНА ---
st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; }
    .game-box { background-color: #0f172a; border: 3px solid #22c55e; border-radius: 12px; padding: 20px; text-align: center; }
    .stats { font-size: 20px; font-weight: bold; color: #4ade80; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Официальные данные ваших персонажей CatStrike 2D
CATS_ROSTER = {
    "Vasya": {"speed": 4, "hp": 150, "desc": "Ленивый, харизматичный, мудрый кошачий король. Тяжелая броня из-за любви к пельменям.", "emoji": "🐱"},
    "Bulya": {"speed": 4, "hp": 100, "desc": "Белая кошка. Безумно любит, когда её гладят. Очень нежная. Умеет лечить себя мурлыканьем.", "emoji": "🐱✨"},
    "Murka": {"speed": 5, "hp": 110, "desc": "Чёрная кошка. Любит играться и царапать людей. Наносит повышенный урон когтями.", "emoji": "🥷"},
    "Rizyk (Рыжик)": {"speed": 8, "hp": 90, "desc": "Рыжий кот. Очень быстрый и смертельно опасный. Легко уворачивается от атак врагов.", "emoji": "🦁"},
    "Tomas": {"speed": 6, "hp": 120, "desc": "Чёрный кот с белыми полосками. Лучший друг Рыжика. Обладает бешеной скоростью.", "emoji": "🐯"}
}

# Инициализация игровых переменных в памяти Streamlit
if 'game_started' not in st.session_state: st.session_state.game_started = False
if 'cat_choice' not in st.session_state: st.session_state.cat_choice = "Vasya"
if 'player_x' not in st.session_state: st.session_state.player_x = 3
if 'player_hp' not in st.session_state: st.session_state.player_hp = 100
if 'score' not in st.session_state: st.session_state.score = 0
if 'battle_logs' not in st.session_state: st.session_state.battle_logs = ["Ваш отряд готов к бою! Нажмите кнопку 'В бой'."]

st.title("🐾 CatStrike 2D — Боевые Коты 🔫")
st.write("Официальный интерактивный прототип геймплея шутера!")

# ================= ЭКРАН ВЫБОРА ПЕРСОНАЖА =================
if not st.session_state.game_started:
    st.header("👤 Сбор боевого отряда")
    st.write("Выберите кота, который поведет команду в атаку:")
    
    selected_name = st.selectbox("Доступные бойцы:", list(CATS_ROSTER.keys()))
    cat_data = CATS_ROSTER[selected_name]
    
    # Карточка персонажа
    st.markdown(f"""
        <div class="game-box">
            <h1 style='font-size: 70px; margin: 0;'>{cat_data['emoji']}</h1>
            <h2>{selected_name}</h2>
            <p style='color: #94a3b8; font-size: 16px;'>{cat_data['desc']}</p>
            <p><b>Скорость бега:</b> {cat_data['speed']} | <b>Здоровье (HP):</b> {cat_data['hp']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🚀 НАЧАТЬ ИГРОВОЙ МАТЧ", use_container_width=True):
        st.session_state.cat_choice = selected_name
        st.session_state.player_hp = cat_data["hp"]
        st.session_state.player_x = 3
        st.session_state.score = 0
        st.session_state.battle_logs = [f"⚔️ {selected_name} высадился на поле боя! Навстречу бегут враги!"]
        st.session_state.game_started = True
        st.rerun()

# ================= ИГРОВОЙ ПРОЦЕСС (МАТЧ) =================
else:
    cat_data = CATS_ROSTER[st.session_state.cat_choice]
    
    # Панель состояния кота
    col_info, col_hp, col_score = st.columns(3)
    with col_info: st.markdown(f"**Боец:** {cat_data['emoji']} {st.session_state.cat_choice}")
    with col_hp: st.markdown(f"❤️ **Здоровье:** `{st.session_state.player_hp} / {cat_data['hp']}`")
    with col_score: st.markdown(f"🎯 **Очки (Убито врагов):** `{st.session_state.score}`")
    
    st.write("---")
    
    # Визуализация 2D карты
    map_length = 10
    grid = ["⬛"] * map_length
    grid[st.session_state.player_x] = cat_data['emoji']
    
    enemy_pos = 8
    grid[enemy_pos] = "🐀"
    
    map_visual = " ".join(grid)
    st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px;'>{map_visual}</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # КНОПКИ УПРАВЛЕНИЯ ШУТЕРОМ
    col_left, col_shoot, col_right, col_skill = st.columns(4)
    
    with col_left:
        if st.button("⬅️ Назад", use_container_width=True):
            st.session_state.player_x = max(0, st.session_state.player_x - 1)
            st.session_state.battle_logs.insert(0, "🏃 Вы отступили назад на одну позицию.")
            st.rerun()
            
    with col_right:
        if st.button("➡️ Вперед", use_container_width=True):
            st.session_state.player_x = min(6, st.session_state.player_x + 1)
            st.session_state.battle_logs.insert(0, "🏃 Вы рванули вперед навстречу врагу!")
            st.rerun()
            
    with col_shoot:
        if st.button("💥 СТРЕЛЯТЬ (Оружие)", use_container_width=True):
            with st.spinner("ТРА-ТА-ТА..."): time.sleep(0.2)
            damage_chance = random.randint(1, 10)
            if damage_chance > 3:
                st.session_state.score += 10
                st.session_state.battle_logs.insert(0, f"🎯 CatStrike! Точный выстрел! Вражеская крыса ликвидирована! (+10 очков)")
            else:
                st.session_state.player_hp -= random.randint(15, 25)
                st.session_state.battle_logs.insert(0, "💨 Промах! Враг увернулся и укусил вас в ответ!")
            st.rerun()
            
    with col_skill:
        if st.button("⚡ СУПЕРСКИЛЛ", use_container_width=True):
            if st.session_state.cat_choice == "Vasya":
                st.session_state.score += 5
                st.session_state.battle_logs.insert(0, "👁️ Vasya применил Гипнотический Взгляд! Враги замерли в ужасе, вы получили халявные очки.")
            elif st.session_state.cat_choice == "Bulya":
                st.session_state.player_hp = min(cat_data['hp'], st.session_state.player_hp + 30)
                st.session_state.battle_logs.insert(0, "🧼 Нежная Bulya начала мурлыкать — восстановлено +30 HP!")
            elif st.session_state.cat_choice == "Murka":
                st.session_state.score += 20
                st.session_state.battle_logs.insert(0, "😼 Чёрная Мурка прыгнула из тени и бешено расцарапала врагов когтями! (+20 очков)")
            elif st.session_state.cat_choice == "Rizyk (Рыжик)":
                st.session_state.player_x = max(0, st.session_state.player_x - 3)
                st.session_state.battle_logs.insert(0, "⚡ Очень быстрый Рыжик совершил тактический супер-рывок назад, уйдя от атаки.")
            elif st.session_state.cat_choice == "Tomas":
                st.session_state.score += 15
                st.session_state.battle_logs.insert(0, "🔫 Томас активировал огневую мощь полосатого штурмовика и засыпал карту пулями!")
            st.rerun()

    # Проверка на проигрыш
    if st.session_state.player_hp <= 0:
        st.error(f"💀 Ваш боец {st.session_state.cat_choice} пал в бою! Игра окончена.")
        st.markdown(f"### Финальный счет в CatStrike 2D: `{st.session_state.score} очков`")
        if st.button("🔄 Вернуться в меню выбора котиков", use_container_width=True):
            st.session_state.game_started = False
            st.rerun()
            
    st.write("")
    st.subheader("📰 Лог боя:")
    for log in st.session_state.battle_logs[:5]:
        st.write(log)

    st.write("---")
    if st.button("❌ Сдаться и выйти"):
        st.session_state.game_started = False
        st.rerun()
