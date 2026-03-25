import streamlit as st

# --- 頁面設定 ---
st.set_page_config(page_title="NICU 全藥品給藥計算機", page_icon="👶", layout="centered")

# 自定義樣式
st.markdown("""
    <style>
    .reportview-container { background: #f7f7f7; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #ddd; }
    .result-card { background-color: #FFF8DC; padding: 20px; border-radius: 10px; border: 2px solid #e0d700; text-align: center; }
    .desc-text { background-color: #fafafa; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ NICU 給藥計算機 (全藥品版)")
st.caption("智慧搖籃專案：基於 Excel 邏輯匯入之給藥安全系統")

# --- 1. 建立藥品資料庫 (對應你的 HTML Data 屬性) ---
# 格式: "名稱": {nicu說明, 基礎濃度mg_per_ml, 稀釋倍率, 時間, 類型}
drugs = {
    "Ampicillin (500mg/Vial)": {"desc": "1 vail 加入 5mL 注射用水 (1mL=100mg) 配置，取實際dose給藥，建議用1.5mL N/S drip 30 mins", "base_conc": 100, "dilute": 1, "time": "30", "type": "vial"},
    "Gentamicin (80mg/2mL/Vial)": {"desc": "取實際dose，稀釋成4倍量 (濃度：1mL=10mg)給藥，建議用1.5mL N/S drip 60 mins", "base_conc": 40, "dilute": 4, "time": "60", "type": "amp"},
    "CeFoTaxiMe (2g/Vial)": {"desc": "1vial加入10mL 注射用水 (1mL=200mg)，取實際dose，稀釋成5倍量 (1mL=40mg)，建議用1.5mL N/S drip 30 mins.", "base_conc": 200, "dilute": 5, "time": "30", "type": "vial"},
    "Cefazolin (1000mg/vial)": {"desc": "1 vail 加入 10mL N/S (1mL=100mg) 配置，取實際dose，建議用1.5mL N/S drip 30 mins", "base_conc": 100, "dilute": 1, "time": "30", "type": "vial"},
    "Ceftazidime (2000mg/vial)": {"desc": "1 vail 加入 10mL N/S (1mL=170mg)，取實際dose，稀釋成2倍(1 mL= 85mg)，建議用1.5mL N/S drip 60 mins", "base_conc": 170, "dilute": 2, "time": "60", "type": "vial"},
    "Ceftriaxone (1g/Vial)": {"desc": "1 vail 加入 10mL 注射用水 (1mL=100mg) 配置，取實際dose，稀釋成2.5倍量 (1ml=40mg) ,不足1mL者加到1mL，建議用1.5 mL N/S drip 60mins", "base_conc": 100, "dilute": 2.5, "time": "60", "type": "vial"},
    "Cefepime (1000mg/Vial)": {"desc": "1 vail 加入 10mL N/S 配置 (1mL=100mg)，取實際dose，建議用1.5 mL N/S drip 30mins.", "base_conc": 100, "dilute": 1, "time": "30", "type": "vial"},
    "Oxacillin (500mg/Vial)": {"desc": "1 vail 加入 5mL N/S (1mL=100mg)，取實際dose給藥，稀釋成5倍量 (1ml=20mg)，建議用1.5mL N/S drip 60 mins.", "base_conc": 100, "dilute": 5, "time": "60", "type": "vial"},
    "Amoxicillin 1.0g + Clavulanate 0.2g (1.2g/vial)": {"desc": "1vial加入20mL N/S (1mL=60mg A+C)，取實際dose，以N/S稀釋2.5倍 (1ml=24mg A+C),建議用1.5mL N/S drip 30 mins。", "base_conc": 60, "dilute": 2.5, "time": "30", "type": "vial"},
    "Ampicillin/Sulbactam (A+S 1.5g/vial)": {"desc": "1 vail 加入 3.2 mL N/S (1mL=375mg)，取實際dose，稀釋成10倍量 (1mL=37.5mg)，建議用1.5mL N/S drip 30 mins.", "base_conc": 375, "dilute": 10, "time": "30", "type": "vial"},
    "Piperacillin sodium 2 g + Tazobactam sodium 0.25 g/vial)": {"desc": "1 vial加入10 mL N/S (1mL=202.5mg), 取實際dose, 稀釋成2.5倍量 (1mL=81 mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 202.5, "dilute": 2.5, "time": "30", "type": "vial"},
    "Ertapenem 1g/Vial": {"desc": "1 vail 加入 10mL 注射用水配置 (1mL=100mg)，取實際dose，以N/S稀釋成5倍量 (1mL=20mg) 給藥，建議用1.5mL N/S drip 30 mins.", "base_conc": 100, "dilute": 5, "time": "30", "type": "vial"},
    "Meropenem (250mg/Vial)": {"desc": "1vial加入12.5mL N/S (1mL=20mg)，取實際dose，建議用1.5mL N/S drip 30-240 mins", "base_conc": 20, "dilute": 1, "time": "30/240", "type": "vial"},
    "Teicoplanin (200 mg/Vial)": {"desc": "1vial加入3mL 注射用水 (1mL=66.66mg)，取實際dose，建議用1.5mL N/S drip 30 mins", "base_conc": 66.66, "dilute": 1, "time": "30", "type": "vial"},
    "Metronidazole (500mg/100mL/bot)": {"desc": "不稀釋，取實際dose (5mg/mL), IVD 30-60 mins", "base_conc": 5, "dilute": 1, "time": "30-60", "type": "amp"},
    "Colistin (66.8mg CBA/vial)": {"desc": "1vial加入2mL N/S (1mL=33.4mg)，取實際dose，稀釋成2倍量(1mL=16.7mg)，建議用1.5mL N/S drip 30 mins。", "base_conc": 33.4, "dilute": 2, "time": "30", "type": "vial"},
    "Clindamycin 300mg/2mL/Amp": {"desc": "取實際dose，稀釋成25倍量 (1mL=6mg)給藥，建議用1.5mL N/S drip 30 mins", "base_conc": 150, "dilute": 25, "time": "30", "type": "amp"},
    "Fluconazole (100 mg/50 mL/Vial)": {"desc": "取實際dose (2mg/mL)，建議用1.5mL N/S drip 60 mins", "base_conc": 2, "dilute": 1, "time": "60", "type": "amp"},
    "Amphotericin B (50mg/Vial)": {"desc": "1vial加入10mL 注射用水(1mL=5mg)，稀釋成50倍量 (1ml=0.1mg)，建議用1.5 mL D5W drip 120-360min", "base_conc": 5, "dilute": 50, "time": "120-360", "type": "vial"},
    "Micafungin 50mg/Vial": {"desc": "1vial加入5 mL NS or D5W(1mL=10mg)，稀釋成10倍量(1mL=1mg)，建議用1.5 mL N/S drip 60min", "base_conc": 10, "dilute": 10, "time": "60", "type": "vial"},
    "Acyclovir (250 mg/Vial)": {"desc": "1vial加入10mL N/S(1mL=25mg)，稀釋成5倍量 (1ml=5mg)，建議用1.5 mL N/S drip 60min", "base_conc": 25, "dilute": 5, "time": "60", "type": "vial"},
    "Ganciclovir (500mg/Vial)": {"desc": "1vial加入10mL 注射用水 (1mL=50mg)，稀釋成5倍量 (1ml=10mg)，建議用1.5 mL N/S drip 60min", "base_conc": 50, "dilute": 5, "time": "60", "type": "vial"},
    "Calcium gluconate (1000mg/10mL/Amp)": {"desc": "抽實際dose (1mL=100mg)，稀釋成2倍量 (1ml=50mg)，建議用1.5 mL N/S drip 30mins。", "base_conc": 100, "dilute": 2, "time": "30", "type": "amp"},
    "Furosemide (20mg/2mL/Amp)": {"desc": "不需稀釋(=10mg/mL) 取實際dose，建議用1.5mL N/S drip 15 mins", "base_conc": 10, "dilute": 1, "time": "15", "type": "amp"},
    "Aminophylline (250mg/10mL/Amp)": {"desc": "不需稀釋(=25mg/mL) 取實際dose，建議用1.5mL N/S drip 30 mins", "base_conc": 25, "dilute": 1, "time": "30", "type": "amp"},
    "Caffeine citrate (20mg/mL/Amp)": {"desc": "不需稀釋(=20mg/mL) 取實際dose，建議用1.5mL N/S drip 30 mins", "base_conc": 20, "dilute": 1, "time": "30", "type": "amp"},
    "Diazepam (10 mg/2ml/Amp)": {"desc": "不稀釋 (5mg/mL)，IVP 0.4ml/min", "base_conc": 5, "dilute": 1, "time": "0.4ml/min", "type": "amp"},
    "Lorazepam (2mg/mL/Amp)": {"desc": "取實際dose (2mg/mL)，稀釋成5倍量 (1mL=0.4mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 2, "dilute": 5, "time": "30", "type": "amp"},
    "Phenobarbital (100mg/mL/Amp)": {"desc": "取實際dose，稀釋成10倍量 (1mL=10mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 100, "dilute": 10, "time": "30", "type": "amp"},
    "Levetiracetam (500mg/5mL/Vial)": {"desc": "取實際dose (100mg/mL)，稀釋成10倍量 (1mL=10mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 100, "dilute": 10, "time": "30", "type": "amp"},
    "Morphine (10 mg/ml/Amp)": {"desc": "取實際dose，稀釋成20倍量 (1mL=0.5mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 10, "dilute": 20, "time": "30", "type": "amp"},
    "Fentanyl (0.05mg/mL)": {"desc": "取實際dose，稀釋成25倍量 (1mL=0.002mg)，建議用1.5mL N/S drip 30 mins", "base_conc": 0.05, "dilute": 25, "time": "30", "type": "amp"},
    "Pantoprazole (40mg/vial)": {"desc": "1vial加入10mL注射用水 (1mL=4mg)，稀釋成5倍量 (1mL=0.8mg)，建議用1.5mL N/S drip 30 mins.", "base_conc": 4, "dilute": 5, "time": "30", "type": "vial"},
    "Metoclopramide (10mg/2mL/Amp)": {"desc": "不需稀釋 (5mg/mL)，取實際dose，建議用1.5mL N/S drip 30 mins", "base_conc": 5, "dilute": 1, "time": "30", "type": "amp"},
    # 特殊判斷藥品
    "Dexamethasone (5mg/mL/Amp)": {"desc": "如果劑量 <= 0.1mL(0.5mg)，建議先稀釋成0.5mg/mL再取藥。", "base_conc": 5, "type": "special_dex"},
    "Hydrocortisone (100mg/Vial) IVD": {"desc": "如果劑量 <= 0.1mL(5mg)，建議先稀釋成5mg/mL再取藥，並稀釋5倍。", "base_conc": 50, "type": "special_hydro"},
    "Famotidine (20mg/2mL/Amp)": {"desc": "如果劑量 <= 0.1mL(1mg)，建議先稀釋成1mg/mL再取藥，並稀釋5倍。", "base_conc": 10, "type": "special_famo"},
}

# --- 2. 側邊欄選單 ---
selected_name = st.selectbox("📌 選擇藥品名稱：", ["-- 請選擇 --"] + list(drugs.keys()))

if selected_name != "-- 請選擇 --":
    drug = drugs[selected_name]
    
    # 顯示泡製說明
    st.markdown(f'<div class="desc-text"><b>NICU 泡製說明：</b><br>{drug["desc"]}</div>', unsafe_allow_html=True)
    
    # 輸入開立劑量
    dose_mg = st.number_input("💉 醫師開立劑量 (mg)：", min_value=0.0, step=0.001, format="%.3f")

    if dose_mg > 0:
        st.markdown("---")
        
        # --- 3. 計算邏輯 (對應 HTML 的 IF 判斷) ---
        take_vol = 0.0
        final_vol = 0.0
        msg = ""
        
        # A. 一般藥品 (Normal & Amp/Vial)
        if drug.get("type") in ["vial", "amp"]:
            take_vol = dose_mg / drug["base_conc"]
            final_vol = take_vol * drug["dilute"]
            time_info = drug["time"]
            
        # B. Dexamethasone 特殊邏輯
        elif drug["type"] == "special_dex":
            pure_take = dose_mg / 5.0
            if pure_take <= 0.1:
                msg = "💡 檢測到小劑量：請抽 0.1mL 原藥液 + 0.9mL N/S (稀釋成 0.5mg/mL)"
                take_vol = dose_mg / 0.5
                final_vol = take_vol # 不再額外稀釋
            else:
                take_vol = pure_take
                final_vol = pure_take
            time_info = "30"

        # C. Hydrocortisone 特殊邏輯
        elif drug["type"] == "special_hydro":
            pure_take = dose_mg / 50.0
            if pure_take <= 0.1:
                msg = "💡 檢測到小劑量：請抽 0.1mL (50mg/mL) + 0.9mL N/S (稀釋成 5mg/mL)"
                take_vol = dose_mg / 5.0
                final_vol = take_vol * 5
            else:
                take_vol = pure_take
                final_vol = take_vol * 50
            time_info = "30"

        # D. Famotidine 特殊邏輯
        elif drug["type"] == "special_famo":
            pure_take = dose_mg / 10.0
            if pure_take <= 0.1:
                msg = "💡 檢測到小劑量：請抽 0.1mL (10mg/mL) + 0.9mL N/S (稀釋成 1mg/mL)"
                take_vol = dose_mg / 1.0
                final_vol = take_vol * 5
            else:
                take_vol = pure_take
                final_vol = pure_take * 50
            time_info = "30"

        # --- 4. 顯示結果 ---
        if msg:
            st.warning(msg)
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("配置後取藥量 (mL)", f"{take_vol:.3f}")
        with col2:
            st.markdown(f'<div class="result-card"><small>給藥前最終體積</small><br><b style="font-size:24px;">{final_vol:.3f} mL</b></div>', unsafe_allow_html=True)
            
        st.success(f"⏱️ **建議給藥時間：** {time_info} 分鐘")
        
        # 額外小提醒：不足 1mL 的處理 (針對 Ceftriaxone 等)
        if "不足1mL者加到1mL" in drug["desc"] and final_vol < 1.0:
            st.info("📢 注意：依據說明，最終體積不足 1mL 者，請加 N/S 補至 1mL。")

else:
    st.write("請從上方選單選擇藥品開始計算。")

st.markdown("---")
st.caption("智慧搖籃專案 :新生兒科給藥安全系統")
