import streamlit as st
import os, json

st.set_page_config(page_title="CatStrike 2D", layout="centered")

# --- СОХРАНЕНИЕ ПРОГРЕССА ---
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

# ШЛЮЗ НАГРАДЫ
if "secure_token" in st.query_params and st.query_params["secure_token"] == "cat_win_777":
    st.session_state.food += 100
    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in st.query_params:
    st.query_params.clear()
    st.session_state.match_playing = False
    st.rerun()

st.sidebar.markdown(f"## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.current_rank.upper()}**")

# --- ИНТЕРФЕЙС ШТАБА И АРЕНЫ ---
if not st.session_state.match_playing:
    st.title("🐾 CatStrike 2D: База")
    
    # Клик по котам меняет текст справа
    c_room, c_desc = st.columns()
    with c_room:
        st.markdown("""
        <style>
            .room { background:#0f172a; border:2px solid #22c55e; border-radius:8px; height:240px; position:relative; }
            .obj { position:absolute; font-size:25px; cursor:pointer; text-decoration:none; }
            .tag { display:block; font-size:10px; color:white; background:rgba(0,0,0,0.6); padding:2px; border-radius:3px; text-align:center; }
        </style>
        <div class="room">
            <a href="?cat=v" target="_self" class="obj" style="bottom:40px; left:100px;">🐱<span class="tag">Вася</span></a>
            <a href="?cat=b" target="_self" class="obj" style="bottom:20px; left:20px;">🐱✨<span class="tag">Буля</span></a>
            <a href="?cat=m" target="_self" class="obj" style="top:90px; left:40px;">🥷<span class="tag">Мурка</span></a>
            <a href="?cat=r" target="_self" class="obj" style="top:30px; right:80px;">🦁<span class="tag">Рыжик</span></a>
            <a href="?cat=t" target="_self" class="obj" style="top:30px; right:20px;">🐯<span class="tag">Томас</span></a>
        </div>
        """, unsafe_allow_html=True)
        
    with c_desc:
        cat = st.query_params.get("cat", "none")
        if cat == "v":
            st.write("🐾 **Вася**: Спит на кресле.")
            if st.button("🥟 Дать пельмень (50 еды)"):
                if st.session_state.food >= 50:
                    st.session_state.food -= 50
                    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
                    st.success("Вася сыто мурчит!")
                else: st.error("Мало еды!")
        elif cat == "b":
            st.write("🐾 **Буля**: Белая и нежная.")
            if st.button("🧼 Погладить"): st.info("Буля громко мурлычет!")
        elif cat == "m": st.warning("🥷 **Мурка**: Царапается и прыгает!")
        elif cat == "r": st.write("🦁 **Рыжик**: Быстрый и опасный.")
        elif cat == "t": st.write("🐯 **Томас**: Друг Рыжика, штурмовик.")
        else: st.info("Кликни кота на базе слева!")

    st.write("---")
    chosen = st.selectbox("Выбери бойца в рейд:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
    if st.button("⚔️ В БОЙ", use_container_width=True):
        st.session_state.match_playing = True
        st.session_state.chosen_hero = chosen
        st.query_params.clear()
        st.rerun()

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
                if(Math.random()<0.025) enemies.push({{x:canvas.width, y:Math.random()*(canvas.height-50)+10, speed:Math.random()*1.5+2+{speed_bonus}}});
                enemies.forEach((e,eIdx)=>{{ e.x-=e.speed; ctx.font="28px Arial"; ctx.fillText("🐀",e.x,e.y);
                    bullets.forEach((b,bIdx)=>{{ if(b.x>e.x && b.x<e.x+30 && b.y>e.y && b.y<e.y+30){{ bullets.splice(bIdx,1); enemies.splice(eIdx,1); score+=10; if(score>=500) finish("win"); }} }});
                    if(e.x<p.x+25 && e.x+25>p.x && e.y<p.y+25 && e.y+25>p.y){{ enemies.splice(eIdx,1); p.hp-=20; if(p.hp<=0) finish("lose"); }}
                    if(e.x<-30) enemies.splice(eIdx,1);
                }});
                ctx.fillStyle="white"; ctx.font="16px Arial"; ctx.fillText(`Кот: ${{p.name}} | ❤️ HP: ${{p.hp}}/${{p.maxHp}} | 🎯 Очки: ${{score}}/500`,15,25);
            }}
            loop();
        </script></body></html>
    """
    st.components.v1.html(game_html, height=420)
