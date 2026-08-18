import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình trang web chuyên nghiệp cho dân kinh doanh
st.set_page_config(page_title="AI Profit Analyzer", layout="wide", page_icon="💸")
st.title("💸 AI Automatically Calculates Online Shop Profit")
st.success("⚡ EXCLUSIVE VIP TOOL - HELPS SHOP OWNERS KEEP THEIR CASH FLOW SAFE")

# Thanh hướng dẫn 3 bước giúp ní ẩn mình hoàn toàn khi bán trên Sharecode / Gumroad
with st.expander("📖 3-STEP GUIDE FOR SHOP OWNERS (USE FOR LIFE))", expanded=True):
    st.markdown("""
    *   **Step 1:** Enter the total **Gross Revenue** earned from platforms (TikTok, Shopee, etc.) into the first box.  
* **Step 2:** Use the **Draft Spreadsheet** in the middle for quick calculations (e.g., 100 boxes * 5,000 dolars). The results will automatically sync to the main expense table.  
* **Step 3:** Double-check the **Expense Declaration Table**, you can edit directly or click **"+ Add row"** to add other expenses, then hit the rocket button to see the results.
    """)

st.write("---")

# CƠ CHẾ NÚT RESET DỮ LIỆU TOÀN DIỆN
if st.button("🔄 Delete All Data (RESET)"):
    # Xoá session state để đưa bảng tính nháp về ban đầu
    if 'calculator_input' in st.session_state:
        del st.session_state['calculator_input']
    if 'expense_editor' in st.session_state:
        del st.session_state['expense_editor']
    if 'data_nhap' in st.session_state:
        del st.session_state['data_nhap']
    st.rerun()

# 1. Ô nhập Doanh thu thô (Doanh thu chưa trừ chi phí)
st.subheader("💰 1. Gross Revenue From Platforms:")
doanh_thu = st.number_input("Total gross revenue displayed on platform app ($):", min_value=0, value=0, step=100000)

st.write("---")

# 2. BẢNG TÍNH NHÁP SỐ HỌC TỰ ĐỘNG ĐỒNG BỘ
st.subheader("🧮 2. Draft Calculation Table (Auto-Sync):")
st.caption("💡 Enter expense names here, select an operation for the system to automatically multiply/divide/add/subtract and add to the expense table below.")

# Tạo danh mục nháp mẫu ban đầu nếu chưa có
if 'data_nhap' not in st.session_state:
    st.session_state.data_nhap = pd.DataFrame([
        {"Cost Item": "Shipping/Packaging Compensation", "First Number": 100, "Operation": "*", "Second Number": 5000}
    ])

bang_nhap = st.data_editor(
    st.session_state.data_nhap,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Operation": st.column_config.SelectboxColumn(options=["+", "-", "*", "/"], required=True)
    },
    key="calculator_input"
)

# Xử lý tính toán cho bảng nháp và lưu kết quả
df_nhap_tinh_toan = pd.DataFrame(bang_nhap)
chi_phi_dong_bo = {}

if not df_nhap_tinh_toan.empty:
    for idx, row in df_nhap_tinh_toan.iterrows():
        try:
            name = str(row["Cost Item"]).strip()
            num1 = float(row["First Number"])
            num2 = float(row["Second Number"])
            op = row["Operation"]

            if op == "+": res = num1 + num2
            elif op == "-": res = num1 - num2
            elif op == "*": res = num1 * num2
            elif op == "/": res = num1 / num2 if num2 != 0 else 0
            else: res = 0
            
            if name and name != "None" and name != "nan":
                chi_phi_dong_bo[name] = int(res)
        except:
            continue

st.write("---")

# 3. Bảng nhập chi phí vận hành shop (Đã đồng bộ)
st.subheader("📉 3. Expense Declaration Table (Auto-Sync):")

# Khởi tạo danh mục chi phí mặc định
data_chi_phi_mac_dinh = [
    {"Cost Item": "Inventory Purchase", "Amount ($)": 0},
    {"Cost Item": "Platform Fee (TikTok/Shopee %)", "Amount ($)": 0},
    {"Cost Item": "Advertising Costs (Ads)", "Amount ($)": 0},
    {"Cost Item": "Shipping/Packaging Compensation", "Amount ($)": 0}
]

