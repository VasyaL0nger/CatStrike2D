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

if 'user' not in st.session_state: st.session_state.user = None
if "play" not in st.session_state: st.session_state.play = False

# ================= 1. БЕЗОПАСНАЯ РЕГИСТРАЦИЯ И ВХОД =================
if not st.session_state.user:
    st.title("CatStrike 2D: Авторизация 🔐")
    m = st.radio("Режим:", ["Войти в штаб", "Создать аккаунт"], horizontal=True)
    u = st.text_input("Логин (английскими буквами):").strip().lower()
    p = st.text_input("Пароль:", type="password").strip()
    db = load_db()
    
    if m == "Создать аккаунт" and st.button("🆕 ЗАРЕГИСТРИРОВАТЬСЯ", use_container_width=True):
        if u and p and u not in db:
            db[u] = {"p": p, "f": 100, "r": "начальный"}
            json.dump(db, open(F, "w"))
            st.success("Аккаунт создан! Теперь выберите режим 'Войти в штаб'.")
        else: st.error("Ошибка! Логин занят или поля пустые.")
    elif m == "Войти в штаб" and st.button("🔓 ВОЙТИ", use_container_width=True):
        if u in db and db[u]["p"] == p:
            st.session_state.user = u
            st.session_state.food, st.session_state.rank = db[u]["f"], db[u]["r"]
            st.rerun()
        else: st.error("Неверный логин или пароль!")
    st.stop()

# --- ЗАГРУЗКА ДАННЫХ ИГРОКА ---
u, db = st.session_state.user, load_db()
RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
idx = list(RANKS.keys()).index(st.session_state.rank)
speed_bonus = idx * 0.4

# Шлюз награды
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
if idx < len(RANKS) - 1 and st.sidebar.button("АПНУТЬ РАНГ"):
    nxt = list(RANKS.keys())[idx + 1]
    if st.session_state.food >= RANKS[nxt]:
        st.session_state.food -= RANKS[nxt]
        st.session_state.rank = nxt
        db[u]["f"], db[u]["r"] = st.session_state.food, nxt
        json.dump(db, open(F, "w"))
        st.rerun()

if st.sidebar.button("🚪 Выйти из профиля"):
    st.session_state.user = None
    st.rerun()

# ================= 2. ИГРОВОЙ ХАБ С КООПЕРАТИВОМ =================
if not st.session_state.play:
    st.title("🐱 CatStrike 2D: Кооперативный режим 🔫")
    st.write("Вы играете вместе на одной клавиатуре!")
    st.write("• **Игрок 1:** Движение — **WASD**, Стрельба — **Пробел**")
    st.write("• **Игрок 2:** Движение — **Стрелочки**, Стрельба — **Enter**")
    
    ch = st.selectbox("Режим матча:", ["Соло матч (Один игрок)", "Кооператив (Два игрока на одном экране)"])
    if st.button("⚔️ ЗАПУСТИТЬ АРЕНУ БОЯ", use_container_width=True):
        st.session_state.play, st.session_state.mode = True, ch
        st.rerun()
