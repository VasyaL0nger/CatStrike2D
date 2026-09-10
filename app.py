import streamlit as st
import streamlit.components.v1 as components
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
    st.session_state.food, st.session_state.current_rank = saved["food"], saved["current_rank"]
    st.session_state.save_init = True

RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
rank_list = list(RANKS.keys())
current_idx = rank_list.index(st.session_state.current_rank)
speed_bonus = current_idx * 0.4

# Боковая панель
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

tab_g, tab_p = st.tabs(["🎮 Арена Боя", "👤 Профиль"])

with tab_g:
    # ИСПРАВЛЕНО: Безопасное и полное удаление параметра из адресной строки браузера
    if "end_match" in st.query_params:
        st.session_state.food += 100
        json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
        del st.query_params["end_match"] # Удаляем хвостик из ссылки навсегда
        st.success("Матч окончен! Начислено 🍖 100 еды!")
        st.rerun()

    game_html = f"""
    <!DOCTYPE html><html><head><style>
        body {{ margin:0; background:#020617; color:white; text-align:center; font-family:Arial; }}
        canvas {{ background:#090d16; border:3px solid #22c55e; border-radius:8px; display:none; margin:5px auto; }}
        .box {{ max-width:450px; margin:10px auto; background:#0f172a; padding:15px; border-radius:12px; border:2px solid #22c55e; }}
        .btn {{ background:#1e293b; color:white; border:1px solid #475569; padding:10px; margin:4px; border-radius:6px; cursor:pointer; width:95%; }}
        .btn:hover {{ background:#16a34a; }}
    </style></head><body>
        <div id="menu" class="box">
            <h3>ВЫБЕРИТЕ КОТА (Бонус скорости врагов: +{speed_bonus:.1f}):</h3>
            <button class="btn" onclick="start('Vasya','🐱',3.5,150)">🐱 Vasya (150 HP)</button>
            <button class="btn" onclick="start('Bulya','🐱',4,100)">🐱 Bulya (100 HP)</button>
            <button class="btn" onclick="start('Murka','🐱',4.5,110)">🐱 Murka (110 HP)</button>
            <button class="btn" onclick="start('Rizyk','🐱',6,90)">🐱 Rizyk (90 HP)</button>
            <button class="btn" onclick="start('Tomas','🐱',5,120)">🐱 Tomas (120 HP)</button>
        </div>
        <canvas id="arena" width="650" height="350"></canvas>
        <script>
            const canvas = document.getElementById("arena"), ctx = canvas.getContext("2d");
            let p = {{x:100, y:160, size:30, emoji:'🐱', speed:4, hp:100, maxHp:100, name:''}}, keys={{}}, bullets=[], enemies=[], score=0, isPlay=false, isEnd=false;
            
            function start(n,e,s,h) {{ 
                document.getElementById("menu").style.display="none"; 
                canvas.style.display="block"; 
                p.name=n; p.emoji=e; p.speed=s; p.hp=h; p.maxHp=h; 
                isPlay=true; 
                loop(); 
            }}
            
            window.addEventListener("keydown",(e)=>{{keys[e.code]=true; if(e.code==="Space")shoot();}});
            window.addEventListener("keyup",(e)=>{{keys[e.code]=false;}});
            canvas.addEventListener("mousedown",shoot);
            
            function shoot() {{ if(isPlay) bullets.push({{x:p.x+15, y:p.y+8, speed:10}}); }}
            
            function finish() {{ 
                if(isEnd) return; 
                isEnd=true; 
                isPlay=false; 
                ctx.fillStyle="rgba(0,0,0,0.8)"; 
                ctx.fillRect(0,0,canvas.width,canvas.height); 
                ctx.fillStyle="white"; 
                ctx.font="30px Arial"; 
                ctx.fillText("МАТЧ ЗАВЕРШЕН",200,180); 
                setTimeout(()=>{{window.parent.location.search="?end_match=1";}},500); 
            }}
            
            function loop() {{ 
                if(!isPlay) return; 
                requestAnimationFrame(loop); 
                ctx.clearRect(0,0,canvas.width,canvas.height);
                
                if(keys["KeyW"]||keys["ArrowUp"]) p.y-=p.speed; 
                if(keys["KeyS"]||keys["ArrowDown"]) p.y+=p.speed; 
                if(keys["KeyA"]||keys["ArrowLeft"]) p.x-=p.speed; 
                if(keys["KeyD"]||keys["ArrowRight"]) p.x+=p.speed;
                
                p.x=Math.max(10,Math.min(canvas.width-40,p.x)); 
                p.y=Math.max(10,Math.min(canvas.height-40,p.y));
                
                ctx.font=p.size+"px Arial"; 
                ctx.fillText(p.emoji,p.x,p.y);
                
                bullets.forEach((b,idx)=>{{ b.x+=b.speed; ctx.beginPath(); ctx.arc(b.x,b.y,5,0,Math.PI*2); ctx.fillStyle="#22c55e"; ctx.fill(); if(b.x>canvas.width)bullets.splice(idx,1); }});
                
                if(Math.random()<0.025) enemies.push({{x:canvas.width, y:Math.random()*(canvas.height-50)+10, speed:Math.random()*1.5+2+{speed_bonus}}});
                
                enemies.forEach((e,eIdx)=>{{ 
                    e.x-=e.speed; 
                    ctx.font="28px Arial"; 
                    ctx.fillText("🐀",e.x,e.y);
                    
                    bullets.forEach((b,bIdx)=>{{ 
                        if(b.x>e.x && b.x<e.x+30 && b.y>e.y && b.y<e.y+30){{ 
                            bullets.splice(bIdx,1); 
                            enemies.splice(eIdx,1); 
                            score+=10; 
                            if(score>=500) finish(); 
                        }} 
                    }});
                    
                    if(e.x<p.x+25 && e.x+25>p.x && e.y<p.y+25 && e.y+25>p.y){{ 
                        enemies.splice(eIdx,1); 
                        p.hp-=20; 
                        if(p.hp <= 0) finish(); 
                    }}
                    if(e.x<-30) enemies.splice(eIdx,1);
                }});
                
                ctx.fillStyle="white"; 
                ctx.font="16px Arial"; 
                ctx.fillText(`Кот: ${{p.name}} | ❤️ HP: ${{p.hp}}/${{p.maxHp}} | 🎯 Очки: ${{score}}/500`,15,25);
            }}
        </script></body></html>
    """
    components.html(game_html, height=400)

with tab_p:
    st.header("👤 Сетка твоих званий")
    for r_n, r_c in RANKS.items():
        is_curr = " (Текущий)" if st.session_state.current_rank == r_n else ""
        st.write(f"• **{r_n.upper()}** — требуется {r_c} еды {is_curr}")

if st.sidebar.button("🧪 Читы: +5000 еды"):
    st.session_state.food += 5000
    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
    st.rerun()

