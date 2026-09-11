import streamlit as st
import os, json

st.set_page_config(page_title="CatStrike 2D", layout="centered")

# --- БАЗА ДАННЫХ АККАУНТОВ ---
DB_FILE = "users_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try: return json.load(open(DB_FILE, "r"))
        except: pass
    return {}

if 'logged_user' not in st.session_state: st.session_state.logged_user = None
if 'match_playing' not in st.session_state: st.session_state.match_playing = False

# ================= АВТОРИЗАЦИЯ =================
if not st.session_state.logged_user:
    st.title("🐱 CatStrike 2D: Вход 🔐")
    auth_mode = st.radio("Действие:", ["Войти", "Регистрация"], horizontal=True)
    user_in = st.text_input("Логин:").strip().lower()
    pass_in = st.text_input("Пароль:", type="password").strip()
    db = load_db()
    
    if auth_mode == "Регистрация" and st.button("🆕 СОЗДАТЬ АККАУНТ", use_container_width=True):
        if user_in and pass_in and user_in not in db:
            db[user_in] = {"password": pass_in, "food": 100, "rank": "начальный"}
            json.dump(db, open(DB_FILE, "w"))
            st.success("Успех! Теперь выберите 'Войти'.")
        else: st.error("Ошибка регистраци!")
    elif auth_mode == "Войти" and st.button("🔓 ВОЙТИ В ШТАБ", use_container_width=True):
        if user_in in db and db[user_in]["password"] == pass_in:
            st.session_state.logged_user = user_in
            st.session_state.food, st.session_state.current_rank = db[user_in]["food"], db[user_in]["rank"]
            st.rerun()
        else: st.error("Неверный логин или пароль!")
    st.stop()

# --- СЕССИЯ ИГРОКА ---
user = st.session_state.logged_user
db = load_db()
RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
rank_list = list(RANKS.keys())
current_idx = rank_list.index(st.session_state.current_rank)
speed_bonus = current_idx * 0.4

# ШЛЮЗ НАГРАДЫ
if "secure_token" in st.query_params and st.query_params["secure_token"] == "cat_win_777":
    db[user]["food"] += 100
    json.dump(db, open(DB_FILE, "w"))
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in st.query_params:
    st.query_params.clear()
    st.session_state.match_playing = False
    st.rerun()

st.sidebar.markdown(f"👤 Кот: **{user.upper()}**\n## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.current_rank.upper()}**")

if current_idx < len(rank_list) - 1 and st.sidebar.button(f"🎖️ АПНУТЬ РАНГ ЗА {RANKS[rank_list[current_idx+1]]}"):
    next_r = rank_list[current_idx+1]
    if st.session_state.food >= RANKS[next_r]:
        st.session_state.food -= RANKS[next_r]
        st.session_state.current_rank = next_r
        db[user]["food"], db[user]["rank"] = st.session_state.food, next_r
        json.dump(db, open(DB_FILE, "w"))
        st.rerun()

if st.sidebar.button("🚪 Выйти"):
    st.session_state.logged_user = None
    st.rerun()

tab_g, tab_p = st.tabs(["🎮 Арена Боя", "👤 Профиль"])

