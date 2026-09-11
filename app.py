import streamlit as st
import streamlit.components.v1 as components
import os, json, time, random

st.set_page_config(page_title="CatStrike 2D & Grader", layout="centered")
F = "db_users.json"

def load_db():
    if os.path.exists(F):
        try: return json.load(open(F, "r"))
        except: pass
    return {}

if "user" not in st.session_state: st.session_state.user = None
if "play" not in st.session_state: st.session_state.play = False
if "mobile_controls" not in st.session_state: st.session_state.mobile_controls = False
if "last_login" not in st.session_state: st.session_state.last_login = 0.0
if "dropped_item" not in st.session_state: st.session_state.dropped_item = None

# ЗАЩИТА 12 ЧАСОВ: Автовыход
if st.session_state.user and st.session_state.last_login > 0:
    if time.time() - st.session_state.last_login > 43200:
        st.session_state.user = None
        st.sidebar.warning("⏱️ Сессия устарела. Войдите заново!")
        st.rerun()

# ЦЕННОСТЬ ПРЕДМЕТОВ ДЛЯ РАСЧЕТА ШАНСА В АПГРЕЙДЕРЕ
SKINS_PRICE = {
    "ножик": 10, "меч 'сакура'": 30, "меч коллекции 'ангел'": 60, "меч коллекции 'вася'": 100,
    "щит коллекции 'вася'": 20, "щит коллекции 'ангел'": 50, "щит имени були": 80,
    "броня 'пещерные обноски'": 15, "броня коллекции 'ангел'": 45, "броня коллекции 'вася'": 75, "броня принца": 120,
    "пистолет 'дракон'": 25, "пистолет коллекции 'вася'": 55, "пистолет коллекции 'ангел'": 90,
    "автомат 'градиент'": 40, "автомат коллекции 'вася'": 70, "автомат коллекции 'ангел'": 110, "автомат 'леденец'": 150,
    "ракетница 'дружба'": 50, "ракетница коллекции 'вася'": 85, "ракетница коллекции 'ангел'": 130, "ракетница 'одесские традиции'": 200,
    "дрон 'томаса'": 35, "дрон коллекции 'вася'": 65, "дрон коллекции 'ангел'": 105, "дрон 'БПЛА'": 160,
    "кинжал 'молния'": 30, "кинжал коллекции 'вася'": 60, "кинжал коллекции 'ангел'": 95,
    "когти рыжика": 45, "когти коллекции 'вася'": 75, "когти коллекции 'ангел'": 115, "когти пантеры": 180
}

def get_weapon_type(skin_name):
    if "меч" in skin_name or skin_name == "ножик": return "меч"
    if "щит" in skin_name: return "щит"
    if "броня" in skin_name: return "броня"
    if "пистолет" in skin_name: return "пистолет"
    if "автомат" in skin_name: return "автомат"
    if "ракетница" in skin_name: return "ракетница"
    if "дрон" in skin_name: return "дрон"
    if "кинжал" in skin_name: return "кинжал"
    return "когти"

# Полный пул оружия для дропа
WEAPONS_POOL = {
    "меч": ["ножик", "меч 'сакура'", "меч коллекции 'ангел'", "меч коллекции 'вася'"],
    "щит": ["щит коллекции 'вася'", "щит коллекции 'ангел'", "щит имени були"],
    "броня": ["броня 'пещерные обноски'", "броня коллекции 'ангел'", "броня коллекции 'вася'", "броня принца"],
    "пистолет": ["пистолет 'дракон'", "пистолет коллекции 'вася'", "пистолет коллекции 'ангел'"],
    "автомат": ["автомат 'градиент'", "автомат коллекции 'вася'", "автомат коллекции 'ангел'", "автомат 'леденец'"],
    "ракетница": ["ракетница 'дружба'", "ракетница коллекции 'вася'", "ракетница коллекции 'ангел'", "ракетница 'одесские традиции'"],
    "дрон": ["дрон 'томаса'", "дрон коллекции 'вася'", "дрон коллекции 'ангел'", "дрон 'БПЛА'"],
    "кинжал": ["кинжал 'молния'", "кинжал коллекции 'вася'", "кинжал коллекции 'ангел'"],
    "когти": ["когти рыжика", "когти коллекции 'вася'", "когти коллекции 'ангел'", "когти пантеры"]
}