else:
    if st.button("↩️ СДАТЬСЯ И ВЕРНУТЬСЯ В ЛОББИ", use_container_width=True):
        st.session_state.play = False
        st.rerun()
        
    is_coop = "true" if st.session_state.mode == "Кооператив (Два игрока на одном экране)" else "false"
    
    game = f"""
    <!DOCTYPE html><html><body style="margin:0;background:#020617;text-align:center;color:white;font-family:Arial;">
    <canvas id="a" width="650" height="340" style="background:#090d16;border:2px solid #22c55e;"></canvas>
    <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
    <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ В МЕНЮ</a>
    <script>
        const canvas=document.getElementById("a"),ctx=canvas.getContext('2d'),jw=document.getElementById("w"),jl=document.getElementById("l");
        let keys={{}}, b=[], en=[], s=0, play=true, t1=0, t2=0;
        
        let p1={{x:50, y:100, h:120, m:120, e:'🐱', active: true}};
        let p2={{x:50, y:200, h:120, m:120, e:'🐯', active: {is_coop}}};
        
        window.addEventListener("keydown",e=>{{keys[e.code]=true;}});
        window.addEventListener("keyup",e=>{{keys[e.code]=false;}});
        
        function finish(r){{play=false;ctx.fillStyle="rgba(0,0,0,0.8)";ctx.fillRect(0,0,650,340);ctx.fillStyle="white";ctx.font="25px Arial";ctx.fillText(r=='win'?"ПОБЕДА КОТОВ!":"КОТЫ ПОВЕРЖЕНЫ",240,165);const url=window.parent.location.origin+window.parent.location.pathname;if(r=='win'){{jw.href=url+"?secure_token=cat_win_777";jw.style.display="block";}}else{{jl.href=url+"?status=l";jl.style.display="block";}}}}
        
        function loop(){{if(!play)return;requestAnimationFrame(loop);ctx.clearRect(0,0,650,340);
            // Управление Игрока 1 (WASD + Пробел)
            if(keys["KeyW"]) p1.y-=4; if(keys["KeyS"]) p1.y+=4; if(keys["KeyA"]) p1.x-=4; if(keys["KeyD"]) p1.x+=4;
            if(keys["Space"] && t1<=0){{ b.push({{x:p1.x+20, y:p1.y+10, c:"#22c55e"}}); t1=10; }} if(t1>0) t1--;
            p1.x=Math.max(0,Math.min(620,p1.x)); p1.y=Math.max(0,Math.min(310,p1.y));
            ctx.font="25px Arial"; ctx.fillText(p1.e, p1.x, p1.y);
            
            // Управление Игрока 2 (Стрелочки + Enter)
            if(p2.active){{
                if(keys["ArrowUp"]) p2.y-=4; if(keys["ArrowDown"]) p2.y+=4; if(keys["ArrowLeft"]) p2.x-=4; if(keys["ArrowRight"]) p2.x+=4;
                if(keys["Enter"] && t2<=0){{ b.push({{x:p2.x+20, y:p2.y+10, c:"#38bdf8"}}); t2=10; }} if(t2>0) t2--;
                p2.x=Math.max(0,Math.min(620,p2.x)); p2.y=Math.max(0,Math.min(310,p2.y));
                ctx.fillText(p2.e, p2.x, p2.y);
            }}
            
            // Пули игроков
            b.forEach((x,i)=>{{x.x+=10; ctx.fillStyle=x.c; ctx.fillRect(x.x,x.y,6,6); if(x.x>650)b.splice(i,1);}});
            
            // Спавн врагов
            if(Math.random()<0.03)en.push({{x:650, y:Math.random()*300+20, s:Math.random()*1.5+2+{speed_bonus}}});
            
            en.forEach((e,i)=>{{e.x-=e.s; ctx.font="20px Arial"; ctx.fillText("🐀",e.x,e.y);
                b.forEach((x,j)=>{{if(x.x>e.x&&x.x<e.x+20&&x.y>e.y-15&&x.y<e.y+15){{b.splice(j,1);en.splice(i,1);s+=10;if(s>=500)finish('win');}}}});
                
                // Укус Игрока 1
                if(e.x<p1.x+20&&e.x+20>p1.x&&e.y>p1.y-20&&e.y<p1.y+20){{ en.splice(i,1); p1.h-=20; }}
                // Укус Игрока 2
                if(p2.active && e.x<p2.x+20&&e.x+20>p2.x&&e.y>p2.y-20&&e.y<p2.y+20){{ en.splice(i,1); p2.h-=20; }}
                
                // Условия поражения
                if(p2.active){{ if(p1.h<=0 && p2.h<=0) finish('lose'); }}
                else {{ if(p1.h<=0) finish('lose'); }}
                
                if(e.x<-20)en.splice(i,1);
            }});
            
            ctx.fillStyle="white"; ctx.font="14px Arial";
            if(p2.active) ctx.fillText(`P1 HP: ${{p1.h>0?p1.h:0}} | P2 HP: ${{p2.h>0?p2.h:0}} | Очки: ${{s}}/500`,10,20);
            else ctx.fillText(`HP: ${{p1.h}}/${{p1.m}} | Очки: ${{s}}/500`,10,20);
        }}loop();
    </script></body></html>
    """
    components.html(game, height=360)
