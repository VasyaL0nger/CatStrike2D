import streamlit as st
import os, json

st.set_page_config(page_title="CatStrike 2D — Лобби", layout="centered")

# --- СИСТЕМА НАДЁЖНОГО СОХРАНЕНИЯ ПРОГРЕССА ---
SAVE_FILE = "save_data.json"
def load_game():
    if os.path.exists(SAVE_FILE):
        try: return json.load(open(SAVE_FILE, "r"))
        except: pass
    return {"food": 100, "current_rank": "начальный"}

if 'save_init' not in st.session_state:
    saved = load_game()
    st.session_state.food, st.session_state.current_rank = saved["food"], saved["current_rank"]
    st.session_state.save_init = True

if 'match_playing' not in st.session_state: st.session_state.match_playing = False

RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
rank_list = list(RANKS.keys())
current_idx = rank_list.index(st.session_state.current_rank)
speed_bonus = current_idx * 0.4

# ШЛЮЗ НАГРАДЫ (Новая вкладка)
query_params = st.query_params
if "secure_token" in query_params and query_params["secure_token"] == "cat_win_777":
    st.session_state.food += 100
    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in query_params and query_params["status"] == "lose":
    st.query_params.clear()
    st.session_state.match_playing = False
    st.rerun()

st.sidebar.markdown(f"## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.current_rank.upper()}**")

if current_idx < len(rank_list) - 1:
    next_r = rank_list[current_idx + 1]
    if st.sidebar.button(f"🎖️ АПНУТЬ РАНГ ЗА {RANKS[next_r]}"):
        if st.session_state.food >= RANKS[next_r]:
            st.session_state.food -= RANKS[next_r]
            st.session_state.current_rank = next_r
            json.dump({"food": st.session_state.food, "current_rank": next_r}, open(SAVE_FILE, "w"))
            st.rerun()
        else: st.sidebar.error("Не хватает еды!")

tab_g, tab_p = st.tabs(["🎮 Штаб Отряда", "👤 Профиль"])