# --- АВТОРИЗАЦИЯ ---
if not st.session_state.user:
    st.title("CatStrike 2D & Grader 🔐")
    m = st.radio("Режим:", ["Войти", "Регистрация"], horizontal=True)
    u = st.text_input("Логин:").strip().lower()
    p = st.text_input("Пароль:", type="password").strip()
    db = load_db()
    if m == "Регистрация" and st.button("🆕 СОЗДАТЬ АККАУНТ", use_container_width=True):
        if u and p and u not in db:
            db[u] = {"p": p, "f": 100, "r": "начальный", "inv": [
                {"w": "меч", "s": "ножик", "q": "Поношенное"},
                {"w": "пистолет", "s": "пистолет коллекции 'вася'", "q": "Поношенное"}
            ]}
            json.dump(db, open(F, "w"))
            st.success("УСПЕХ! ТЕПЕРЬ ВЫБЕРИТЕ 'ВОЙТИ'.")
        else: st.error("ОШИБКА!")
    elif m == "Войти" and st.button("🔓 ВОЙТИ В ШТАБ", use_container_width=True):
        if u in db and db[u]["p"] == p:
            st.session_state.user = u
            st.session_state.food, st.session_state.rank = db[u]["f"], db[u]["r"]
            st.session_state.last_login = time.time()
            st.rerun()
        else: st.error("ОШИБКА АВТОРИЗАЦИИ!")
    st.stop()

st.session_state.last_login = time.time()
u, db = st.session_state.user, load_db()
RANKS = {"начальный":0, "котенок":5000, "кот":10000, "питомец":15000, "любимец":20000, "томас":25000, "рыжик":30000, "буля":35000, "мурка":40000, "вася":50000}
idx = list(RANKS.keys()).index(st.session_state.rank)
sb_speed = idx * 0.4

if "secure_token" in st.query_params and st.query_params["secure_token"] == "cat_win_777":
    db[u]["f"] += 100
    rand_w = random.choice(list(WEAPONS_POOL.keys()))
    rand_s = random.choice(WEAPONS_POOL[rand_w])
    new_drop = {"w": rand_w, "s": rand_s, "q": "После полевых испытаний"}
    if "inv" not in db[u]: db[u]["inv"] = []
    db[u]["inv"].append(new_drop)
    json.dump(db, open(F, "w"))
    st.session_state.dropped_item = f"🎁 {rand_w.upper()} | {rand_s}"
    st.query_params.clear()
    st.html("<script>window.close();</script>")
    st.stop()
elif "status" in st.query_params:
    st.query_params.clear()
    st.session_state.play = False
    st.rerun()
st.sidebar.markdown(f"👤 Профиль: **{u.upper()}**\n## 🍖 Еда: `{st.session_state.food}`\n## 🎖️ Ранг: **{st.session_state.rank.upper()}**")
st.sidebar.write("---")
st.sidebar.subheader("⚙️ Настройки игры")
st.session_state.mobile_controls = st.sidebar.checkbox("📱 Сенсорный Джойстик", value=st.session_state.mobile_controls)

if idx < len(RANKS) - 1 and st.sidebar.button(f"🎖️ АПНУТЬ РАНГ ЗА {RANKS[list(RANKS.keys())[idx+1]]}"):
    next_r = list(RANKS.keys())[idx+1]
    if st.session_state.food >= RANKS[next_r]:
        st.session_state.food -= RANKS[next_r]
        st.session_state.rank = next_r
        db[u]["f"], db[u]["r"] = st.session_state.food, next_r
        json.dump(db, open(F, "w"))
        st.rerun()

if st.sidebar.button("🚪 Выйти"):
    st.session_state.user = None
    st.rerun()

