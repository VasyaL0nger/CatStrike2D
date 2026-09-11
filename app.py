import streamlit as st
import streamlit.components.v1 as components
import os, json

st.set_page_config(page_title="CatStrike 2D", layout="centered")
F = "db_users.json"

def load_db():
    if os.path.exists(F):
        try: return json.load(open(F, "r"))
        except: pass
    return {}

if "user" not in st.session_state: st.session_state.user = None
if "play" not in st.session_state: st.session_state.play = False

# --- АВТОРИЗАЦИЯ ПРИ СТАРТЕ ---
if not st.session_state.user:
    st.title("CatStrike 2D 🔐")
    m = st.radio("Режим:", ["Войти", "Регистрация"], horizontal=True)
    u = st.text_input("Логин:").strip().lower()
    p = st.text_input("Пароль:", type="password").strip()
    db = load_db()
    if m == "Регистрация" and st.button("🆕 СОЗДАТЬ АККАУНТ", use_container_width=True):
        if u and p and u not in db:
            db[u] = {"p": p, "f": 100, "r": "начальный"}
            json.dump(db, open(F, "w"))
            st.success("УСПЕХ! ТЕПЕРЬ ВЫБЕРИТЕ 'ВОЙТИ'.")
        else: st.error("ОШИБКА!")
    elif m == "Войти" and st.button("🔓 ВОЙТИ В ИГРУ", use_container_width=True):
        if u in db and db[u]["p"] == p:
            st.session_state.user = u
            st.session_state.food, st.session_state.rank = db[u]["f"], db[u]["r"]
            st.rerun()
        else: st.error("ОШИБКА АВТОРИЗАЦИИ!")
    st.stop()

u, db = st.session_state.user, load_db()
RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
idx = list(RANKS.keys()).index(st.session_state.rank)
sb = idx * 0.4 # Бонус сложности от ранга

# ШЛЮЗ НАГРАДЫ
if "secure_token" in st.query_params:
    db[u]["f"] += 100
    json.dump(db, open(F, "w"))
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in st.query_params:
    st.query_params.clear()
    st.session_state.play = False
    st.rerun()

st.sidebar.markdown(f"👤 Аккаунт: **{u.upper()}**\n## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.rank.upper()}**")
if idx < len(RANKS) - 1 and st.sidebar.button(f"🎖️ АПНУТЬ РАНГ ЗА {RANKS[list(RANKS.keys())[idx+1]]}"):
    next_r = list(RANKS.keys())[idx+1]
    if st.session_state.food >= RANKS[next_r]:
        st.session_state.food -= RANKS[next_r]
        st.session_state.rank = nxt_r
        db[u]["f"], db[u]["r"] = st.session_state.food, next_r
        json.dump(db, open(F, "w"))
        st.rerun()

if st.sidebar.button("🚪 Выйти"):
    st.session_state.user = None
    st.rerun()