# Chuyển đổi và nạp giá trị từ bảng nháp vào bảng chính
for item in data_chi_phi_mac_dinh:
    if item["Cost Item"] in chi_phi_dong_bo:
        item["Amount ($)"] = chi_phi_dong_bo[item["Cost Item"]]

df_mac_dinh = pd.DataFrame(data_chi_phi_mac_dinh)

# Thêm những chi phí mới từ bảng nháp không trùng với mặc định vào bảng chính
for name, val in chi_phi_dong_bo.items():
    if name not in df_mac_dinh["Cost Item"].values:
        df_mac_dinh = pd.concat([df_mac_dinh, pd.DataFrame([{"Cost Item": name, "Amount ($)": val}])], ignore_index=True)

# Hiển thị bảng chi phí chính cho người dùng chỉnh sửa thêm nếu muốn
bang_chi_phi = st.data_editor(
    df_mac_dinh,
    num_rows="dynamic",
    use_container_width=True,
    key="expense_editor"
)

st.write("---")

# 4. Nút bấm kích hoạt Bộ não AI Pandas để tính Lợi Nhuận Ròng
if st.button("🚀 KÍCH HOẠT AI TÍNH LỢI NHUẬN THỰC TẾ"):
    # Lấy dữ liệu trực tiếp từ bảng kê khai chi phí cuối cùng
    df_chi_phi = pd.DataFrame(bang_chi_phi)
    
    # Ép kiểu dữ liệu an toàn tránh lỗi NaN hoặc chuỗi chữ
    df_chi_phi["Amount ($)"] = pd.to_numeric(df_chi_phi["Amount ($)"], errors='coerce').fillna(0).astype(float)
    
    # Lọc bỏ các dòng có chi phí bằng 0 để vẽ biểu đồ tròn không bị rối
    df_chi_phi_bieu_do = df_chi_phi[df_chi_phi["Amount ($)"] > 0]
    
    # Tính tổng chi phí
    tong_chi_phi = df_chi_phi["Amount ($)"].sum()
    
    # Tính Lợi nhuận ròng (Tiền thực tế bỏ túi)
    loi_nhuan_rong = doanh_thu - tong_chi_phi
    
    # Tính Tỷ suất lợi nhuận (%)
    ty_suat = (loi_nhuan_rong / doanh_thu * 100) if doanh_thu > 0 else 0
    
    # Hiển thị kết quả bằng các ô chỉ số (Metrics) cực kỳ sang chảnh
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📊 Total Operating Costs", value=f"{tong_chi_phi:,} $")
    with c2:
        if loi_nhuan_rong >= 0:
            st.metric(label="🤑 Net Profit", value=f"{loi_nhuan_rong:,} $")
        else:
            st.metric(label="😭 Shop Is Operating At A Loss", value=f"{loi_nhuan_rong:,} $", delta="- Danger!")
    with c3:
        st.metric(label="📈 Net Profit Margin", value=f"{ty_suat:.1f} %")
        
    # Xử lý hiệu ứng hình ảnh và biểu đồ ăn tiền
    st.write("---")
    if loi_nhuan_rong > 0:
        st.balloons()
        st.success("🎉Congratulations! Your shop is running with very good profits. Keep it up!")
        
        # ĐỔI THÀNH BIỂU ĐỒ TRÒN (PIE CHART) BẰNG PLOTLY ĐẸP MẮT
        st.write("📊 **Chart analyzing the proportion of the shop's expenses:**")
        if not df_chi_phi_bieu_do.empty:
            fig = px.pie(
                df_chi_phi_bieu_do, 
                values='Amount ($)', 
                names='Cost Item', 
                hole=0.4, # Tạo khoảng trống ở giữa làm donut chart nhìn hiện đại hơn
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 There are no expenses greater than 0 $ to display in the chart.")
            
    elif doanh_thu == 0 and tong_chi_phi == 0:
        st.info("💡 Please fill in the revenue and expense numbers so the AI can calculate it, shop!")
    else:
        st.error("🚨 Shop is spending more than its revenue! Please check your advertising costs or import fees immediately!")
        
        # Vẫn vẽ biểu đồ tròn ở phần lỗ vốn để chủ shop biết tiền thất thoát đi đâu
        st.write("📊 **Chart analyzing the proportion of the shop's expenses:**")
        if not df_chi_phi_bieu_do.empty:
            fig = px.pie(df_chi_phi_bieu_do, values='Amount ($)', names='Cost Item', hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