# --- СЕТКА ВКЛАДОК (АРЕНА + ВАСЯГРЕЙДЕР CS2) ---
tab_arena, tab_grader = st.tabs(["🎮 Арена Боя", "🛠️ Верстак Василия"])

# ================= НАСТОЯЩАЯ СИСТЕМА UPGRADER CS2 =================
with tab_grader:
    st.title("🧰 Апгрейдер Скинов CS2 от Василия")
    st.write("Выбери пушку из рюкзака и попытайся улучшить её до ЛЮБОГО желаемого скина!")
    st.session_state.food = db[u]["f"]
    user_inventory = db[u].get("inv", [])

    if not user_inventory:
        st.warning("🎒 Твой рюкзак пуст! Иди на Арену и выбей пушку за победу.")
    else:
        my_item_labels = [f"{item['w'].upper()} | {item['s']} ({item['q']}) — [Ценность: {SKINS_PRICE.get(item['s'], 10)}🎸]" for item in user_inventory]
        st.subheader("1️⃣ Выбери свой предмет для обмена:")
        my_chosen_idx = st.selectbox("Твой скин:", range(len(user_inventory)), format_func=lambda x: my_item_labels[x], key="my_skin_sel")
        my_item = user_inventory[my_chosen_idx]
        my_price = SKINS_PRICE.get(my_item["s"], 10)

        st.write("---")

        all_available_skins = list(SKINS_PRICE.keys())
        all_skin_labels = [f"{get_weapon_type(sk).upper()} | {sk} — [Ценность: {SKINS_PRICE[sk]}🎸]" for sk in all_available_skins]
        st.subheader("2️⃣ Выбери скин-цель, который хочешь получить:")
        target_chosen_idx = st.selectbox("Желаемый скин:", range(len(all_available_skins)), format_func=lambda x: all_skin_labels[x], key="target_skin_sel")
        target_skin_name = all_available_skins[target_chosen_idx]
        target_price = SKINS_PRICE[target_skin_name]

        st.write("---")

        raw_chance = (my_price / target_price) * 100
        final_chance = min(95.0, max(1.0, round(raw_chance, 1)))
        st.subheader("🔨 Верстак Апгрейда")
        st.markdown(f"• Твой вклад: **{my_item['s']}** ({my_price} 🎸)")
        st.markdown(f"• Цель контракта: **{target_skin_name}** ({target_price} 🎸)")
        st.markdown(f"• Стоимость попытки: **🍖 50 еды**")
        
        if final_chance > 70: st.success(f"🎯 Шанс на успех: **{final_chance}%** (Очень высокий!)")
        elif final_chance > 35: st.info(f"🎯 Шанс на успех: **{final_chance}%** (Хороший шанс)")
        else: st.warning(f"🎯 Шанс на успех: **{final_chance}%** (Рискованно!)")

        if st.button("🔥 ЗАПУСТИТЬ КОЛЕСО АПГРЕЙДА CS2", use_container_width=True):
            if st.session_state.food >= 50:
                st.session_state.food -= 50
                db[u]["f"] = st.session_state.food
                roll = random.uniform(0.0, 100.0)
                if roll <= final_chance:
                    new_weapon_type = get_weapon_type(target_skin_name)
                    db[u]["inv"][my_chosen_idx] = {"w": new_weapon_type, "s": target_skin_name, "q": "Прямо с завода"}
                    json.dump(db, open(F, "w"))
                    st.balloons()
                    st.success(f"🏆 КОНТРАКТ СРАБОТАЛ! Василий скрафтил тебе: **{target_skin_name.upper()} (Прямо с завода)**!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    burned_item_name = my_item["s"]
                    db[u]["inv"].pop(my_chosen_idx)
                    json.dump(db, open(F, "w"))
                    st.error(f"💀 АПГРЕЙД СОРВАЛСЯ! Твой скин **{burned_item_name}** сгорел в пламени горна...")
                    time.sleep(1.5)
                    st.rerun()
            else:
                st.error("Не хватает еды для оплаты работы Василия! Нужно минимум 🍖 50 еды.")

# ================= ВКЛАДКА ИГРЫ (ВЫБОР 2 СЛОТОВ) =================
with tab_arena:
    if st.session_state.dropped_item:
        st.balloons()
        st.success(f"🎉 ПОБЕДА! Тебе начислено +100 еды и выпал новый дроп:\n### **{st.session_state.dropped_item}**")
        if st.button("👍 Положить в рюкзак и продолжить"):
            st.session_state.dropped_item = None
            st.rerun()

    if not st.session_state.play:
        st.title(" Меню CatStrike 2D")
        ch = st.selectbox("Выбери кота:", ["Vasya", "Bulya", "Murka", "Rizyk", "Tomas", "ADMIN"])
        r = st.radio("Режим:", ["Соло", "Хост P1", "Клиент P2"], horizontal=True)
        rm = st.text_input("ID Комнаты:", "cat777")
        
        # --- СИСТЕМА ВЫБОРА ДВУХ СЛОТОВ ОРУЖИЯ ---
        st.write("---")
        st.subheader("🎒 Снаряжение отряда (Выбери максимум 2 оружия в бой):")
        user_inventory = db[u].get("inv", [])
            # ИСПРАВЛЕНО: Создаем вечную память для выбранных пушек, чтобы они не стирались при перезагрузке сайта
        if "chosen_slots" not in st.session_state:
            st.session_state.chosen_slots = ["стандарт"]

        st.write("---")
        st.subheader("🎒 Снаряжение отряда (Выбери максимум 2 оружия в бой):")
        user_inventory = db[u].get("inv", [])
        
        current_selection = []
        if not user_inventory:
            st.info("У тебя нет оружия, пойдёшь со стандартными лапками!")
        else:
            for i_idx, item in enumerate(user_inventory):
                is_selected = st.checkbox(f"🔘 {item['w'].upper()} | {item['s']}", key=f"equip_{i_idx}")
                if is_selected:
                    current_selection.append(item["w"])
        
        # Записываем выбор в память сессии
        if current_selection:
            st.session_state.chosen_slots = current_selection
        else:
            st.session_state.chosen_slots = ["стандарт"]

        if len(st.session_state.chosen_slots) > 2:
            st.error("🚨 Кошачьи карманы не бездонные! Нельзя взять больше 2 пушек за раз.")
            combat_ready = False
        else:
            combat_ready = True

        if st.button("⚔ НАЧАТЬ МАТЧ НА АРЕНЕ", use_container_width=True, disabled=not combat_ready):
            st.session_state.play, st.session_state.room, st.session_state.role, st.session_state.hero = True, rm, r, ch
            # Фиксируем пушки намертво перед отправкой на арену
            st.session_state.slot1 = st.session_state.chosen_slots
            st.rerun()
        if len(selected_weapons) > 2:
            st.error("🚨 Кошачьи карманы не бездонные! Нельзя взять больше 2 пушек за раз.")
            combat_ready = False
        elif len(selected_weapons) == 0:
            selected_weapons = ["стандарт"]
            combat_ready = True
        else:
            combat_ready = True

        if st.button("⚔ НАЧАТЬ МАТЧ НА АРЕНЕ", use_container_width=True, disabled=not combat_ready):
            st.session_state.play, st.session_state.room, st.session_state.role, st.session_state.hero = True, rm, r, ch
            st.session_state.slot1 = selected_weapons[0]
            st.session_state.slot2 = selected_weapons[1] if len(selected_weapons) > 1 else "none"
            st.rerun()
    else:
        if st.button(" В МЕНЮ", use_container_width=True):
            st.session_state.play = False
            st.rerun()
            
        is_solo = "true" if "Соло" in st.session_state.role else "false"
        p_num = "2" if "P2" in st.session_state.role else "1"
        hp = 2000 if st.session_state.hero == "ADMIN" else 120
        cd = 2 if st.session_state.hero == "ADMIN" else 15
        sk = "👑" if st.session_state.hero == "ADMIN" else "🐱"
        show_mobile = "true" if st.session_state.mobile_controls else "false"
        r_n = str(st.session_state.get('room', 'cat777'))
        
        # Передаем массив выбранного оружия в JS
        equipped_list = st.session_state.get('slot1', ["стандарт"])
        w_list_json = json.dumps(equipped_list)

        game = """
        <!DOCTYPE html><html><head><style>
            body { margin:0; background:#020617; text-align:center; color:white; font-family:Arial; user-select:none; touch-action:none; }
            canvas { background:#090d16; border:2px solid #22c55e; border-radius:8px; margin:5px auto; display:block; touch-action:none; }
            .link { display:none; color:#22c55e; font-size:20px; text-decoration:none; }
        </style></head><body>
            <canvas id="a" width="650" height="340"></canvas>
            <a id="w" style="display:none;color:#22c55e;font-size:20px;text-decoration:none;" href="" target="_blank" onclick="setTimeout(()=>{window.parent.location.reload();},500)">🏆 ЗАБРАТЬ +100 ЕДЫ</a>
            <a id="l" style="display:none;color:#ef4444;font-size:20px;text-decoration:none;" href="" target="_parent">❌ ВЫЙТИ</a>
            <script>
                const canvas=document.getElementById("a"),ctx=canvas.getContext('2d'),jw=document.getElementById("w"),jl=document.getElementById("l");
                let keys={}, b=[], en=[], s=0, play=true, t=0, dTimer=0;
                
                let solo = """ + is_solo + """; let myId = """ + p_num + """; let mOn = """ + show_mobile + """; let sb = """ + str(sb_speed) + """;
                let p1={x:50, y:150, h:""" + str(hp) + """, m:""" + str(hp) + """, cd:""" + str(cd) + """, e:'""" + sk + """', name:'""" + str(st.session_state.hero) + """'};
                let p2={x:50, y:230, h:120, m:120, e:'🐯', active:!solo}, joystickActive=false, joyCenter={x:100,y:240}, joyStick={x:100,y:240}, joyRadius=50, stickRadius=20, moveX=0, moveY=0, jId=null;

                // СИСТЕМА ДВУХ СЛОТОВ И ПЕРЕКЛЮЧЕНИЯ
                let myWeapons = """ + w_list_json + """;
                let currentWIdx = 0;
                let curW = myWeapons[currentWIdx]; // Текущее активное оружие
                let shootCount = 0; // Для подсчета комбо каждого 2-го, 5-го или 10-го выстрела

                window.addEventListener("keydown",e=>{ 
                    if(play){ 
                        if(e.code==='Space'&&!keys['Space']&&t<=0){shoot();} 
                        if(e.code==='KeyQ') { switchWeapon(); } // Смена оружия на Q
                        keys[e.code]=true; 
                    } 
                });
                window.addEventListener("keyup",e=>{keys[e.code]=false;});
                canvas.addEventListener("mousedown",(e)=>{ 
                    if(play && t<=0 && !mOn) shoot(); 
                });
                
                function switchWeapon() {
                    if(myWeapons.length <= 1) return;
                    currentWIdx = (currentWIdx + 1) % myWeapons.length;
                    curW = myWeapons[currentWIdx];
                }
                
                if(mOn) {
                    canvas.addEventListener("touchstart",e=>{ 
                        e.preventDefault(); 
                        for(let i=0;i<e.changedTouches.length;i++){ 
                            let tObj=e.changedTouches[i], r=canvas.getBoundingClientRect(), tx=tObj.clientX-r.left, ty=tObj.clientY-r.top; 
                            if(tx<canvas.width/2&&!joystickActive){ 
                                // Верхний левый угол на мобилках тоже меняет оружие
                                if(ty < 60) { switchWeapon(); }
                                else { joystickActive=true; jId=tObj.identifier; joyCenter.x=tx; joyCenter.y=ty; joyStick.x=tx; joyStick.y=ty; }
                            } else if(tx>=canvas.width/2&&t<=0&&play){shoot();} 
                        } 
                    });
                    canvas.addEventListener("touchmove",e=>{ e.preventDefault(); if(!joystickActive)return; for(let i=0; i<e.touches.length; i++){ let tObj=e.touches[i]; if(tObj.identifier===jId){ let r=canvas.getBoundingClientRect(), tx=tObj.clientX-r.left, ty=tObj.clientY-r.top, dx=tx-joyCenter.x, dy=ty-joyCenter.y, dist=Math.sqrt(dx*dx+dy*dy); if(dist<joyRadius){ joyStick.x=tx; joyStick.y=ty; } else { joyStick.x=joyCenter.x+(dx/dist)*joyRadius; joyStick.y=joyCenter.y+(dy/dist)*joyRadius; } moveX=(joyStick.x-joyCenter.x)/joyRadius; moveY=(joyStick.y-joyCenter.y)/joyRadius; } } });
                    canvas.addEventListener("touchend",e=>{ e.preventDefault(); for(let i=0;i<e.changedTouches.length;i++){ if(e.changedTouches[i].identifier===jId){ joystickActive=false; jId=null; moveX=0; moveY=0; } } });
                    canvas.addEventListener("touchcancel",()=>{ joystickActive=false; jId=null; moveX=0; moveY=0; });
                }

                function shoot() { 
                    let bx=p1.x+20, by=p1.y+10, bid=1; 
                    if(!solo&&myId==2){ bx=p2.x+20; by=p2.y+10; bid=2; } 
                    
                    shootCount++;
                    
                    // ЛОГИКА ТВОИХ УНИКАЛЬНЫХ МЕХАНИК СТРЕЛЬБЫ
                    if(curW === "пистолет") {
                        b.push({x:bx, y:by, id:bid, type:"normal"});
                        if(shootCount % 2 === 0) { b.push({x:bx+15, y:by-5, id:bid, type:"normal"}); } // +1 пуля
                    } 
                    else if(curW === "автомат") {
                        b.push({x:bx, y:by, id:bid, type:"normal"});
                        if(shootCount % 2 === 0) {
                            b.push({x:bx+10, y:by-15, id:bid, type:"normal", vy:-1.5}); // Веер пуль
                            b.push({x:bx+10, y:by+15, id:bid, type:"normal", vy:1.5});
                            b.push({x:bx+15, y:by, id:bid, type:"normal"});
                        }
                    } 
                    else if(curW === "ракетница") {
                        if(shootCount % 5 === 0) {
                            b.push({x:bx, y:by, id:bid, type:"rocket", target:null}); // Самонаводящаяся
                        } else {
                            b.push({x:bx, y:by, id:bid, type:"normal"});
                        }
                    } 
                    else if(curW === "кинжал") {
                        if(shootCount % 10 === 0) {
                            b.push({x:bx, y:by, id:bid, type:"dagger", vy:-2, ric:2}); // Рикошетные ножи
                            b.push({x:bx, y:by, id:bid, type:"dagger", vy:0, ric:2});
                            b.push({x:bx, y:by, id:bid, type:"dagger", vy:2, ric:2});
                        } else {
                            b.push({x:bx, y:by, id:bid, type:"normal"});
                        }
                    }
                    else if(curW === "меч" || curW === "когти") {
                        // Ближний бой бьет невидимой короткой волной
                        b.push({x:bx, y:by, id:bid, type:"melee", range:60});
                    }
                    else {
                        b.push({x:bx, y:by, id:bid, type:"normal"});
                    }
                    
                    t=(solo||myId==1)?p1.cd:15; 
                }

                function finish(r){ play=false; ctx.fillStyle="rgba(0,0,0,0.8)"; ctx.fillRect(0,0,650,340); ctx.fillStyle="white"; ctx.font="25px Arial"; ctx.fillText("МАТЧ ОКОНЧЕН",240,165); const url=window.parent.location.origin+window.parent.location.pathname; if(r=='win'){ jw.href=url+"?secure_token=cat_win_777"; jw.style.display="block"; } else { jl.href=url+"?status=l"; jl.style.display="block"; } }
                function networkSync() { if(solo)return; if(myId==1){ if(Math.random()<0.1) p2.y+=(Math.random()>0.5?15:-15); } else { if(Math.random()<0.05) p1.y+=(Math.random()>0.5?15:-15); } p2.y=Math.max(10,Math.min(300,p2.y)); p1.y=Math.max(10,Math.min(300,p1.y)); }
                function drawJoystick() { if(!mOn||!joystickActive)return; ctx.beginPath(); ctx.arc(joyCenter.x,joyCenter.y,joyRadius,0,Math.PI*2); ctx.fillStyle="rgba(255,255,255,0.15)"; ctx.fill(); ctx.strokeStyle="rgba(34,197,94,0.5)"; ctx.lineWidth=2; ctx.stroke(); ctx.beginPath(); ctx.arc(joyStick.x,joyStick.y,stickRadius,0,Math.PI*2); ctx.fillStyle="rgba(34,197,94,0.7)"; ctx.fill(); }
                
                function loopScene() { if(!play)return; requestAnimationFrame(loopScene); ctx.clearRect(0,0,650,340); if(t>0)t--;
                    if(solo||myId==1){ if(mOn&&joystickActive){ p1.x+=moveX*4; p1.y+=moveY*4; } else { if(keys["KeyW"]||keys["ArrowUp"])p1.y-=4; if(keys["KeyS"]||keys["ArrowDown"])p1.y+=4; if(keys["KeyA"]||keys["ArrowLeft"])p1.x-=4; if(keys["KeyD"]||keys["ArrowRight"])p1.x+=4; } p1.x=Math.max(0,Math.min(620,p1.x)); p1.y=Math.max(0,Math.min(310,p1.y)); }
                    if(!solo&&myId==2){ if(mOn&&joystickActive){ p2.x+=moveX*4; p2.y+=moveY*4; } else { if(keys["KeyW"]||keys["ArrowUp"])p2.y-=4; if(keys["KeyS"]||keys["ArrowDown"])p2.y+=4; if(keys["KeyA"]||keys["ArrowLeft"])p2.x-=4; if(keys["KeyD"]||keys["ArrowRight"])p2.x+=4; } p2.x=Math.max(0,Math.min(620,p2.x)); p2.y=Math.max(0,Math.min(310,p2.y)); }
                    networkSync(); ctx.font="25px Arial"; if(p1.h>0)ctx.fillText(p1.e,p1.x,p1.y); if(p2.active&&p2.h>0)ctx.fillText(p2.e,p2.x,p2.y); drawJoystick();
                    
                    // МЕХАНИКА ДРОНОВ: авто-атака каждые 5 сек
                    if(curW === "дрон") {
                        dTimer++;
                        if(dTimer > 300 && en.length > 0) {
                            dTimer = 0;
                            let targetEnemy = en[0];
                            b.push({x:p1.x, y:p1.y, id:1, type:"drone_bot", tx:targetEnemy.x, ty:targetEnemy.y});
                        }
                    }

                    // Обработка летящих снарядов
                    b.forEach((x,i)=>{ 
                        if(x.vy) x.y += x.vy;
                        
                        // Поведение самонаводящейся ракеты одесских традиций
                        if(x.type === "rocket") {
                            if(en.length > 0) {
                                let target = en[0];
                                if(target.y > x.y) x.y += 2; if(target.y < x.y) x.y -= 2;
                            }
                            x.x += 6;
                            ctx.font="20px Arial"; ctx.fillText("🚀", x.x, x.y);
                        } 
                        // Поведение дрона-камикадзе
                        else if(x.type === "drone_bot") {
                            let dx = x.tx - x.x, dy = x.ty - x.y, dist = Math.sqrt(dx*dx + dy*dy);
                            if(dist > 5) { x.x += (dx/dist)*5; x.y += (dy/dist)*5; }
                            ctx.font="18px Arial"; ctx.fillText("🛸", x.x, x.y);
                        }
                        // Поведение кинжала (рикошет от пола и потолка)
                        else if(x.type === "dagger") {
                            x.x += 12;
                            if((x.y < 10 || x.y > 330) && x.ric > 0) { x.vy = -x.vy; x.ric--; }
                            ctx.fillStyle = "#ef4444"; ctx.fillRect(x.x, x.y, 8, 4);
                        }
                        // Обычные пули лазера
                        else if(x.type === "normal") {
                            x.x+=10; ctx.fillStyle=x.id==1?"#22c55e":"#38bdf8"; ctx.fillRect(x.x,x.y,6,6); 
                        }
                        // Визуализация меча/когтей
                        else if(x.type === "melee") {
                            x.x += 15;
                            ctx.strokeStyle = "rgba(239, 68, 68, 0.4)"; ctx.lineWidth = 4;
                            ctx.beginPath(); ctx.arc(x.x, x.y, 20, 0, Math.PI*2); ctx.stroke();
                            if(x.x > p1.x + x.range) b.splice(i,1);
                        }

                        if(x.x>650 || x.x < -50) b.splice(i,1); 
                    });

                    if(Math.random()<0.025) en.push({x:650, y:Math.random()*280+20, s:Math.random()*1.5+2+sb, hp:100});
                    
                    en.forEach((e,i)=>{ e.x-=e.s; ctx.font="20px Arial"; ctx.fillText("🐀",e.x,e.y); 
                        b.forEach((x,j)=>{
                            let hit = false;
                            if(x.type === "melee" && x.x>e.x-25 && x.x<e.x+25 && x.y>e.y-25 && x.y<e.y+25) hit = true;
                            if(x.type !== "melee" && x.x>e.x && x.x<e.x+20 && x.y>e.y-15 && x.y<e.y+15) hit = true;
                            
                            if(hit){
                                b.splice(j,1);
                                if(x.type === "dagger") { en.splice(i,1); s+=10; }
                                else if(x.type === "rocket" || x.type === "drone_bot") {
                                    en.splice(i,1); s+=10;
                                    ctx.fillStyle = "rgba(239, 68, 68, 0.5)"; ctx.beginPath(); ctx.arc(e.x, e.y, 60, 0, Math.PI*2); ctx.fill();
                                    for(let k=0; k<2; k++) { if(en[k]) { en.splice(k,1); s+=10; } }
                                }
                                else { en.splice(i,1); s+=10; }
                                if(s>=500)finish('win');
                            }
                        }); 
                        
                        if(e.x<p1.x+20&&e.x+20>p1.x&&e.y>p1.y-20&&e.y<p1.y+20){
                            en.splice(i,1); 
                            let dmg = 20; let takeDmg = true;
                            if(curW === "броня") dmg = 15;
                            if(curW === "щит" && Math.random() < 0.20) takeDmg = false;
                            if(curW === "когти" && Math.random() < 0.50) takeDmg = false;
                            if(takeDmg) p1.h -= dmg;
                            if(curW === "меч" || curW === "когти") { s += 10; if(s>=500) finish('win'); }
                        } 
                        if(p2.active&&e.x<p2.x+20&&e.x+20>p2.x&&e.y>p2.y-20&&e.y<p2.y+20){en.splice(i,1);p2.h-=20;} 
                        if(p2.active){ if(p1.h<=0&&p2.h<=0)finish('lose'); } else { if(p1.h<=0)finish('lose'); } 
                        if(e.x<-20)en.splice(i,1); 
                    });
                    
                    ctx.fillStyle="white"; ctx.font="14px Arial"; 
                    ctx.fillText("Пушка: " + curW.toUpperCase() + " | ❤️ HP: " + (p1.h>0?p1.h:0) + " | 🎯 Очки: " + s + "/500", 10, 20);
                }requestAnimationFrame(loopScene);
            </script></body></html>
        """
        components.html(game, height=360)

