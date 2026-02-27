import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. Cấu hình giao diện chuẩn nhận diện thương hiệu
st.set_page_config(page_title="AI Thuế TNCN - Trạm Tuân Thủ Thông Minh", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #001F5B;} /* Xanh Navy */
    .stButton>button {background-color: #D4AF37; color: #001F5B; font-weight: bold; border-radius: 5px; width: 100%; border: none; padding: 10px;} /* Vàng Gold */
    .stButton>button:hover {background-color: #b5952f; color: #ffffff;}
    .info-box {background-color: #e9ecef; padding: 15px; border-left: 5px solid #001F5B; border-radius: 4px; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AI Chẩn Đoán Rủi Ro Thuế TNCN")
st.markdown("**Đơn vị phát triển:** Trạm Tuân Thủ Thông Minh (Smart Compliance Hub)")

st.markdown('<div class="info-box">Hệ thống tự động phân tích dữ liệu tiền lương, rà soát cấu trúc phụ cấp và đối chiếu với Luật Thuế TNCN hiện hành để phát hiện rủi ro truy thu/phạt vi phạm.</div>', unsafe_allow_html=True)

# Lấy API Key từ "két sắt" của Streamlit
api_key = st.secrets.get("GOOGLE_API_KEY")

# 2. Khu vực nhập liệu dữ liệu đầu vào
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Cách 1: Nhập dữ liệu nhanh")
    salary_data = st.text_area(
        "Nhập thông tin lương/phụ cấp hoặc dán (paste) dữ liệu từ Excel vào đây:", 
        height=200,
        placeholder="Ví dụ: \n- Nhân viên A: Lương cơ bản 10tr, phụ cấp xăng xe 5tr, ăn trưa 2tr, không người phụ thuộc.\n- Lương gộp: 17tr..."
    )

with col2:
    st.subheader("Cách 2: Tải lên tài liệu")
    st.info("Hỗ trợ định dạng: Hình ảnh (JPG, PNG), PDF hoặc Text (TXT, CSV).")
    uploaded_file = st.file_uploader("Kéo thả file Bảng lương / Hợp đồng vào đây...", type=["jpg", "png", "pdf", "txt", "csv"])

# 3. Nút xử lý cốt lõi
st.markdown("---")
if st.button("🔍 Bắt Đầu Quét & Phân Tích Rủi Ro"):
    if not api_key:
        st.error("Hệ thống chưa được cấp API Key trong phần cài đặt bảo mật (Secrets).")
    elif not salary_data and not uploaded_file:
        st.error("Vui lòng cung cấp dữ liệu bằng cách nhập văn bản hoặc tải file lên!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            with st.spinner("⏳ Chuyên gia AI đang đối chiếu dữ liệu với Luật Thuế. Vui lòng đợi..."):
                
                # Chuẩn bị dữ liệu gửi đi
                contents_to_send = []
                
                # Prompt hệ thống khắt khe
                prompt = """
                Bạn là Chuyên gia Đánh giá Rủi ro Thuế TNCN cấp cao tại "Trạm Tuân Thủ Thông Minh". 
                Nhiệm vụ của bạn là rà soát dữ liệu tiền lương/phụ cấp được cung cấp và chỉ ra các rủi ro pháp lý theo Luật Thuế TNCN hiện hành.

                YÊU CẦU PHÂN TÍCH:
                1. Tính hợp lý của Phụ cấp: Phát hiện các khoản phụ cấp quá cao so với lương cơ bản (có dấu hiệu trốn thuế).
                2. Rủi ro truy thu: Chỉ ra các khoản thu nhập có khả năng bị cơ quan thuế bóc tách và tính thuế.
                3. Thiếu sót hồ sơ: Đề xuất các giấy tờ/chứng từ cần thiết để bảo vệ chi phí hợp lý.

                CẤU TRÚC BÁO CÁO (Trình bày bằng Markdown chuyên nghiệp):
                ### 📊 1. TÓM TẮT TÌNH TRẠNG DỮ LIỆU
                (Tóm tắt ngắn gọn cấu trúc thu nhập bạn đọc được)

                ### 🚨 2. CÁC RỦI RO THUẾ TNCN PHÁT HIỆN ĐƯỢC
                (Liệt kê các điểm bất thường, rủi ro truy thu, vi phạm tỷ lệ)

                ### 💡 3. GIẢI PHÁP & KHUYẾN NGHỊ TỪ TRẠM TUÂN THỦ THÔNG MINH
                (Đưa ra lời khuyên cụ thể để cơ cấu lại lương/phụ cấp cho hợp pháp và tối ưu)
                """
                contents_to_send.append(prompt)

                # Nạp dữ liệu văn bản (nếu có)
                if salary_data:
                    contents_to_send.append(f"DỮ LIỆU KHÁCH HÀNG CUNG CẤP:\n{salary_data}")

                # Nạp file upload (nếu có)
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    ai_file = genai.upload_file(path=tmp_file_path)
                    contents_to_send.append(ai_file)

                # Yêu cầu AI xử lý
                response = model.generate_content(contents_to_send)
                
                # Dọn dẹp file rác
                if uploaded_file:
                    os.remove(tmp_file_path)

            st.success("✅ Đã hoàn thành Báo cáo Đánh giá Rủi ro!")
            st.markdown("---")
            st.write(response.text)

        except Exception as e:

            st.error(f"Đã xảy ra lỗi hệ thống: {e}")