# --- МЕНЮ ВЫБОРА РЕЖИМА И КОТА ---
if not st.session_state.play:
    st.title("🌐 Игровое меню CatStrike 2D")
    chosen_hero = st.selectbox("Выбери своего боевого кота:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
    role = st.radio("Режим игры:", ["🏃 Одиночный матч (Соло)", "🔵 Игрок 1 (Хост комнаты)", "🟡 Игрок 2 (Подключиться к другу)"], horizontal=True)
    room_id = st.text_input("ID Секретной Комнаты (для сети):", "cat777")

    if st.button("🚀 ЗАПУСТИТЬ АРЕНУ", use_container_width=True):
        st.session_state.play = True
        st.session_state.room = room_id
        st.session_state.role = role
        st.session_state.hero = chosen_hero
        st.rerun()
else:
    if st.button("↩️ ВЕРНУТЬСЯ В МЕНЮ", use_container_width=True):
        st.session_state.play = False
        st.rerun()

    is_solo = "true" if "Одиночный" in st.session_state.role else "false"
    p_num = "2" if "Игрок 2" in st.session_state.role else "1"
    hp = 2000 if st.session_state.hero == "ADMIN" else 120
    cd = 2 if st.session_state.hero == "ADMIN" else 12
    skin = "👑" if st.session_state.hero == "ADMIN" else "🐱"

    game = f"""
    <!DOCTYPE html><html><body style="margin:0;background:#020617;text-align:center;color:white;font-family:Arial;">
    <canvas id="a" width="650" height="340" style="background:#090d16;border:2px solid #22c55e;"></canvas>
    <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
    <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ</a>
    <script>
        const canvas=document.getElementById("a"),ctx=canvas.getContext('2d'),jw=document.getElementById("w"),jl=document.getElementById("l");
        let keys={{}}, b=[], en=[], s=0, play=true, t=0, solo={is_solo}, myId={p_num};
        let p1={{x:50,y:150,h:{hp},m:{hp},cd:{cd},e:'{skin}',name:'{st.session_state.hero}'}};
        let p2={{x:50,y:230,h:120,m:120,e:'🐯',active:!solo}};
        window.addEventListener("keydown",e=>{{keys[e.code]=true;}});window.addEventListener("keyup",e=>{{keys[e.code]=false;}});
        
        canvas.addEventListener("mousedown",()=>{{ if(play && t<=0) shoot(); }});
        function shoot() {{ 
            b.push({{x:(solo || myId==1?p1.x:p2.x)+20, y:(solo || myId==1?p1.y:p2.y)+10, id:solo?1:myId}}); 
            t = (solo || myId==1) ? p1.cd : 12; 
        }}
        
        function finish(r){{play=false;ctx.fillStyle="rgba(0,0,0,0.8)";ctx.fillRect(0,0,650,340);ctx.fillStyle="white";ctx.font="25px Arial";ctx.fillText("МАТЧ ОКОНЧЕН",240,165);const url=window.parent.location.origin+window.parent.location.pathname;if(r=='win'){{jw.href=url+"?secure_token=cat_win_777";jw.style.display="block";}}else{{jl.href=url+"?status=l";jl.style.display="block";}}}}
        function networkSync() {{
            if(solo) return;
            if(myId == 1) {{ if(Math.random()<0.1) p2.y += (Math.random() > 0.5 ? 15 : -15); }} 
            else {{ if(Math.random()<0.05) p1.y += (Math.random() > 0.5 ? 15 : -15); }}
            p2.y = Math.max(10, Math.min(300, p2.y)); p1.y = Math.max(10, Math.min(300, p1.y));
        }}
        function loopScene() {{ if(!play)return; requestAnimationFrame(loopScene); ctx.clearRect(0,0,650,340);
            if(t>0) t--;
            if(solo || myId == 1){{
                if(keys["KeyW"]||keys["ArrowUp"]) p1.y-=4; if(keys["KeyS"]||keys["ArrowDown"]) p1.y+=4;
                if(keys["KeyA"]||keys["ArrowLeft"]) p1.x-=4; if(keys["KeyD"]||keys["ArrowRight"]) p1.x+=4;
                if(keys["Space"] && t<=0) shoot();
                p1.x=Math.max(0,Math.min(620,p1.x)); p1.y=Math.max(0,Math.min(310,p1.y));
            }}
            if(!solo && myId == 2){{
                if(keys["KeyW"]||keys["ArrowUp"]) p2.y-=4; if(keys["KeyS"]||keys["ArrowDown"]) p2.y+=4;
                if(keys["KeyA"]||keys["ArrowLeft"]) p2.x-=4; if(keys["KeyD"]||keys["ArrowRight"]) p2.x+=4;
                if(keys["Space"] && t<=0) shoot();
                p2.x=Math.max(0,Math.min(620,p2.x)); p2.y=Math.max(0,Math.min(310,p2.y));
            }}
            networkSync(); ctx.font="25px Arial";
            if(p1.h>0) ctx.fillText(p1.e, p1.x, p1.y);
            if(p2.active && p2.h>0) ctx.fillText(p2.e, p2.x, p2.y);
            b.forEach((x,i)=>{{x.x+=10; ctx.fillStyle=x.id==1?"#22c55e":"#38bdf8"; ctx.fillRect(x.x,x.y,6,6); if(x.x>650)b.splice(i,1);}});
            
            // ИСПРАВЛЕНО: Спавн крыс теперь считывает переменную сложности {sb}
            if(Math.random()<0.025)en.push({{x:650, y:Math.random()*280+20, s:Math.random()*1.5+2+{sb}}});
            
            en.forEach((e,i)=>{{e.x-=e.s; ctx.font="20px Arial"; ctx.fillText("🐀",e.x,e.y);
                b.forEach((x,j)=>{{if(x.x>e.x&&x.x<e.x+20&&x.y>e.y-15&&x.y<e.y+15){{b.splice(j,1);en.splice(i,1);s+=10;if(s>=500)finish('win');}}}});
                if(e.x<p1.x+20&&e.x+20>p1.x&&e.y>p1.y-20&&e.y<p1.y+20){{ en.splice(i,1); p1.h-=20; }}
                if(p2.active && e.x<p2.x+20&&e.x+20>p2.x&&e.y>p2.y-20&&e.y<p2.y+20){{ en.splice(i,1); p2.h-=20; }}
                if(p2.active) {{ if(p1.h<=0 && p2.h<=0) finish('lose'); }} else {{ if(p1.h<=0) finish('lose'); }}
                if(e.x<-20)en.splice(i,1);
            }});
            ctx.fillStyle="white"; ctx.font="14px Arial";
            if(solo) ctx.fillText(`Кот: ${{p1.name}} | ❤️ HP: ${{p1.h}} | 🎯 Очки: ${{s}}/500`,10,20);
            else ctx.fillText(`Сеть | ${{myId==1?'🐱 P1':'🐯 P2'}} | Комната: ${{st.session_state.room}} | Очки: ${{s}}/500`,10,20);
        }}requestAnimationFrame(loopScene);
    </script></body></html>
    """
    components.html(game, height=360)
