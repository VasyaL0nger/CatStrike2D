import streamlit as st
import random

# Настройка страницы
st.set_page_config(page_title="CatStrike 2D", layout="centered")

# Стили оформления
st.markdown("""
    <style>
    .stApp { background-color: #020617; color: white; }
    .game-box { background-color: #0f172a; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Официальный ростер персонажей
STATS = {
    "Vasya": {"speed": 4, "hp": 150, "desc": "Ленивый, харизматичный, мудрый кошачий король. Тяжелая броня из-за любви к пельменям.", "char": "V"},
    "Bulya": {"speed": 4, "hp": 100, "desc": "Белая кошка. Безумно любит, когда её гладят. Очень нежная. Умеет лечить себя мурлыканьем.", "char": "B"},
    "Murka": {"speed": 5, "hp": 110, "desc": "Чёрная кошка. Любит играться и царапать людей. Наносит повышенный урон когтями.", "char": "M"},
    "Rizyk": {"speed": 8, "hp": 90, "desc": "Рыжий кот. Очень быстрый и смертельно опасный. Легко уворачивается от атак.", "char": "R"},
    "Tomas": {"speed": 6, "hp": 120, "desc": "Чёрный кот с белыми полосками. Лучший друг Рыжика. Обладает бешеной скоростью.", "char": "T"}
}

# Инициализация игровых переменных в памяти Streamlit
if 'game_started' not in st.session_state: st.session_state.game_started = False
if 'cat_choice' not in st.session_state: st.session_state.cat_choice = "Vasya"
if 'player_x' not in st.session_state: st.session_state.player_x = 1
if 'enemy_x' not in st.session_state: st.session_state.enemy_x = 9
if 'bullet_x' not in st.session_state: st.session_state.bullet_x = -1  # -1 означает, что пули на экране нет
if 'player_hp' not in st.session_state: st.session_state.player_hp = 100
if 'score' not in st.session_state: st.session_state.score = 0
if 'battle_logs' not in st.session_state: st.session_state.battle_logs = ["Отряд готов к бою. Выберите бойца."]

st.title("CatStrike 2D")
st.write("Интерактивный пошаговый прототип 2D арены шутера.")

# ================= ЭКРАН ВЫБОРА ПЕРСОНАЖА =================
if not st.session_state.game_started:
    st.header("Выбор персонажа")
    selected_name = st.selectbox("Доступные бойцы:", list(STATS.keys()))
    cat_data = STATS[selected_name]
    
    st.markdown(f"""
        <div class="game-box">
            <h2>{selected_name}</h2>
            <p style='color: #94a3b8; font-size: 16px;'>{cat_data['desc']}</p>
            <p>Скорость бега: {cat_data['speed']} | Здоровье (HP): {cat_data['hp']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("В БОЙ", use_container_width=True):
        st.session_state.cat_choice = selected_name
        st.session_state.player_hp = cat_data["hp"]
        st.session_state.player_x = 1
        st.session_state.enemy_x = 9
        st.session_state.bullet_x = -1
        st.session_state.score = 0
        st.session_state.battle_logs = [f"Матч начался. {selected_name} высадился на арену."]
        st.session_state.game_started = True
        st.rerun()

# ================= ИГРОВОЙ ПРОЦЕСС (МАТЧ НА АРЕНЕ) =================
else:
    cat_char = STATS[st.session_state.cat_choice]["char"]
    max_hp = STATS[st.session_state.cat_choice]["hp"]
    
    # Игровая статистика
    col_info, col_hp, col_score = st.columns(3)
    with col_info: st.markdown(f"**Персонаж:** {st.session_state.cat_choice}")
    with col_hp: st.markdown(f"**HP:** `{st.session_state.player_hp} / {max_hp}`")
    with col_score: st.markdown(f"**Убито врагов:** `{st.session_state.score}`")
    
    st.write("---")
    
    # Логика пошагового движения пули и врага перед отрисовкой карты
    # Если пуля летит, двигаем её вправо
    if st.session_state.bullet_x != -1:
        st.session_state.bullet_x += 2  # Пуля летит быстро (через клетку)
        if st.session_state.bullet_x >= st.session_state.enemy_x:
            # Попадание во врага!
            st.session_state.score += 10
            st.session_state.battle_logs.insert(0, "Успешное попадание. Враг ликвидирован. Снаряд уничтожен.")
            st.session_state.enemy_x = 9  # Спавним нового врага в конце карты
            st.session_state.bullet_x = -1
        elif st.session_state.bullet_x > 9:
            # Пуля улетела за карту
            st.session_state.bullet_x = -1
            st.session_state.battle_logs.insert(0, "Промах. Пуля улетела за пределы видимости арены.")

    # Логика движения врага (он наступает влево на 1 клетку каждый ход)
    if st.session_state.game_started and random.choice([True, False]): # 50% шанс шага врага за действие игрока
        st.session_state.enemy_x -= 1
        
    # Проверка столкновения врага с котом
    if st.session_state.enemy_x <= st.session_state.player_x:
        damage = random.randint(15, 30)
        st.session_state.player_hp -= damage
        st.session_state.battle_logs.insert(0, f"Враг прорвал дистанцию и нанес урон: -{damage} HP.")
        st.session_state.enemy_x = 9  # Отбрасываем нового врага назад

    # РЕНДЕРИНГ 2D АРЕНЫ ИЗ 11 КЛЕТОК
    map_length = 11
    grid = ["_"] * map_length
    
    # Заполняем позиции на поле
    if st.session_state.bullet_x != -1 and st.session_state.bullet_x < map_length:
        grid[st.session_state.bullet_x] = "•"  # Обозначение летящей пули
    grid[st.session_state.player_x] = f"[{cat_char}]"  # Обозначение вашего кота
    grid[st.session_state.enemy_x] = "[E]"  # Обозначение врага (Enemy)
    
    # Выводим арену на экран
    map_visual = " ".join(grid)
    st.markdown(f"<h1 style='text-align: center; font-family: monospace; letter-spacing: 3px;'>{map_visual}</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # КНОПКИ ДЕЙСТВИЙ (УПРАВЛЕНИЕ ТАКТИЧЕСКИМ МАТЧЕМ)
    col_left, col_shoot, col_right, col_skill = st.columns(4)
    
    with col_left:
        if st.button("Шаг Назад", use_container_width=True):
            st.session_state.player_x = max(0, st.session_state.player_x - 1)
            st.session_state.battle_logs.insert(0, "Вы сместились назад по тактической сетке.")
            st.rerun()
            
    with col_right:
        if st.button("Шаг Вперед", use_container_width=True):
            st.session_state.player_x = min(st.session_state.enemy_x - 1, st.session_state.player_x + 1)
            st.session_state.battle_logs.insert(0, "Вы сократили дистанцию с противником.")
            st.rerun()
            
    with col_shoot:
        # Кнопка выстрела активирует летящую пулю
        if st.button("ОГОНЬ", use_container_width=True):
            if st.session_state.bullet_x == -1:
                st.session_state.bullet_x = st.session_state.player_x + 1
                st.session_state.battle_logs.insert(0, "Произведен выстрел. Пуля выпущена на арену.")
            else:
                st.session_state.battle_logs.insert(0, "Отказ системы: предыдущий снаряд еще в полете.")
            st.rerun()
            
    with col_skill:
        if st.button("СУПЕРСКИЛЛ", use_container_width=True):
            if st.session_state.cat_choice == "Vasya":
                st.session_state.enemy_x = min(9, st.session_state.enemy_x + 2)
                st.session_state.battle_logs.insert(0, "Vasya применил Гипноз. Враг отброшен назад на 2 клетки.")
            elif st.session_state.cat_choice == "Bulya":
                st.session_state.player_hp = min(max_hp, st.session_state.player_hp + 25)
                st.session_state.battle_logs.insert(0, "Нежная Bulya восстановила себе +25 HP за счет мурлыканья.")
            elif st.session_state.cat_choice == "Murka":
                st.session_state.score += 10
                st.session_state.enemy_x = 9
                st.session_state.battle_logs.insert(0, "Murka совершила прыжок когтями вперед. Враг уничтожен ближним боем.")
            elif st.session_state.cat_choice == "Rizyk":
                st.session_state.player_x = max(0, st.session_state.player_x - 2)
                st.session_state.battle_logs.insert(0, "Рыжик активировал супер-скорость и разорвал дистанцию на 2 клетки назад.")
            elif st.session_state.cat_choice == "Tomas":
                st.session_state.score += 10
                st.session_state.enemy_x = 9
                st.session_state.battle_logs.insert(0, "Tomas открыл шквальный полосатый огонь. Враг на позиции ликвидирован.")
            st.rerun()

    # Проверка на Game Over
    if st.session_state.player_hp <= 0:
        st.error(f"Боец {st.session_state.cat_choice} погиб на поле боя. Игра окончена.")
        st.markdown(f"### Итоговый результат в CatStrike 2D: `{st.session_state.score} очков`")
        if st.button("Вернуться в меню выбора бойцов", use_container_width=True):
            st.session_state.game_started = False
            st.rerun()
            
    # Журнал логов боя
    st.write("")
    st.subheader("Лог боя:")
    for log in st.session_state.battle_logs[:4]:
        st.write(log)

    st.write("---")
    if st.button("Покинуть матч"):
        st.session_state.game_started = False
        st.rerun()
