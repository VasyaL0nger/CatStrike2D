import streamlit as st
import streamlit.components.v1 as components
import os, json

st.set_page_config(page_title="CatStrike 2D", layout="centered")

# --- СИСТЕМА НАДЁЖНОГО СОХРАНЕНИЯ ПРОГРЕССА ---
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

if 'match_playing' not in st.session_state: st.session_state.match_playing = False

RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
rank_list = list(RANKS.keys())
current_idx = rank_list.index(st.session_state.current_rank)
speed_bonus = current_idx * 0.4

# ПРОВЕРКА НАГРАДЫ: Принимаем данные через легальный шлюз ссылок
query_params = st.query_params
if "status" in query_params:
    status = query_params["status"]
    if status == "win":
        st.session_state.food += 100
        json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
        st.success("🏆 ПОБЕДА! Начислено 100 еды!")
        st.balloons()
    elif status == "lose":
        st.error("Вы проиграли. Попробуйте еще раз!")
    
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

tab_g, tab_p = st.tabs(["资料 Арена Боя", "👤 Профиль"])

with tab_g:
    if not st.session_state.match_playing:
        st.subheader("Сбор кошачьего отряда")
        chosen_cat = st.selectbox("Выбери бойца:", ["ADMIN", "Vasya", "Bulya", "Murka", "Rizyk", "Tomas"])
        if st.button("⚔️ НАЧАТЬ МАТЧ НА АРЕНЕ", use_container_width=True):
            st.session_state.match_playing = True
            st.session_state.chosen_hero = chosen_cat
            st.rerun()
    else:
        if st.button("↩️ ПОКИНУТЬ МАТЧ (ВЕРНУТЬСЯ В ЛОББИ)", use_container_width=True):
            st.session_state.match_playing = False
            st.rerun()

        st.write("---")
        hp_val = 2000 if st.session_state.chosen_hero == "ADMIN" else 120
        cd_val = 2 if st.session_state.chosen_hero == "ADMIN" else 10

        game_html = f"""
        <!DOCTYPE html><html><head><style>
            body {{ margin:0; background:#020617; color:white; text-align:center; font-family:Arial; user-select:none; }}
            canvas {{ background:#090d16; border:3px solid #22c55e; border-radius:8px; margin:5px auto; }}
            .claim-link {{ display:none; background:#22c55e; color:black; font-weight:bold; padding:12px; border-radius:6px; text-decoration:none; width:90%; max-width:450px; margin:10px auto; font-size:16px; }}
            .claim-link:hover {{ background:#16a34a; }}
        </style></head><body>
            
            <canvas id="arena" width="650" height="350"></canvas>
            
            <!-- ИСПРАВЛЕНО: Кнопки теперь являются чистыми HTML-ссылками с флагом target="_parent" -->
            <a id="jsClaim" class="claim-link" href="" target="_parent">🏆 ЗАБРАТЬ НАГРАДУ (+100 ЕДЫ)</a>
            <a id="jsLose" class="claim-link" style="background:#ef4444; color:white;" href="" target="_parent">❌ ВЫЙТИ В МЕНЮ</a>

            <script>
                const canvas = document.getElementById("arena"), ctx = canvas.getContext("2d");
                const jsClaim = document.getElementById("jsClaim"), jsLose = document.getElementById("jsLose");
                
                let p = {{x:100, y:160, size:30, emoji:'🐱', speed:4, hp:{hp_val}, maxHp:{hp_val}, name:'{st.session_state.chosen_hero}', shootCooldown:{cd_val}}};
                let keys={{}}, bullets=[], enemies=[], score=0, isPlay=true, cooldownTimer=0;
                let speedBonus = {speed_bonus}; 
                if(p.name === 'ADMIN') p.emoji = '👑';
                
                window.addEventListener("keydown",(e)=>{{ if(isPlay) keys[e.code]=true; }});
                window.addEventListener("keyup",(e)=>{{ keys[e.code] = false; }});
                canvas.addEventListener("mousedown",()=>{{ if(isPlay && cooldownTimer<=0) shoot(); }});
                function shoot() {{ bullets.push({{x:p.x+15, y:p.y+8, speed:12}}); cooldownTimer = p.shootCooldown; }}
                
                function finish(result) {{ 
                    if(!isPlay) return; isPlay = false; 
                    ctx.fillStyle="rgba(15, 23, 42, 0.9)"; ctx.fillRect(0,0,canvas.width,canvas.height); 
                    ctx.fillStyle = result === "win" ? "#22c55e" : "#ef4444";
                    ctx.font="bold 30px Arial"; ctx.textAlign="center";
                    ctx.fillText(result === "win" ? "МАТЧ ЗАВЕРШЕН (ПОБЕДА!)" : "ВЫ ПОГИБЛИ", canvas.width/2, 160); 
                    
                    // Генерируем железные прямые ссылки для клика наружу
                    const base_url = window.parent.location.origin + window.parent.location.pathname;
                    if(result === "win") {{
                        jsClaim.href = base_url + "?status=win";
                        jsClaim.style.display = "block";
                    }} else {{
                        jsLose.href = base_url + "?status=lose";
                        jsLose.style.display = "block";
                    }}
                }}
                
                function loop() {{ 
                    if(!isPlay) return; requestAnimationFrame(loop); ctx.clearRect(0,0,canvas.width,canvas.height);
                    if(keys["KeyW"]||keys["ArrowUp"]) p.y-=p.speed; if(keys["KeyS"]||keys["ArrowDown"]) p.y+=p.speed; if(keys["KeyA"]||keys["ArrowLeft"]) p.x-=p.speed; if(keys["KeyD"]||keys["ArrowRight"]) p.x+=p.speed;
                    if(keys["Space"] && cooldownTimer<=0) shoot(); if(cooldownTimer > 0) cooldownTimer--;
                    p.x=Math.max(10,Math.min(canvas.width-40,p.x)); p.y=Math.max(10,Math.min(canvas.height-40,p.y));
                    ctx.font=p.size+"px Arial"; ctx.textAlign="left"; ctx.fillText(p.emoji, p.x, p.y);
                    bullets.forEach((b,idx)=>{{ b.x+=b.speed; ctx.beginPath(); ctx.arc(b.x,b.y,5,0,Math.PI*2); ctx.fillStyle="#22c55e"; ctx.fill(); if(b.x>canvas.width)bullets.splice(idx,1); }});
                    if(Math.random()<0.025) enemies.push({{x:canvas.width, y:Math.random()*(canvas.height-50)+10, speed:Math.random()*1.5+2+speedBonus}});
                    enemies.forEach((e,eIdx)=>{{ 
                        e.x-=e.speed; ctx.font="28px Arial"; ctx.fillText("🐀",e.x,e.y);
                        bullets.forEach((b,bIdx)=>{{ 
                            if(b.x>e.x && b.x<e.x+30 && b.y>e.y && b.y<e.y+30){{ bullets.splice(bIdx,1); enemies.splice(eIdx,1); score+=10; if(score>=500) finish("win"); }} 
                        }});
                        if(e.x<p.x+25 && e.x+25>p.x && e.y<p.y+25 && e.y+25>p.y){{ enemies.splice(eIdx,1); p.hp-=20; if(p.hp <= 0) finish("lose"); }}
                        if(e.x<-30) enemies.splice(eIdx,1);
                    }});
                    ctx.fillStyle="white"; ctx.font="16px Arial"; ctx.textAlign="left";
                    ctx.fillText(`Кот: ${{p.name}} | ❤️ HP: ${{p.hp}}/${{p.maxHp}} | 🎯 Очки: ${{score}}/500`,15,25);
                }}
                loop();
            </script></body></html>
        """
        components.html(game_html, height=420)

with tab_p:
    st.header("👤 Сетка твоих званий")
    for r_n, r_c in RANKS.items():
        is_curr = " (Текущий)" if st.session_state.current_rank == r_n else ""
        st.write(f"• **{r_n.upper()}** — требуется {r_c} еды {is_curr}")

if st.sidebar.button("🧪 Читы: +5000 еды"):
    st.session_state.food += 5000
    json.dump({"food": st.session_state.food, "current_rank": st.session_state.current_rank}, open(SAVE_FILE, "w"))
    st.rerun()
