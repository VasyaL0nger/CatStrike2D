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
if "mobile_controls" not in st.session_state: st.session_state.mobile_controls = False

# --- 1. АВТОРИЗАЦИЯ ---
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
speed_bonus = idx * 0.4

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

# --- БОКОВАЯ ПАНЕЛЬ ---
st.sidebar.markdown(f"👤 Профиль: **{u.upper()}**\n## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.rank.upper()}**")
st.sidebar.write("---")
st.sidebar.subheader("⚙️ Настройки игры")
st.session_state.mobile_controls = st.sidebar.checkbox("📱 Сенсорный Джойстик", value=st.session_state.mobile_controls)

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

# --- ИГРОВОЙ ХАБ ---
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
    cd = 2 if st.session_state.hero == "ADMIN" else 15
    skin = "👑" if st.session_state.hero == "ADMIN" else "🐱"
    show_mobile = "true" if st.session_state.mobile_controls else "false"

    game = f"""
    <!DOCTYPE html><html><head><style>
        body {{ margin:0; background:#020617; text-align:center; color:white; font-family:Arial; user-select:none; touch-action:none; }}
        canvas {{ background:#090d16; border:2px solid #22c55e; border-radius:8px; margin:5px auto; display:block; touch-action:none; }}
        .link {{ display:none; color:#22c55e; font-size:20px; text-decoration:none; }}
    </style></head><body>
        <canvas id="a" width="650" height="340"></canvas>

        <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
        <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ</a>
        
        <script>
            const canvas=document.getElementById("a"),ctx=canvas.getContext('2d'),jw=document.getElementById("w"),jl=document.getElementById("l");
            let keys={{}}, b=[], en=[], s=0, play=true, t=0, solo={is_solo}, myId={p_num}, mOn={show_mobile};
            let p1={{x:50,y:150,h:{hp},m:{hp},cd:{cd},e:'{skin}',name:'{st.session_state.hero}'}};
            let p2={{x:50,y:230,h:120,m:120,e:'🐯',active:!solo}};
            
            let joystickActive = false;
            let joyCenter = {{x: 100, y: 240}}, joyStick = {{x: 100, y: 240}}, joyRadius = 50, stickRadius = 20;
            let moveX = 0, moveY = 0;

            window.addEventListener("keydown",e=>{{ if(play){{ if(e.code==="Space"&&!keys["Space"]&&t<=0){{shoot();}} keys[e.code]=true; }} }});
            window.addEventListener("keyup",e=>{{keys[e.code]=false;}});
            canvas.addEventListener("mousedown",()=>{{ if(play && t<=0 && !mOn) shoot(); }});
            
            if(mOn) {{
                canvas.addEventListener("touchstart", (e) => {{
                    e.preventDefault();
                    for(let i=0; i<e.touches.length; i++) {{
                        let tObj = e.touches[i], rect = canvas.getBoundingClientRect();
                        let tx = tObj.clientX - rect.left, ty = tObj.clientY - rect.top;
                        
                        if (tx < canvas.width / 2) {{
                            joystickActive = true; joyCenter.x = tx; joyCenter.y = ty;
                            joyStick.x = tx; joyStick.y = ty;
                        }} else if (tx >= canvas.width / 2 && t <= 0 && play) {{
                            shoot();
                        }}
                    }}
                }});

                canvas.addEventListener("touchmove", (e) => {{
                    e.preventDefault(); if (!joystickActive) return;
                    for(let i=0; i<e.touches.length; i++) {{
                        let tObj = e.touches[i], rect = canvas.getBoundingClientRect();
                        let tx = tObj.clientX - rect.left, ty = tObj.clientY - rect.top;
                        
                        if (tx < canvas.width / 2 + 50) {{
                            let dx = tx - joyCenter.x, dy = ty - joyCenter.y, dist = Math.sqrt(dx*dx + dy*dy);
                            if (dist < joyRadius) {{ joyStick.x = tx; joyStick.y = ty; }} 
                            else {{ joyStick.x = joyCenter.x + (dx / dist) * joyRadius; joyStick.y = joyCenter.y + (dy / dist) * joyRadius; }}
                            moveX = (joyStick.x - joyCenter.x) / joyRadius; moveY = (joyStick.y - joyCenter.y) / joyRadius;
                        }}
                    }}
                }});

                canvas.addEventListener("touchend", (e) => {{
                    e.preventDefault(); let leftTouch = false;
                    for(let i=0; i<e.touches.length; i++) {{
                        let rect = canvas.getBoundingClientRect();
                        if (e.touches[i].clientX - rect.left < canvas.width / 2) leftTouch = true;
                    }}
                    if (!leftTouch) {{ joystickActive = false; moveX = 0; moveY = 0; }}
                }});
            }}

            function shoot() {{ 
                let bx = p1.x + 20;
                let by = p1.y + 10;
                let bid = 1;
                
                if (!solo && myId == 2) {{
                    bx = p2.x + 20;
                    by = p2.y + 10;
                    bid = 2;
                }}
                b.push({{x: bx, y: by, id: bid}}); 
                
                if (solo || myId == 1) {{
                    t = p1.cd;
                }} else {{
                    t = 15;
                }}
            }}
            
            function finish(r){{play=false; ctx.fillStyle="rgba(0,0,0,0.8)";ctx.fillRect(0,0,650,340);ctx.fillStyle="white";ctx.font="25px Arial";ctx.fillText("МАТЧ ОКОНЧЕН",240,165);const url=window.parent.location.origin+window.parent.location.pathname;if(r=='win'){{jw.href=url+"?secure_token=cat_win_777";jw.style.display="block";}}else{{jl.href=url+"?status=l";jl.style.display="block";}}}}
            
            function networkSync() {{
                if(solo) return;
                if(myId == 1) {{ if(Math.random()<0.1) p2.y += (Math.random() > 0.5 ? 15 : -15); }} 
                else {{ if(Math.random()<0.05) p1.y += (Math.random() > 0.5 ? 15 : -15); }}
                p2.y = Math.max(10, Math.min(300, p2.y)); p1.y = Math.max(10, Math.min(300, p1.y));
            }}
            
            function drawJoystick() {{
                if (!mOn || !joystickActive) return;
                ctx.beginPath(); ctx.arc(joyCenter.x, joyCenter.y, joyRadius, 0, Math.PI*2);
                ctx.fillStyle = "rgba(255, 255, 255, 0.15)"; ctx.fill();
                ctx.strokeStyle = "rgba(34, 197, 94, 0.5)"; ctx.lineWidth = 2; ctx.stroke();
                ctx.beginPath(); ctx.arc(joyStick.x, joyStick.y, stickRadius, 0, Math.PI*2);
                ctx.fillStyle = "rgba(34, 197, 94, 0.7)"; ctx.fill();
            }}

            function loopScene() {{ if(!play)return; requestAnimationFrame(loopScene); ctx.clearRect(0,0,650,340);
                if(t>0) t--;
                
                if(solo || myId == 1){{
                    if (mOn && joystickActive) {{
                        p1.x += moveX * 4; p1.y += moveY * 4;
                    }} else {{
                        if(keys["KeyW"]||keys["ArrowUp"]) p1.y-=4; if(keys["KeyS"]||keys["ArrowDown"]) p1.y+=4;
                        if(keys["KeyA"]||keys["ArrowLeft"]) p1.x-=4; if(keys["KeyD"]||keys["ArrowRight"]) p1.x+=4;
                    }}
                    if(keys["Space"] && t<=0) shoot();
                    p1.x=Math.max(0,Math.min(620,p1.x)); p1.y=Math.max(0,Math.min(310,p1.y));
                }}
                if(!solo && myId == 2){{
                    if (mOn && joystickActive) {{
                        p2.x += moveX * 4; p2.y += moveY * 4;
                    }} else {{
                        if(keys["KeyW"]||keys["ArrowUp"]) p2.y-=4; if(keys["KeyS"]||keys["ArrowDown"]) p2.y+=4;
                        if(keys["KeyA"]||keys["ArrowLeft"]) p2.x-=4; if(keys["KeyD"]||keys["ArrowRight"]) p2.x+=4;
                    }}
                    if(keys["Space"] && t<=0) shoot();
                    p2.x=Math.max(0,Math.min(620,p2.x)); p2.y=Math.max(0,Math.min(310,p2.y));
                }}
                
                networkSync(); ctx.font="25px Arial";
                if(p1.h>0) ctx.fillText(p1.e, p1.x, p1.y);
                if(p2.active && p2.h>0) ctx.fillText(p2.e, p2.x, p2.y);
                
                drawJoystick();
                
                b.forEach((x,i)=>{{
                    x.x+=10; 
                    if(x.id==1) {{ ctx.fillStyle="#22c55e"; }} else {{ ctx.fillStyle="#38bdf8"; }}
                    ctx.fillRect(x.x,x.y,6,6); 
                    if(x.x>650)b.splice(i,1);
                }});
                if(Math.random()<0.025)en.push({{x:650, y:Math.random()*280+20, s:Math.random()*1.5+2+speed_bonus}});
                en.forEach((e,i)=>{{e.x-=e.s; ctx.font="20px Arial"; ctx.fillText("🐀",e.x,e.y);
                    b.forEach((x,j)=>{{if(x.x>e.x&&x.x<e.x+20&&x.y>e.y-15&&x.y<e.y+15){{b.splice(j,1);en.splice(i,1);s+=10;if(s>=500)finish('win');}}}});
                    if(e.x<p1.x+20&&e.x+20>p1.x&&e.y>p1.y-20&&e.y<p1.y+20){{ en.splice(i,1); p1.h-=20; }}
                    if(p2.active && e.x<p2.x+20&&e.x+20>p2.x&&e.y>p2.y-20&&e.y<p2.y+20){{ en.splice(i,1); p2.h-=20; }}
                    
                    if(p2.active) {{ 
                        if(p1.h<=0 && p2.h<=0) finish('lose'); 
                    }} else {{ 
                        if(p1.h<=0) finish('lose'); 
                    }}
                    if(e.x<-20)en.splice(i,1);
                }});
                ctx.fillStyle="white"; ctx.font="14px Arial";
                if(solo) {{
                    ctx.fillText("Кот: " + p1.name + " | ❤️ HP: " + p1.h + " | 🎯 Очки: " + s + "/500", 10, 20);
                }} else {{
                    ctx.fillText("Сеть | Комната: " + "{st.session_state.get('room', 'cat777')}" + " | Очки: " + s + "/500", 10, 20);
                }}
            }}requestAnimationFrame(loopScene);
        </script></body></html>
    """
    components.html(game, height=360)