with tab_g:
    if not st.session_state.match_playing:
        st.title("🐾 CatStrike 2D: База Кошачьего Спецназа")
        st.write("Нажмите на любого кота на базе, чтобы взаимодействовать с ним!")
        
        # --- ИНТЕРАКТИВНАЯ КАРТА ШТАБА (КАТ-СПЕЙС) ---
        col_base, col_desc = st.columns([5, 4])
        
        with col_base:
            # HTML5/CSS3 Кастомная комната лобби
            lobby_style = """
            <style>
                .lobby-room { background: #0f172a; border: 3px solid #22c55e; border-radius: 12px; height: 320px; position: relative; overflow: hidden; margin-bottom: 15px; }
                .furniture { position: absolute; font-size: 14px; color: #475569; font-weight: bold; }
                .cat-sticker { position: absolute; font-size: 35px; cursor: pointer; transition: transform 0.2s; user-select: none; }
                .cat-sticker:hover { transform: scale(1.3); }
                .name-tag { display: block; font-size: 11px; color: white; background: rgba(0,0,0,0.6); padding: 2px 4px; border-radius: 4px; text-align: center; margin-top: -5px; }
            </style>
            <div class="lobby-room">
                <!-- Мебель базы -->
                <div class="furniture" style="bottom: 40px; left: 180px; font-size: 40px;">🛏️<span class="name-tag">Кресло</span></div>
                <div class="furniture" style="bottom: 20px; left: 30px; font-size: 35px;">🪵<span class="name-tag">Коврик</span></div>
                <div class="furniture" style="top: 30px; right: 40px; font-size: 35px;">🪟<span class="name-tag">Батарея</span></div>
                
                <!-- Ваши коты-стикеры расставлены по комнате -->
                <a href="?interact=vasya" target="_self" class="cat-sticker" style="bottom: 85px; left: 195px;">🐱<span class="name-tag">Вася</span></a>
                <a href="?interact=bulya" target="_self" class="cat-sticker" style="bottom: 40px; left: 40px;">🐱✨<span class="name-tag">Буля</span></a>
                <a href="?interact=murka" target="_self" class="cat-sticker" style="top: 150px; left: 80px;">🥷<span class="name-tag">Мурка</span></a>
                <a href="?interact=rizyk" target="_self" class="cat-sticker" style="top: 70px; right: 80px;">🦁<span class="name-tag">Рыжик</span></a>
                <a href="?interact=tomas" target="_self" class="cat-sticker" style="top: 70px; right: 35px;">🐯<span class="name-tag">Томас</span></a>
            </div>
            """
            st.markdown(lobby_style, unsafe_allow_html=True)
            
        with col_desc:
            st.markdown("### 📋 Панель взаимодействия")
            interact = st.query_params.get("interact", "none")
            
            if interact == "vasya":
                st.subheader("Кот Василий")
                st.write("Ленивый, харизматичный кошачий король. Сейчас сладко дрыхнет на любимом мягком кресле и видит сны о горе пельменей.")
                if st.button("🥟 Скормить Васе 50 еды"):
                    if st.session_state.food >= 50:
                        st.session_state.food -= 50
                        json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
                        st.success("Василий лениво открыл один глаз, сыто мурлыкнул и съел пельмень!")
                    else: st.error("У вас мало еды!")
            elif interact == "bulya":
                st.subheader("Кошка Буля")
                st.write("Белая, невероятно нежная кошка. Обожает сидеть на теплом коврике и когда её гладят.")
                if st.button("🧼 Погладить Булю"):
                    st.info("Буля зажмурила глаза от удовольствия, тихонько замурчала и потерлась о вашу руку лапкой. Милота!")
            elif interact == "murka":
                st.subheader("Кошка Мурка")
                st.write("Чёрная кошка-ассасин. Любит бешено играться, прыгать по стенам и внезапно царапать людей.")
                st.warning("Мурка злобно посмотрела на вас, выпустила когти и сделала резкий тыгыдык на шкаф!")
            elif interact == "rizyk":
                st.subheader("Кот Rizyk")
                st.write("Ярко-рыжий кот. Очень быстрый и смертельно опасный. Сидит у батареи и начищает свои боевые когти.")
            elif interact == "tomas":
                st.subheader("Кот Tomas")
                st.write("Чёрный полосатый штурмовик. Лучший друг Рыжика. Сидит рядом с ним у тепла и заряжает магазины пулями.")
            else:
                st.info("Кликните по любому коту-стикеру в комнате слева, чтобы поговорить с ним, погладить или покормить!")

        st.write("---")
        chosen_cat = st.selectbox("С каким бойцом вы пойдете в рейд?", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
        if st.button("⚔️ НАЧАТЬ ТАКТИЧЕСКИЙ МАТЧ", use_container_width=True):
            st.session_state.match_playing = True
            st.session_state.chosen_hero = chosen_cat
            st.query_params.clear()
            st.rerun()

    # РЕЖИМ АРЕНЫ
    else:
        if st.button("↩️ СБРОСИТЬ МАТЧ И ВЕРНУТЬСЯ В ШТАБ", use_container_width=True):
            st.session_state.match_playing = False
            st.rerun()

        st.write("---")
        hp_val = 2000 if st.session_state.chosen_hero == "ADMIN" else 120
        cd_val = 2 if st.session_state.chosen_hero == "ADMIN" else 10

        game_html = f"""
        <!DOCTYPE html><html><head><style>
            body {{ margin:0; background:#020617; color:white; text-align:center; font-family:Arial; user-select:none; }}
            canvas {{ background:#090d16; border:3px solid #22c55e; border-radius:8px; margin:5px auto; }}
            .claim-link {{ display:none; background:#22c55e; color:black; font-weight:bold; padding:12px; border-radius:6px; text-decoration:none; width:90%; max-width:450px; margin:10px auto; font-size:16px; display:inline-block; }}
        </style></head><body>
            <canvas id="arena" width="650" height="350"></canvas>
            <a id="jsWin" class="claim-link" href="" target="_blank" onclick="setTimeout(()=>{{ window.parent.location.reload(); }}, 500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
            <a id="jsLose" class="claim-link" style="background:#ef4444; color:white;" href="" target="_parent">❌ ВЫЙТИ В МЕНЮ</a>
            <script>
                const canvas = document.getElementById("arena"), ctx = canvas.getContext("2d");
                const jsWin = document.getElementById("jsWin"), jsLose = document.getElementById("jsLose");
                let p = {{x:100, y:160, size:30, emoji:'🐱', speed:4, hp:{hp_val}, maxHp:{hp_val}, name:'{st.session_state.chosen_hero}', shootCooldown:{cd_val}}};
                let keys={{}}, bullets=[], enemies=[], score=0, isPlay=true, cooldownTimer=0;
                if(p.name === 'ADMIN') p.emoji = '👑';
                window.addEventListener("keydown",(e)=>{{ if(isPlay) keys[e.code]=true; }});
                window.addEventListener("keyup",(e)=>{{ keys[e.code] = false; }});
                canvas.addEventListener("mousedown",()=>{{ if(isPlay && cooldownTimer<=0) shoot(); }});
                function shoot() {{ bullets.push({{x:p.x+15, y:p.y+8, speed:12}}); cooldownTimer = p.shootCooldown; }}
                function finish(result) {{ 
                    if(!isPlay) return; isPlay = false; 
                    ctx.fillStyle="rgba(15, 23, 42, 0.9)"; ctx.fillRect(0,0,canvas.width,canvas.height); 
                    ctx.fillStyle = result === "win" ? "#22c55e" : "#ef4444"; ctx.font="bold 30px Arial"; ctx.textAlign="center";
                    ctx.fillText(result === "win" ? "МАТЧ ЗАВЕРШЕН (ПОБЕДА!)" : "ВЫ ПОГИБЛИ", canvas.width/2, 160); 
                    const base_url = window.parent.location.origin + window.parent.location.pathname;
Используйте код с осторожностью.if(result === "win") {{ jsWin.href = base_url + "?secure_token=cat_win_777"; jsWin.style.display = "block"; }}else {{ jsLose.href = base_url + "?status=lose"; jsLose.style.display = "block"; }}}}function loop() {{if(!isPlay) return; requestAnimationFrame(loop); ctx.clearRect(0,0,canvas.width,canvas.height);if(keys["KeyW"]||keys["ArrowUp"]) p.y-=p.speed; if(keys["KeyS"]||keys["ArrowDown"]) p.y+=p.speed; if(keys["KeyA"]||keys["ArrowLeft"]) p.x-=p.speed; if(keys["KeyD"]||keys["ArrowRight"]) p.x+=p.speed;if(keys["Space"] && cooldownTimer<=0) shoot(); if(cooldownTimer > 0) cooldownTimer--;p.x=Math.max(10,Math.min(canvas.width-40,p.x)); p.y=Math.max(10,Math.min(canvas.height-40,p.y));ctx.font=p.size+"px Arial"; ctx.textAlign="left"; ctx.fillText(p.emoji, p.x, p.y);bullets.forEach((b,idx)=>{{ b.x+=b.speed; ctx.beginPath(); ctx.arc(b.x,b.y,5,0,Math.PI2); ctx.fillStyle="#22c55e"; ctx.fill(); if(b.x>canvas.width)bullets.splice(idx,1); }});if(Math.random()<0.025) enemies.push({{x:canvas.width, y:Math.random()(canvas.height-50)+10, speed:Math.random()*1.5+2+{speed_bonus}}});enemies.forEach((e,eIdx)=>{{e.x-=e.speed; ctx.font="28px Arial"; ctx.fillText("🐀",e.x,e.y);bullets.forEach((b,bIdx)=>{{ if(b.x>e.x && b.x<e.x+30 && b.y>e.y && b.y<e.y+30){{ bullets.splice(bIdx,1); enemies.splice(eIdx,1); score+=10; if(score>=500) finish("win"); }} }});if(e.x<p.x+25 && e.x+25>p.x && e.y<p.y+25 && e.y+25>p.y){{ enemies.splice(eIdx,1); p.hp-=20; if(p.hp<=0) finish("lose"); }}if(e.x<-30) enemies.splice(eIdx,1);}});ctx.fillStyle="white"; ctx.font="16px Arial"; ctx.textAlign="left";ctx.fillText(Кот: ${{p.name}} | ❤️ HP: ${{p.hp}}/${{p.maxHp}} | 🎯 Очки: ${{score}}/500,15,25);}}loop();"""st.components.v1.html(game_html, height=420)with tab_p:st.header("👤 Сетка твоих званий")for r_n, r_c in RANKS.items():is_curr = " (Текущий)" if st.session_state.current_rank == r_n else ""st.write(f"• {r_n.upper()} — требуется {r_c} еды {is_curr}")