with tab_g:
    # ================= ЛОББИ БАЗЫ =================
    if not st.session_state.match_playing:
        c_room, c_desc = st.columns(2) # ИСПРАВЛЕНО: Теперь тут стоит цифра 2!
        with c_room:
            st.markdown("""
            <style>
                .room { background:#0f172a; border:2px solid #22c55e; border-radius:8px; height:200px; position:relative; }
                .obj { position:absolute; font-size:25px; text-decoration:none; }
                .tag { display:block; font-size:10px; color:white; background:rgba(0,0,0,0.6); padding:2px; border-radius:3px; }
            </style>
            <div class="room">
                <a href="?cat=v" target="_self" class="obj" style="bottom:20px; left:90px;">🐱<span class="tag">Вася</span></a>
                <a href="?cat=b" target="_self" class="obj" style="bottom:10px; left:15px;">🐱✨<span class="tag">Буля</span></a>
                <a href="?cat=m" target="_self" class="obj" style="top:70px; left:20px;">🥷<span class="tag">Мурка</span></a>
                <a href="?cat=r" target="_self" class="obj" style="top:20px; right:70px;">🦁<span class="tag">Рыжик</span></a>
                <a href="?cat=t" target="_self" class="obj" style="top:20px; right:15px;">🐯<span class="tag">Томас</span></a>
            </div>
            """, unsafe_allow_html=True)
            
        with c_desc:
            cat = st.query_params.get("cat", "none")
            if cat == "v":
                st.write("🐾 **Вася**: Спит на кресле.")
                if st.button("🥟 Дать пельмень (50 еды)") and st.session_state.food >= 50:
                    st.session_state.food -= 50
                    db[user]["food"] = st.session_state.food
                    json.dump(db, open(DB_FILE, "w"))
                    st.success("Вася сыто мурчит!")
            elif cat == "b":
                st.write("🐾 **Буля**: Белая и нежная.")
                if st.button("🧼 Погладить"): st.info("Буля мурчит!")
            elif cat == "m": st.warning("🥷 **Мурка**: Царапается!")
            elif cat == "r": st.write("🦁 **Рыжик**: Быстрый боец.")
            elif cat == "t": st.write("🐯 **Томас**: Штурмовик.")
            else: st.info("Кликни кота на базе!")

        chosen = st.selectbox("Боец в рейд:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
        if st.button("⚔️ В БОЙ", use_container_width=True):
            st.session_state.match_playing = True
            st.session_state.chosen_hero = chosen
            st.query_params.clear()
            st.rerun()

    # ================= АРЕНА ИГРЫ =================
    else:
        if st.button("↩️ ВЕРНУТЬСЯ В ШТАБ", use_container_width=True):
            st.session_state.match_playing = False
            st.rerun()
        hp = 2000 if st.session_state.chosen_hero == "ADMIN" else 120
        cd = 2 if st.session_state.chosen_hero == "ADMIN" else 10

        game_html = f"""
        <!DOCTYPE html><html><head><style>
            body {{ margin:0; background:#020617; color:white; text-align:center; font-family:Arial; user-select:none; }}
            canvas {{ background:#090d16; border:3px solid #22c55e; border-radius:8px; margin:5px auto; }}
            .link {{ display:none; background:#22c55e; color:black; font-weight:bold; padding:12px; border-radius:6px; text-decoration:none; width:90%; font-size:16px; display:inline-block; }}
        </style></head><body>
            <canvas id="arena" width="650" height="350"></canvas>
            <a id="jsWin" class="link" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
            <a id="jsLose" class="link" style="background:#ef4444; color:white;" href="" target="_parent">❌ ВЫЙТИ В МЕНЮ</a>
            <script>
                const canvas = document.getElementById("arena"), ctx = canvas.getContext("2d");
                const jsWin = document.getElementById("jsWin"), jsLose = document.getElementById("jsLose");
                let p = {{x:100, y:160, size:30, emoji: '{'👑' if st.session_state.chosen_hero=='ADMIN' else '🐱'}', speed:4, hp:{hp}, maxHp:{hp}, name:'{st.session_state.chosen_hero}', cd:{cd}}}, keys={{}}, bullets=[], enemies=[], score=0, isPlay=true, timer=0;
                window.addEventListener("keydown",(e)=>{{ if(isPlay) keys[e.code]=true; }});
                window.addEventListener("keyup",(e)=>{{ keys[e.code] = false; }});
                canvas.addEventListener("mousedown",()=>{{ if(isPlay && timer<=0) shoot(); }});
                function shoot() {{ bullets.push({{x:p.x+15, y:p.y+8, speed:12}}); timer = p.cd; }}
                function finish(res) {{ 
                    if(!isPlay) return; isPlay = false; 
                    ctx.fillStyle="rgba(15,17,26,0.9)"; ctx.fillRect(0,0,canvas.width,canvas.height); 
                    ctx.fillStyle = res === "win" ? "#22c55e" : "#ef4444"; ctx.font="bold 30px Arial"; ctx.fillText(res === "win" ? "ПОБЕДА!" : "ВЫ ПОГИБЛИ", 230, 160); 
                    const base = window.parent.location.origin + window.parent.location.pathname;
                    if(res === "win") {{ jsWin.href = base + "?secure_token=cat_win_777"; jsWin.style.display = "block"; }} 
                    else {{ jsLose.href = base + "?status=lose"; jsLose.style.display = "block"; }}
                }}
                function loop() {{ if(!isPlay) return; requestAnimationFrame(loop); ctx.clearRect(0,0,canvas.width,canvas.height);
                    if(keys["KeyW"]||keys["ArrowUp"]) p.y-=p.speed; if(keys["KeyS"]||keys["ArrowDown"]) p.y+=p.speed; if(keys["KeyA"]||keys["ArrowLeft"]) p.x-=p.speed; if(keys["KeyD"]||keys["ArrowRight"]) p.x+=p.speed;
                    if(keys["Space"] && timer<=0) shoot(); if(timer > 0) timer--;
                    p.x=Math.max(10,Math.min(canvas.width-40,p.x)); p.y=Math.max(10,Math.min(canvas.height-40,p.y));
                    ctx.font=p.size+"px Arial"; ctx.fillText(p.emoji, p.x, p.y);
                    bullets.forEach((b,idx)=>{{ b.x+=b.speed; ctx.beginPath(); ctx.arc(b.x,b.y,5,0,Math.PI*2); ctx.fillStyle="#22c55e"; ctx.fill(); if(b.x>canvas.width)bullets.splice(idx,1); }});
                    if(Math.random()<0.025) enemies.push({{x:canvas.width, y:Math.random()*(canvas.height-50)+10, speed:Math.random()*1.5+2+ {speed_bonus} }});
                    enemies.forEach((e,eIdx)=>{{ e.x-=e.speed; ctx.font="28px Arial"; ctx.fillText("🐀",e.x,e.y);
                        bullets.forEach((b,bIdx)=>{{ if(b.x>e.x && b.x<e.x+30 && b.y>e.y && b.y<e.y+30){{ bullets.splice(bIdx,1); enemies.splice(eIdx,1); score+=10; if(score>=500) finish("win"); }} }});
                        if(e.x<p.x+25 && e.x+25>p.x && e.y<p.y+25 && e.y+25>p.y){{ enemies.splice(eIdx,1); p.hp-=20; if(p.hp<=0) finish("lose"); }}
                        if(e.x<-30) enemies.splice(eIdx,1);
                    }});
