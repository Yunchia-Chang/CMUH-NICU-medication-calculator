import streamlit as st

st.set_page_config(page_title="NICU 給藥計算機", page_icon="💊", layout="wide")

# --- 自定義 CSS 與背景顏色 ---
st.markdown("""
    <style>
    /* 整體背景改為淡鵝黃色 */
    .stApp { background-color: #FFFDF0; }
    
    /* 標題與標籤文字改為黑色 */
    h1, .label-text { color: #000000 !important; font-weight: bold; }
    
    /* 泡製方式說明內部的文字顏色 */
    .info-box { background-color: #FFFFFF; border-left: 6px solid #FFD700; padding: 15px; margin-bottom: 20px; border-radius: 4px; color: #000000; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    
    /* 數值顯示框文字改為黑色 */
    .value-box { padding: 12px; background: #ffffff; border-radius: 8px; border: 1px solid #ccc; min-height: 45px; margin-bottom: 15px; font-family: 'Courier New', monospace; font-size: 1.1em; color: #000000; }
    
    /* 最終結果顯示 */
    .final-result { padding: 20px; background: #FFD700; border: 3px solid #000000; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.8em; color: #000000; }
    
    /* 警示文字樣式 */
    .warning-text { color: #FF0000; font-weight: bold; font-size: 1.2em; border: 2px solid #FF0000; padding: 10px; border-radius: 8px; background-color: #FFF0F0; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 初始化 Session State (用於清除功能) ---
if 'dose_input' not in st.session_state:
    st.session_state.dose_input = 0.0
if 'drug_choice' not in st.session_state:
    st.session_state.drug_choice = "-- 請選擇 --"

def clear_fields():
    st.session_state.dose_input = 0.0
    st.session_state.drug_choice = "-- 請選擇 --"

st.markdown("<h1>NICU 給藥計算機 (由 Excel 全藥品匯入)</h1>", unsafe_allow_html=True)

# --- 核心資料庫 (44項藥品) ---
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
    "Dexamethasone (5mg/mL/Amp)": "SPECIAL_DEX",
    "Hydrocortisone (100mg/Vial) IVD": "SPECIAL_HYDRO",
    "Hydrocortisone (100mg/Vial) IVP": ["IVP：1vial加入2mL N/S (1mL=50mg) 配置， 取實際dose", "2mL N/S", "-", "dose/50", "-", "-", "-", "F", ">30sec"],
    "Famotidine (20mg/2mL/Amp)": "SPECIAL_FAMO"
}

# --- 藥品選擇與劑量輸入 ---
c_top1, c_top2 = st.columns([3, 1])
with c_top1:
    selected_name = st.selectbox("請選擇藥品項目:", ["-- 請選擇 --"] + list(drug_data.keys()), key="drug_choice")

with c_top2:
    st.write(" ") # 調整按鈕位置
    st.button("🔄 清除重新計算", on_click=clear_fields)

if selected_name != "-- 請選擇 --":
    dose = st.number_input("💉 醫師開立劑量 (mg):", min_value=0.0, step=0.001, format="%.3f", key="dose_input")
    
    res = {k: "--" for k in ["D", "E", "F", "G", "H", "I", "J", "time", "nicu"]}
    show_warning = False

    # 1. 處理特殊藥品邏輯
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

    # 2. 處理一般藥品
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

    # --- 顯示介面 ---
    # 警示語 (只在需要二次稀釋時顯示)
    if show_warning:
        st.markdown('<div class="warning-text">⚠️ 注意：此藥物劑量極小，請務必確認二次稀釋步驟！</div>', unsafe_allow_html=True)

    st.markdown('<p class="label-text">NICU 泡製方式說明:</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">{res["nicu"]}</div>', unsafe_allow_html=True)
    
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
    st.info("👋 請由下拉選單選擇藥品開始計算。")

st.markdown('<p style="color:gray; font-size:0.8em; text-align:center; margin-top:50px;">智慧搖籃專案 | 數值四捨五入至千分位</p>', unsafe_allow_html=True)
