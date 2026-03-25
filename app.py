import streamlit as st

# 設定網頁標題與圖示
st.set_page_config(page_title="NICU 給藥安全計算機", page_icon="👶")

# 顯示標題
st.title("🛡️ 智慧搖籃：新生兒給藥安全系統")
st.info("本工具由 Excel 全藥品匯入邏輯轉化，僅供臨床輔助參考。")

# 1. 藥品資料庫 (從你提供的 HTML 邏輯簡化轉譯)
# 格式: "藥名": [濃度mg/mL, 稀釋倍率, 給藥時間]
drug_data = {
    "Ampicillin (500mg/Vial)": [100, 1, "30"],
    "Gentamicin (80mg/2mL/Vial)": [40, 4, "60"],
    "CeFoTaxiMe (2g/Vial)": [200, 5, "30"],
    "Cefazolin (1000mg/vial)": [100, 1, "30"],
    "Ceftriaxone (1g/Vial)": [100, 2.5, "60"],
    "Oxacillin (500mg/Vial)": [100, 5, "60"],
    "Meropenem (250mg/Vial)": [20, 1, "30/240"],
    "Vancomycin (500mg/Vial)": [50, 10, "60"],
    "Furosemide (20mg/2mL/Amp)": [10, 1, "15"],
}

# 2. 介面設計
selected_drug = st.selectbox("1. 請選擇藥品項目：", list(drug_data.keys()))
dose_mg = st.number_input("2. 醫師開立劑量 (mg)：", min_value=0.0, step=0.1, format="%.3f")

if selected_drug and dose_mg > 0:
    # 取得藥品參數
    conc, dilute, time = drug_data[selected_drug]
    
    # 3. 計算邏輯
    # 取藥量 = 劑量 / 濃度
    take_vol = dose_mg / conc
    # 最終體積 = 取藥量 * 稀釋倍率
    final_vol = take_vol * dilute
    
    st.markdown("---")
    st.subheader("📊 計算結果")
    
    # 顯示美觀的結果卡片
    col1, col2 = st.columns(2)
    with col1:
        st.metric("配置後取藥量", f"{take_vol:.3f} mL")
    with col2:
        st.metric("給藥前最終體積", f"{final_vol:.3f} mL")
        
    st.success(f"⏱️ **建議給藥時間：** {time} 分鐘")
    
    # 複製文字功能 (方便紀錄)
    result_text = f"藥品: {selected_drug}\n劑量: {dose_mg} mg\n最終體積: {final_vol:.3f} mL\n給藥時間: {time} min"
    st.download_button("下載計算紀錄", result_text, file_name="calculation.txt")

# 頁尾標示
st.markdown("---")
st.caption("智慧搖籃專案：新生兒給藥安全系統 ")
