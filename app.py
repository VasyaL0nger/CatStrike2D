import streamlit as st
import streamlit.components.v1 as components
import os, json

st.set_page_config(page_title="CatStrike 2D", layout="centered")
F = "save_data.json"

# Автоматическая загрузка без паролей
if 'food' not in st.session_state:
    if os.path.exists(F):
        try:
            saved = json.load(open(F, "r"))
            st.session_state.food, st.session_state.rank = saved["f"], saved["r"]
        except: st.session_state.food, st.session_state.rank = 100, "начальный"
    else: st.session_state.food, st.session_state.rank = 100, "начальный"

if "play" not in st.session_state: st.session_state.play = False

RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
idx = list(RANKS.keys()).index(st.session_state.rank)

# Шлюз награды
if "secure_token" in st.query_params:
    st.session_state.food += 100
    json.dump({"f": st.session_state.food, "r": st.session_state.rank}, open(F, "w"))
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in st.query_params:
    st.query_params.clear()
    st.session_state.play = False
    st.rerun()

st.sidebar.markdown(f"## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.rank.upper()}**")
if idx < len(RANKS) - 1 and st.sidebar.button("АПНУТЬ РАНГ"):
    nxt = list(RANKS.keys())[idx + 1]
    if st.session_state.food >= RANKS[nxt]:
        st.session_state.food -= RANKS[nxt]
        st.session_state.rank = nxt
        json.dump({"f": st.session_state.food, "r": nxt}, open(F, "w"))
        st.rerun()

# Экран базы и матча
if not st.session_state.play:
    st.title("🐾 CatStrike 2D: База")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div style="background:#0f172a;border:2px solid #22c55e;border-radius:5px;height:160px;position:relative;">
        <a href="?c=v" target="_self" style="position:absolute;bottom:15px;left:20px;text-decoration:none;font-size:20px;">🐱Вася</a>
        <a href="?c=b" target="_self" style="position:absolute;bottom:15px;right:20px;text-decoration:none;font-size:20px;">🐱✨Буля</a>
        <a href="?c=m" target="_self" style="position:absolute;top:15px;left:20px;text-decoration:none;font-size:20px;">🥷Мурка</a>
        <a href="?c=r" target="_self" style="position:absolute;top:15px;right:20px;text-decoration:none;font-size:20px;">🦁Рыжик</a>
        </div>""", unsafe_allow_html=True)
    with c2:
        c = st.query_params.get("c", "")
        if c == "v" and st.button("🥟 Дать пельмень (50 еды)"):
            if st.session_state.food >= 50:
                st.session_state.food -= 50
                json.dump({"f": st.session_state.food, "r": st.session_state.rank}, open(F, "w"))
                st.success("Вася сыт!")
            else: st.error("Мало еды!")
        elif c == "b" and st.button("🧼 Погладить"): st.info("Буля мурчит!")
        elif c == "m": st.warning("Мурка царапается!")
        elif c == "r": st.write("Рыжик опасен!")
        else: st.write("Кликни кота в комнате!")

    ch = st.selectbox("Боец:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
    if st.button("⚔️ В БОЙ", use_container_width=True):
        st.session_state.play, st.session_state.hero = True, ch
        st.query_params.clear()
        st.rerun()
else:
    if st.button("↩️ В ШТАБ", use_container_width=True):
        st.session_state.play = False
        st.rerun()
    hp = 2000 if st.session_state.hero == "ADMIN" else 120
    cd = 2 if st.session_state.hero == "ADMIN" else 10
    game = f"""
    <!DOCTYPE html><html><body style="margin:0;background:#020617;text-align:center;color:white;font-family:Arial;">
    <canvas id="a" width="650" height="320" style="background:#090d16;border:2px solid #22c55e;"></canvas>
    <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{{window.parent.location.reload();}},500)">🏆 ЗАБРАТЬ НАГРАДУ</a>
    <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ В МЕНЮ</a>
    <script>
        const canvas=document.getElementById("a"),ctx=canvas.getContext("a"?'2d':null),jw=document.getElementById("w"),jl=document.getElementById("l");
        let p={{x:50,y:130,h:{hp},m:{hp},cd:{cd},e:'{st.session_state.hero=='ADMIN' and '👑' or '🐱'}'}},keys={{}},b=[],en=[],s=0,play=true,t=0;
        window.addEventListener("keydown",e=>{{if(play)keys[e.code]=true;}});window.addEventListener("keyup",e=>{{keys[e.code]=false;}});
        canvas.addEventListener("mousedown",()=>{{if(play&&t<=0)shoot();}});
        function shoot() {{ b.push({{x:p.x+20,y:p.y+10}}); t=p.cd; }}
        function finish(r){{play=false;ctx.fillStyle="rgba(0,0,0,0.8)";ctx.fillRect(0,0,650,320);ctx.fillStyle="white";ctx.font="25px Arial";ctx.fillText(r=='win'?"ПОБЕДА":"ПРОИГРЫШ",260,150);const url=window.parent.location.origin+window.parent.location.pathname;if(r=='win'){{jw.href=url+"?secure_token=cat_win_777";jw.style.display="block";}}else{{jl.href=url+"?status=l";jl.style.display="block";}}}}
        function loop(){{if(!play)return;requestAnimationFrame(loop);ctx.clearRect(0,0,650,320);
            if(keys["KeyW"]||keys["ArrowUp"]) p.y-=4;if(keys["KeyS"]||keys["ArrowDown"]) p.y+=4;if(keys["KeyA"]||keys["ArrowLeft"]) p.x-=4;if(keys["KeyD"]||keys["ArrowRight"]) p.x+=4;
            if(keys["Space"]&&t<=0)shoot();if(t>0)t--;p.x=Math.max(0,Math.min(620,p.x));p.y=Math.max(0,Math.min(290,p.y));ctx.font="25px Arial";ctx.fillText(p.e,p.x,p.y);
            b.forEach((x,i)=>{{x.x+=10;ctx.fillStyle="#22c55e";ctx.fillRect(x.x,x.y,5,5);if(x.x>650)b.splice(i,1);}});
            if(Math.random()<0.03)en.push({{x:650,y:Math.random()*280,s:Math.random()*1.5+2+{idx*0.4}}});
            en.forEach((e,i)=>{{e.x-=e.s;ctx.font="20px Arial";ctx.fillText("🐀",e.x,e.y);b.forEach((x,j)=>{{if(x.x>e.x&&x.x<e.x+20&&x.y>e.y&&x.y<e.y+20){{b.splice(j,1);en.splice(i,1);s+=10;if(s>=500)finish('win');}}}});if(e.x<p.x+20&&e.x+20>p.x&&e.y<p.y+20&&e.y+20>p.y){{en.splice(i,1);p.h-=20;if(p.h<=0)finish('lose');}}if(e.x<-20)en.splice(i,1);}});
            ctx.fillStyle="white"; ctx.font="14px Arial"; ctx.fillText(`HP: ${{p.h}}/${{p.m}} | Очки: ${{s}}/500`,10,20);
        }}loop();
    </script></body></html>
    """
    components.html(game, height=360)
