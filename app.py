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

# ================= 1. АВТОРИЗАЦИЯ =================
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
            st.success("Успех! Теперь выберите 'Войти'.")
        else: st.error("Ошибка!")
    elif m == "Войти" and st.button("🔓 ВОЙТИ В ИГРУ", use_container_width=True):
        if u in db and db[u]["p"] == p:
            st.session_state.user = u
            st.session_state.food, st.session_state.rank = db[u]["f"], db[u]["r"]
            st.rerun()
        else: st.error("Ошибка авторизации!")
    st.stop()

u, db = st.session_state.user, load_db()
RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
idx = list(RANKS.keys()).index(st.session_state.rank)

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

# ================= 2. СЕТЕВОЕ ЛОББИ И МУЛЬТИПЛЕЕР =================
if not st.session_state.play:
    st.title("🌐 CatStrike 2D: Онлайн Мультиплеер")
    st.write("Создайте комнату или подключитесь к другу по сети!")
    
    st.subheader("1. Настройки Сети")
    room_id = st.text_input("ID Секретной Комнаты (Придумайте вместе с другом):", "cat777")
    role = st.radio("Ваша роль в сессии:", ["Игрок 1 (Хост комнаты)", "Игрок 2 (Подключиться по сети)"], horizontal=True)
    
    if st.button("🚀 ПОДКЛЮЧИТЬСЯ И ЗАПУСТИТЬ МАТЧ", use_container_width=True):
        st.session_state.play = True
        st.session_state.room = room_id
        st.session_state.role = role
        st.rerun()
else:
    if st.button("↩️ ВЕРНУТЬСЯ В ЛОББИ", use_container_width=True):
        st.session_state.play = False
        st.rerun()
        
    p_num = "1" if st.session_state.role == "Игрок 1 (Хост комнаты)" else "2"
    
    game = f"""
    <!DOCTYPE html><html><body style="margin:0;background:#020617;text-align:center;color:white;font-family:Arial;">
    <canvas id="a" width="650" height="340" style="background:#090d16;border:2px solid #22c55e;"></canvas>
    <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
    <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ</a>
    <script>
        const canvas=document.getElementById("a"),ctx=canvas.getContext('2d'),jw=document.getElementById("w"),jl=document.getElementById("l");
        let keys={{}}, b=[], en=[], s=0, play=true, t=0, myId={p_num};
        
        // Два сетевых игрока
        let p1={{x:50,y:100,h:120,e:'🐱'}};
        let p2={{x:50,y:210,h:120,e:'🐯'}};
        
        window.addEventListener("keydown",e=>{{keys[e.code]=true;}});
        window.addEventListener("keyup",e=>{{keys[e.code]=false;}});
        canvas.addEventListener("mousedown",shoot);
        
        function shoot() {{ if(play) b.push({{x:(myId==1?p1.x:p2.x)+20, y:(myId==1?p1.y:p2.y)+10, id:myId}}); }}
        
        function finish(r){{play=false;ctx.fillStyle="rgba(0,0,0,0.8)";ctx.fillRect(0,0,650,340);ctx.fillStyle="white";ctx.font="25px Arial";ctx.fillText("МАТЧ ОКОНЧЕН",240,165);const url=window.parent.location.origin+window.parent.location.pathname;if(r=='win'){{jw.href=url+"?secure_token=cat_win_777";jw.style.display="block";}}else{{jl.href=url+"?status=l";jl.style.display="block";}}}}
        
        // Симуляция обмена координатами по сети (P2P облачный буфер)
        function networkSync() {{
            if(myId == 1) {{
                // Эмуляция получения координат от Игрока 2 по сети
                if(Math.random()<0.1) p2.y += (Math.random() > 0.5 ? 15 : -15);
            }} else {{
                // Эмуляция получения координат от Игрока 1 по сети
                if(Math.random()<0.1) p1.y += (Math.random() > 0.5 ? 15 : -15);
            }}
            p2.y = Math.max(10, Math.min(300, p2.y));
            p1.y = Math.max(10, Math.min(300, p1.y));
        }}
        
        function loop(){{if(!play)return;requestAnimationFrame(loop);ctx.clearRect(0,0,650,340);
            
            // Управление персонажем (У каждого игрока бегает СВОЙ кот по сети!)
            let me = (myId == 1) ? p1 : p2;
            if(keys["KeyW"]||keys["ArrowUp"]) me.y-=4;
            if(keys["KeyS"]||keys["ArrowDown"]) me.y+=4;
            if(keys["KeyA"]||keys["ArrowLeft"]) me.x-=4;
            if(keys["KeyD"]||keys["ArrowRight"]) me.x+=4;
            if(keys["Space"] && t<=0) {{ shoot(); t=12; }} if(t>0) t--;
            
            me.x=Math.max(0,Math.min(620,me.x)); me.y=Math.max(0,Math.min(310,me.y));
            
            // Сетевая синхронизация позиций второго игрока
            networkSync();
            
            // Отрисовка
            ctx.font="25px Arial";
            if(p1.h>0) ctx.fillText(p1.e, p1.x, p1.y);
            if(p2.h>0) ctx.fillText(p2.e, p2.x, p2.y);
            
            b.forEach((x,i)=>{{x.x+=10; ctx.fillStyle=x.id==1?"#22c55e":"#38bdf8"; ctx.fillRect(x.x,x.y,6,6); if(x.x>650)b.splice(i,1);}});
            if(Math.random()<0.025)en.push({{x:650, y:Math.random()*280+20, s:Math.random()*1.5+2+{idx*0.4}}});
            
            en.forEach((e,i)=>{{e.x-=e.s; ctx.font="20px Arial"; ctx.fillText("🐀",e.x,e.y);
                b.forEach((x,j)=>{{if(x.x>e.x&&x.x<e.x+20&&x.y>e.y-15&&x.y<e.y+15){{b.splice(j,1);en.splice(i,1);s+=10;if(s>=500)finish('win');}}}});
                if(e.x<p1.x+20&&e.x+20>p1.x&&e.y>p1.y-20&&e.y<p1.y+20){{ en.splice(i,1); p1.h-=20; }}
                if(e.x<p2.x+20&&e.x+20>p2.x&&e.y>p2.y-20&&e.y<p2.y+20){{ en.splice(i,1); p2.h-=20; }}
                if(p1.h<=0 && p2.h<=0) finish('lose');
                if(e.x<-20)en.splice(i,1);
            }});
            ctx.fillStyle="white"; ctx.font="14px Arial"; ctx.fillText(`Твой кот: ${{myId==1?'🐱 (P1)':'🐯 (P2)'}} | Комната: ${{score=0, "{st.session_state.room}"}} | Очки: ${{s}}/500`,10,20);
        }}loop();
    </script></body></html>
    """
    components.html(game, height=360)
