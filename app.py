import streamlit as st
import os, json, random

st.set_page_config(page_title="CatStrike 2D", layout="centered")

# --- СИСТЕМА СОХРАНЕНИЯ ПРОГРЕССА ---
SAVE_FILE = "save_data.json"
def load_game():
    if os.path.exists(SAVE_FILE):
        try: return json.load(open(SAVE_FILE, "r"))
        except: pass
    return {"food": 0, "current_rank": "начальный"}

if 'save_init' not in st.session_state:
    saved = load_game()
    st.session_state.food = saved["food"]
    st.session_state.current_rank = saved["current_rank"]
    st.session_state.save_init = True

# Инициализация игрового процесса матча на сервере
if 'playing' not in st.session_state: st.session_state.playing = False
if 'p_x' not in st.session_state: st.session_state.p_x = 1
if 'e_x' not in st.session_state: st.session_state.e_x = 9
if 'p_hp' not in st.session_state: st.session_state.p_hp = 100
if 'p_score' not in st.session_state: st.session_state.p_score = 0
if 'cat_name' not in st.session_state: st.session_state.cat_name = "Vasya"

RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
rank_list = list(RANKS.keys())
current_idx = rank_list.index(st.session_state.current_rank)

# Панель игрока в сайдбаре
st.sidebar.markdown(f"## 🍖 Баланс: `{st.session_state.food}` еды")
st.sidebar.markdown(f"## 🎖️ Ранг: **{st.session_state.current_rank.upper()}**")

if current_idx < len(rank_list) - 1:
    next_r = rank_list[current_idx + 1]
    if st.sidebar.button(f" апнуть ранг за {RANKS[next_r]}".upper()):
        if st.session_state.food >= RANKS[next_r]:
            st.session_state.food -= RANKS[next_r]
            st.session_state.current_rank = next_r
            json.dump({"food": st.session_state.food, "current_rank": next_r}, open(SAVE_FILE, "w"))
            st.rerun()
        else: st.sidebar.error("Не хватает еды!")

# --- ГЛАВНЫЙ ЭКРАН ИГРЫ ---
st.title("🐱 CatStrike 2D 🔫")

tab_g, tab_p = st.tabs([" Арена Боя", " Профиль"])

with tab_g:
    # РЕЖИМ 1: ВЫБОР ПЕРСОНАЖА (ЛОББИ)
    if not st.session_state.playing:
        st.subheader("Сбор кошачьего отряда")
        st.session_state.cat_name = st.selectbox("Выбери бойца:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
        
        if st.button(" ВСТУПИТЬ В БОЙ", use_container_width=True):
            st.session_state.p_hp = 2000 if st.session_state.cat_name == "ADMIN" else 120
            st.session_state.p_x = 1
            st.session_state.e_x = 9
            st.session_state.p_score = 0
            st.session_state.playing = True
            st.rerun()

    # РЕЖИМ 2: АКТИВНЫЙ МАТЧ НА СЕРВЕРЕ PYTHON
    else:
        # Проверка условий окончания матча силами сервера
        if st.session_state.p_score >= 500:
            st.session_state.food += 100
            json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
            st.session_state.playing = False
            st.balloons()
            st.success(" ПОБЕДА! Вы набрали 500 очков. +100 еды автоматически начислено!")
            time_to_sleep = time.sleep(1) if 'time' in globals() else None
            st.rerun()
            
        if st.session_state.p_hp <= 0:
            st.session_state.playing = False
            st.error(" Боец погиб на арене. Награда не начислена.")
            st.rerun()

        # Интерфейс матча
        col_name, col_hp, col_score = st.columns(3)
        with col_name: st.write(f"**Боец:** {st.session_state.cat_name}")
        with col_hp: st.write(f"❤️ **HP:** {st.session_state.p_hp}")
        with col_score: st.write(f"🎯 **Очки:** {st.session_state.p_score} / 500")

        # Рендеринг 2D-сетки арены со стикерами
        arena_slots = ["_"] * 11
        arena_slots[st.session_state.p_x] = "🐱" if st.session_state.cat_name != "ADMIN" else "👑"
        arena_slots[st.session_state.e_x] = "🐀"
        
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 5px;'>{' '.join(arena_slots)}</h1>", unsafe_allow_html=True)
        st.write("---")

        # Тактические кнопки управления
        col_b1, col_b2, col_b3 = st.columns(3)
        
        with col_b1:
            if st.button("⬅️ Шаг Назад"):
                st.session_state.p_x = max(0, st.session_state.p_x - 1)
                if random.choice([True, False]): st.session_state.e_x -= 1
                st.rerun()
                
        with col_b2:
            if st.button("💥 ВЫСТРЕЛ (ОГОНЬ)"):
                # Кулдаун пули мгновенный на Python. Рассчитываем попадание
                if st.session_state.cat_name == "ADMIN" or random.randint(1, 10) > 3:
                    st.session_state.p_score += 50 if st.session_state.cat_name == "ADMIN" else 20
                    st.session_state.e_x = 9 # Спавним новую крысу сзади
                else:
                    st.session_state.p_hp -= random.randint(10, 20)
                if random.choice([True, False]): st.session_state.e_x -= 1
                st.rerun()
                
        with col_b3:
            if st.button("➡️ Шаг Вперед"):
                st.session_state.p_x = min(st.session_state.e_x - 1, st.session_state.p_x + 1)
                st.session_state.e_x -= 1
                st.rerun()

        # Если крыса дошла до кота
        if st.session_state.e_x <= st.session_state.p_x:
            st.session_state.p_hp -= 25
            st.session_state.e_x = 9
            st.rerun()

with tab_p:
    st.header(" Сетка твоих званий")
    for r_n, r_c in RANKS.items():
        is_curr = " (Текущий)" if st.session_state.current_rank == r_n else ""
        st.write(f"• **{r_n.upper()}** — требуется {r_c} еды {is_curr}")

if st.sidebar.button("🧪 Читы: +5000 еды"):
    st.session_state.food += 5000
    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
    st.rerun()
