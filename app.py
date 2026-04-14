import streamlit as st

# --- 1. 設定網頁與 PWA Icon ---
APP_EMOJI = "💊"
emoji_codepoint = hex(ord(APP_EMOJI))[2:] 
EMOJI_SVC_URL = f"https://fonts.gstatic.com/s/e/notoemoji/latest/{emoji_codepoint}/512.webp"

st.set_page_config(
    page_title="NICU 給藥計算機", 
    page_icon=APP_EMOJI, 
    layout="centered"
)

st.markdown(f"""
    <head>
    <link rel="icon" sizes="192x192" href="{EMOJI_SVC_URL}">
    <link rel="icon" sizes="512x512" href="{EMOJI_SVC_URL}">
    <link rel="apple-touch-icon" href="{EMOJI_SVC_URL}">
    <meta name="msapplication-TileImage" content="{EMOJI_SVC_URL}">
    </head>
    """, unsafe_allow_html=True)

# --- 2. 自定義 CSS 樣式區 ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF0; }
    label, .label-text, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] li { 
        color: #000000 !important; 
        font-weight: bold !important; 
    }
    [data-testid="stMarkdownContainer"] h1 { font-size: 1.8em !important; }
    label, .label-text { font-size: 1.15em !important; }
    .streamlit-expanderHeader, .streamlit-expanderHeader p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
    }
    .info-box-style { 
        background-color: #FFFFFF; 
        border-left: 6px solid #FFD700; 
        padding: 15px; 
        margin-bottom: 20px; 
        border-radius: 4px; 
        color: #000000; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        font-size: 1.1em;
    }
    .final-volume-text {
        font-size: 2.2em;
        font-weight: 800;
        text-align: center;
        color: #000000;
    }
    .value-box { 
        padding: 12px; 
        background: #ffffff; 
        border-radius: 8px; 
        border: 1px solid #ccc; 
        min-height: 45px; 
        margin-bottom: 20px; 
        font-family: 'Courier New', monospace; 
        font-size: 1.1em; 
        color: #000000; 
    }
    .warning-text { 
        color: #000000; 
        font-weight: bold; 
        font-size: 1.2em; 
        border: 3px solid #FF0000; 
        padding: 15px; 
        border-radius: 8px; 
        background-color: #FFF0F0; 
        text-align: center; 
        margin-bottom: 25px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 Session State ---
if 'dose_input' not in st.session_state:
    st.session_state.dose_input = 0.0
if 'drug_choice' not in st.session_state:
    st.session_state.drug_choice = "-- 請選擇 --"

def clear_fields():
    st.session_state.dose_input = 0.0
    st.session_state.drug_choice = "-- 請選擇 --"

st.markdown("<h1>NICU 給藥計算機</h1>", unsafe_allow_html=True)

# --- 4. 核心資料庫 (已新增 Ceftaroline fosamil) ---
drug_data = {
    "Ceftaroline fosamil (600mg/Vial)": ["1 vail 加入 20mL 注射用水 (1mL=30mg) 配置，取實際dose，稀釋成2.5倍量 (1ml=12mg)，建議用1.5 mL N/S drip 60mins", "20mL 注射用水", "-", "dose/30", "N/S 2.5倍", "-", "-", "F*2.5", "60"],
    "Ampicillin (500mg/Vial)": ["1 vail 加入 5mL 注射用水 (1mL=100mg) 配置，取實際dose給藥，建議用1.5mL N/S drip 30 mins", "5mL 注射用水", "-", "dose/100", "-", "-", "-", "F", "30"],
    "Gentamicin (80mg/2mL/Vial)": ["取實際dose，稀釋成4倍量 (1mL=10mg)給藥，建議用1.5mL N/S drip 60 mins", "-", "dose/40", "-", "N/S 4倍", "-", "-", "D*4", "60"],
    "CeFoTaxiMe (2g/Vial)": ["1vial加入10mL 注射用水 (1mL=200mg)，稀釋成5倍量 (1mL=40mg)，建議用1.5mL N/S drip 30 mins.", "10mL注射用水", "-", "dose/200", "D/W N/S 5倍", "-", "-", "F*5", "30"],
    "Cefazolin (1000mg/vial)": ["1 vail 加入 10mL N/S (1mL=100mg) 配置，建議用1.5mL N/S drip 30 mins", "10mL N/S", "-", "dose/100", "-", "-", "-", "F", "30"],
    "Ceftazidime (2000mg/vial)": ["1 vail 加入 10mL N/S (1mL=170mg)，稀釋成2倍(1 mL= 85mg)，建議用1.5mL N/S drip 60 mins", "10mL N/S", "-", "dose/170", "N/S 2倍", "-", "-", "F*2", "60"],
    "Ceftriaxone (1g/Vial)": ["1 vail 加入 10mL 注射用水 (1mL=100mg) 配置，稀釋成2.5倍量 (1ml=40mg)，建議用1.5 mL N/S drip 60mins", "10mL注射用水", "-", "dose/100", "N/S 2.5倍", "-", "-", "F*2.5", "60"],
    "Cefepime (1000mg/Vial)": ["1 vail 加入 10mL N/S 配置 (1mL=100mg)，建議用1.5 mL N/S drip 30mins.", "10mL N/S", "-", "dose/200", "-", "-", "-", "F", "30"],
    "Oxacillin (500mg/Vial)": ["1 vail 加入 5mL N/S (1mL=100mg)，稀釋成5倍量 (1ml=20mg)，建議用1.5mL N/S drip 60 mins.", "5mL N/S", "-", "dose/100", "N/S 5倍", "-", "-", "F*5", "60"],
    "Amoxicillin 1.0g + Clavulanate 0.2g (1.2g/vial)": ["1vial加入20mL N/S (1mL=60mg A+C)，以N/S稀釋2.5倍 (1ml=24mg A+C)", "20mL N/S", "-", "dose/60", "N/S 2.5倍", "-", "-", "F*2.5", "30"],
    "Ampicillin/Sulbactam (A+S 1.5g/vial)": ["1 vail 加入 3.2 mL N/S (1mL=375mg)，稀釋成10倍量 (1mL=37.5mg)", "3.2mL N/S", "-", "dose/375", "N/S 10倍", "-", "-", "F*10", "30"],
    "Piperacillin + Tazobactam (2.25g/vial)": ["1 vial加入10 mL N/S (1mL=202.5mg), 稀釋成2.5倍量 (1mL=81 mg)", "10mL N/S", "-", "dose/202.5", "N/S 2.5倍", "-", "-", "F*2.5", "30"],
    "Ertapenem 1g/Vial": ["1 vail 加入 10mL 注射用水 (1mL=100mg)，以N/S稀釋成5倍量 (1mL=20mg)", "10mL注射用水", "-", "dose/100", "N/S 5倍", "-", "-", "F*5", "30"],
    "Meropenem (250mg/Vial)": ["1vial加入12.5mL N/S (1mL=20mg)，建議用1.5mL N/S drip 30 mins", "12.5mL N/S", "-", "dose/20", "-", "-", "-", "F", "30/240"],
    "Teicoplanin (200 mg/Vial)": ["1vial加入3mL 注射用水 (1mL=66.66mg)，建議用1.5mL N/S drip 30 mins", "3mL注射用水", "-", "dose/66.66", "-", "-", "-", "F", "30"],
    "Metronidazole (500mg/100mL/bot)": ["不稀釋, IVD 30-60 mins", "-", "dose/5", "-", "-", "-", "-", "D", "30-60"],
    "Colistin (2MU/Vial=66.8mg CBA)": ["1vial加入2mL N/S (1mL=33.4mg)，稀釋成2倍量(1mL=16.7mg)", "2mL N/S", "-", "dose/33.4", "N/S 2倍", "-", "-", "F*2", "30"],
    "Clindamycin 300mg/2mL/Amp": ["取實際dose，稀釋成25倍量 (1mL=6mg)給藥", "-", "dose/150", "-", "N/S 25倍", "-", "-", "D*25", "30"],
    "Fluconazole (100 mg/50 mL/Vial)": ["取實際dose (2mg/mL)，建議用1.5mL N/S drip 60 mins", "-", "dose/2", "-", "-", "-", "-", "D", "60"],
    "Amphotericin B (50mg/Vial)": ["1vial加入10mL 注射用水(1mL=5mg)，以D5W稀釋成50倍量 (1ml=0.1mg)", "10mL注射用水", "-", "dose/5", "D5W 50倍", "-", "-", "F*50", "120-360"],
    "Liposomal Amphotericin B 50 mg/Vial": ["1 vial 加入 12 mL 注射用水 (1ml=4mg)，以D5W稀釋成4倍量 (1ml=1mg)", "12mL注射用水", "-", "dose/4", "D5W 4倍", "-", "-", "F*4", "120"],
    "Micafungin 50mg/Vial": ["1vial加入5 mL NS/D5W(1mL=10mg)，稀釋成10倍量(1mL=1mg)", "5mL N/S D5W", "-", "dose/10", "D/W N/S 10倍", "-", "-", "F*10", "60"],
    "Acyclovir (250 mg/Vial)": ["1vial加入10mL N/S(1mL=25mg)，以N/S稀釋成5倍量 (1ml=5mg)", "10mL N/S", "-", "dose/25", "N/S 5倍", "-", "-", "F*5", "60"],
    "Ganciclovir (500mg/Vial)": ["1vial加入10mL 注射用水 (1mL=50mg)，以N/S稀釋成5倍量 (1ml=10mg)", "10mL注射用水", "-", "dose/50", "N/S 5倍", "-", "-", "F*5", "60"],
    "Calcium gluconate (1000mg/10mL)": ["抽實際dose (1mL=100mg)，稀釋成2倍量 (1ml=50mg)", "-", "dose/100", "-", "D5W N/S 2倍", "-", "-", "D*2", "30"],
    "Furosemide (20mg/2mL/Amp)": ["不需稀釋(=10mg/mL) 取實際dose", "-", "dose/10", "-", "-", "-", "-", "D", "15"],
    "Bumetanide (2mg/4mL/Amp)": ["取實際dose, 稀釋為2倍量 (1ml=0.25mg)", "-", "dose/0.5", "-", "D5W N/S 2倍", "-", "-", "D*2", "1-2"],
    "Ibuprofen (10mg/2mL/Amp)": ["不稀釋取實際dose，建議用1.5mL N/S drip 30 mins", "-", "dose/5", "-", "-", "-", "-", "D", "30"],
    "Propacetamol 1 g/Vial": ["1 vial 加入 5mL 溶解液 (1mL=200mg)，以N/S稀釋成10倍量 (1ml=20mg)", "5mL 溶解液", "-", "dose/200", "N/S 10倍", "-", "-", "F*10", "30"],
    "Aminophylline (250mg/10mL)": ["不需稀釋(=25mg/mL) 取實際dose", "-", "dose/25", "-", "-", "-", "-", "D", "30"],
    "Caffeine citrate (20mg/mL)": ["不需稀釋(=20mg/mL) 取實際dose", "-", "dose/20", "-", "-", "-", "-", "D", "30"],
    "Diazepam (10 mg/2ml/Amp)": ["不稀釋 (5mg/mL)，IVP 0.4ml/min", "-", "dose/5", "-", "-", "-", "-", "D", "0.4ml/min"],
    "Lorazepam (2mg/mL/Amp)": ["取實際dose，稀釋成5倍量 (1mL=0.4mg)給藥", "-", "dose/2", "-", "N/S 5倍", "-", "-", "D*5", "30"],
    "Phenobarbital (100mg/mL/Amp)": ["取實際dose，稀釋成10倍量 (1mL=10mg)給藥", "-", "dose/100", "-", "N/S 10倍", "-", "-", "D*10", "30"],
    "Levetiracetam (500mg/5mL/Vial)": ["取實際dose，稀釋成10倍量 (1mL=10mg)給藥", "-", "dose/100", "-", "N/S 10倍", "-", "-", "D*10", "30"],
    "Morphine (10 mg/ml/Amp)": ["取實際dose，稀釋成20倍量 (1mL=0.5mg)給藥", "-", "dose/10", "-", "N/S 20倍", "-", "-", "D*20", "30"],
    "Fentanyl (0.05mg/mL) 2mL/Amp": ["取實際dose，稀釋成25倍量 (1mL=0.002mg)給藥", "-", "dose/0.05", "-", "N/S 25倍", "-", "-", "D*25", "30"],
    "Ketamine (500mg/10mL/Vial)": ["IVP：不稀釋，取實際dose, IVP>1 min", "-", "dose/50", "-", "-", "-", "-", "D", "IVP>1 min"],
    "Pantoprazole (40mg/vial)": ["1vial加入10mL 注射用水 (1mL=4mg)，稀釋成5倍量 (1mL=0.8mg)", "10mL注射用水", "-", "dose/4", "N/S 5倍", "-", "-", "F*5", "30"],
    "Metoclopramide (10mg/2mL/Amp)": ["不需稀釋，取實際dose，建議用1.5mL N/S drip 30 mins", "-", "dose/5", "-", "-", "-", "-", "D", "30"],
    "Hydrocortisone (100mg/Vial) IVP": ["IVP：1vial加入2mL N/S (1mL=50mg) 配置， 取實際dose", "2mL N/S", "-", "dose/50", "-", "-", "-", "F", ">30sec"],
    "Famotidine (20mg/2mL/Amp)": "SPECIAL_FAMO",
    "Dexamethasone (5mg/mL/Amp)": "SPECIAL_DEX",
    "Hydrocortisone (100mg/Vial) IVD": "SPECIAL_HYDRO"
}

# --- 5. 藥品選擇與清除按鈕 ---
c_select, c_button = st.columns([4, 1])
with c_select:
    selected_name = st.selectbox("💊 請選擇藥品項目:", ["-- 請選擇 --"] + sorted(list(drug_data.keys())), key="drug_choice")

with c_button:
    st.write("<div style='padding-top: 32px;'></div>", unsafe_allow_html=True)
    st.button("🔄 清除", on_click=clear_fields, use_container_width=True)

if selected_name != "-- 請選擇 --":
    st.markdown("---")
    dose = st.number_input("💉 醫師開立劑量 (mg):", min_value=0.0, step=0.001, format="%.3f", key="dose_input")
    
    res = {k: "--" for k in ["D", "E", "F", "G", "H", "I", "J", "time", "nicu"]}
    show_warning = False

    if drug_data[selected_name] == "SPECIAL_HYDRO":
        res["nicu"] = "1vial加入2mL N/S(1mL=50mg)，若取藥<=0.1mL，稀釋成1mL(5mg/mL)再取藥，並稀釋5倍"
        res["E"] = "2mL N/S"
        if dose > 0:
            if (dose/50.0) <= 0.1:
                res.update({"F": "抽0.1mL, dilute to 1mL", "G": "-", "I": "NS 5倍", "J": f"{(dose/5.0)*5:.3f}"})
                show_warning = True
            else:
                res.update({"F": f"{dose/50.0:.3f}", "G": "NS 50倍", "I": "-", "J": f"{(dose/50.0)*50:.3f}"})
        res["time"] = "30"
    elif drug_data[selected_name] == "SPECIAL_FAMO":
        res["nicu"] = "抽0.1mL(10mg)稀釋成1mL(1mg)再取，或直接取10mg/mL後稀釋50倍"
        res["E"] = "-"
        if dose > 0:
            if (dose/10.0) <= 0.1:
                res.update({"D": "抽0.1mL, dilute to 1mL", "G": "-", "I": "NS 5倍", "J": f"{dose*5:.3f}"})
                show_warning = True
            else:
                res.update({"D": f"{dose/10.0:.3f}", "G": "NS 50倍", "I": "-", "J": f"{(dose/10.0)*50:.3f}"})
        res["time"] = "30"
    elif drug_data[selected_name] == "SPECIAL_DEX":
        res["nicu"] = "不需稀釋(5mg/mL)；若劑量<=0.1mL，稀釋成1mL(0.5mg/mL)再取藥"
        res["E"] = "-"
        if dose > 0:
            if (dose/5.0) <= 0.1:
                res.update({"D": "抽0.1mL, dilute to 1mL", "I": "稀釋至1mL", "J": f"{(dose/0.5):.3f}"})
                show_warning = True
            else:
                res.update({"D": f"{dose/5.0:.3f}", "J": f"{dose/5.0:.3f}"})
        res["time"] = "30"
    else:
        d = drug_data[selected_name]
        res["nicu"], res["E"], res["G"], res["I"], res["time"] = d[0], d[1], d[4], d[6], d[8]
        if dose > 0:
            d_val = eval(d[2].replace("dose", str(dose))) if d[2] != "-" else 0
            f_val = eval(d[3].replace("dose", str(dose))) if d[3] != "-" else 0
            res["D"] = f"{d_val:.3f}" if d[2] != "-" else "-"
            res["F"] = f"{f_val:.3f}" if d[3] != "-" else "-"
            j_expr = d[7].replace("D", str(d_val)).replace("F", str(f_val))
            res["J"] = f"{eval(j_expr):.3f}"
            if res["I"] != "-": show_warning = True

    if show_warning:
        st.markdown('<div class="warning-text">⚠️ 注意：此藥物劑量極小，請務必確認二次稀釋步驟！</div>', unsafe_allow_html=True)

    st.markdown('<p class="label-text">NICU 泡製方式說明:</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box-style">{res["nicu"]}</div>', unsafe_allow_html=True)
    
    display_fields = [
        ("純藥液品項取藥量 (mL)", res["D"]),
        ("1 vial 配置液與量", res["E"]),
        ("配置後取藥量 (mL)", res["F"]),
        ("稀釋倍率", res["G"]),
        ("再稀釋倍率", res["I"]),
        ("建議給藥時間 (分鐘)", res["time"])
    ]

    for label, val in display_fields:
        st.markdown(f'<p class="label-text">{label}</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{val}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="label-text" style="text-align:center;">給藥前最終體積</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box-style"><div class="final-volume-text">{res["J"]} mL</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📲 如何將計算機加入手機桌面？"):
        st.markdown("""
        **iPhone (Safari):**
        1. 打開本網頁，點擊底部的「分享」按鈕 (方框向上箭頭)。
        2. 向上滑動選單，選擇「加入主畫面」。
        
        **Android (Chrome):**
        1. 打開本網頁，點擊右上角「三個小點 (⋮)」。
        2. 選擇「安裝應用程式」或「加到主螢幕」。
        
        *完成後，你的桌面上會出現一個 💊 小藥丸專屬圖示！*
        """)
else:
    st.info("👋 請由下拉選單選擇藥品項目開始。")

st.markdown('<p style="color:gray; font-size:0.8em; text-align:center; margin-top:50px;">智慧搖籃專案 | 數值四捨五入至千分位 | 技術支援: NICU 臨床藥師</p>', unsafe_allow_html=True)
