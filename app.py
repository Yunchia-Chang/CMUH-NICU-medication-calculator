import streamlit as st

st.set_page_config(page_title="NICU 給藥計算機 — 全藥品版", page_icon="💊", layout="wide")

# 自定義 CSS 樣式
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    .label-text { font-weight: bold; color: #333; margin-bottom: 5px; font-size: 1.1em; }
    .value-box { padding: 12px; background: #ffffff; border-radius: 8px; border: 1px solid #ccc; min-height: 45px; margin-bottom: 15px; font-family: 'Courier New', monospace; font-size: 1.1em; color: #000; }
    .final-result { padding: 20px; background: #FFF8DC; border: 3px solid #e0d700; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.8em; color: #d4af37; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .info-box { background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 15px; margin-bottom: 20px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ NICU 給藥計算機 (由 Excel 全藥品匯入)")

# --- 核心資料庫 (44項藥品) ---
# 格式說明: [nicu說明, E(配置液), D(純藥公式), F(配置後公式), G(稀釋倍), H(二次藥液), I(再稀釋), J(最終公式), time(分鐘)]
drug_data = {
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
    # 特殊邏輯藥品標記
    "Dexamethasone (5mg/mL/Amp)": "SPECIAL_DEX",
    "Hydrocortisone (100mg/Vial) IVD": "SPECIAL_HYDRO",
    "Hydrocortisone (100mg/Vial) IVP": ["IVP：1vial加入2mL N/S (1mL=50mg) 配置， 取實際dose", "2mL N/S", "-", "dose/50", "-", "-", "-", "F", ">30sec"],
    "Famotidine (20mg/2mL/Amp)": "SPECIAL_FAMO"
}

# --- 側邊欄 ---
st.sidebar.header("⚙️ 參數設定")
selected_name = st.selectbox("💊 請選擇藥品項目：", ["-- 請選擇 --"] + list(drug_data.keys()))

if selected_name != "-- 請選擇 --":
    # 劑量輸入
    dose = st.number_input("💉 醫師開立劑量 (mg)：", min_value=0.0, step=0.001, format="%.3f")
    
    # 建立計算字典
    res = {k: "--" for k in ["D", "E", "F", "G", "H", "I", "J", "time", "nicu"]}
    
    # 1. 處理特殊藥品邏輯
    if drug_data[selected_name] == "SPECIAL_HYDRO":
        res["nicu"] = "1vial加入2mL N/S(1mL=50mg)，若取藥<=0.1mL，稀釋成1mL(5mg/mL)再取藥，並稀釋5倍"
        res["E"] = "2mL N/S"
        if dose > 0:
            if (dose/50.0) <= 0.1:
                res.update({"F": "抽0.1mL, dilute to 1mL", "G": "-", "H": "-", "I": "NS 5倍", "J": f"{(dose/5.0)*5:.3f}"})
            else:
                res.update({"F": f"{dose/50.0:.3f}", "G": "NS 50倍", "H": "-", "I": "-", "J": f"{(dose/50.0)*50:.3f}"})
        res["time"] = "30"

    elif drug_data[selected_name] == "SPECIAL_FAMO":
        res["nicu"] = "抽0.1mL(10mg)稀釋成1mL(1mg)再取，或直接取10mg/mL後稀釋50倍"
        res["E"] = "-"
        if dose > 0:
            if (dose/10.0) <= 0.1:
                res.update({"D": "抽0.1mL, dilute to 1mL", "G": "-", "H": "-", "I": "NS 5倍", "J": f"{dose*5:.3f}"})
            else:
                res.update({"D": f"{dose/10.0:.3f}", "G": "NS 50倍", "H": "-", "I": "-", "J": f"{(dose/10.0)*50:.3f}"})
        res["time"] = "30"

    elif drug_data[selected_name] == "SPECIAL_DEX":
        res["nicu"] = "不需稀釋(5mg/mL)；若劑量<=0.1mL，稀釋成1mL(0.5mg/mL)再取藥"
        res["E"] = "-"
        if dose > 0:
            if (dose/5.0) <= 0.1:
                res.update({"D": "抽0.1mL, dilute to 1mL", "J": f"{(dose/0.5):.3f}"})
            else:
                res.update({"D": f"{dose/5.0:.3f}", "J": f"{dose/5.0:.3f}"})
        res["time"] = "30"

    # 2. 處理一般藥品邏輯
    else:
        d = drug_data[selected_name]
        res["nicu"], res["E"], res["G"], res["I"], res["time"] = d[0], d[1], d[4], d[6], d[8]
        
        if dose > 0:
            d_val = eval(d[2].replace("dose", str(dose))) if d[2] != "-" else 0
            f_val = eval(d[3].replace("dose", str(dose))) if d[3] != "-" else 0
            
            res["D"] = f"{d_val:.3f}" if d[2] != "-" else "-"
            res["F"] = f"{f_val:.3f}" if d[3] != "-" else "-"
            
            # 最終結果計算 J
            j_expr = d[7].replace("D", str(d_val)).replace("F", str(f_val))
            res["J"] = f"{eval(j_expr):.3f}"

    # --- 顯示介面 ---
    st.markdown(f'<div class="info-box"><b>NICU 泡製方式說明：</b><br>{res["nicu"]}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="label-text">純藥液品項取藥量 (mL)</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["D"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="label-text">1 vial 配置液與量</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["E"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="label-text">配置後取藥量 (mL)</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["F"]}</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<p class="label-text">稀釋倍率</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["G"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="label-text">再稀釋倍率</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["I"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<p class="label-text">建議給藥時間</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="value-box">{res["time"]} 分鐘</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="label-text" style="text-align:center;">給藥前最終體積</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="final-result">{res["J"]} mL</div>', unsafe_allow_html=True)

else:
    st.info("👋 您好！請從下拉選單選擇藥品開始計算。")

st.markdown('<p style="color:gray; font-size:0.8em; text-align:center; margin-top:50px;">智慧搖籃專案：新生兒科給藥安全之品質改善 | 數值四捨五入至千分位</p>', unsafe_allow_html=True)
