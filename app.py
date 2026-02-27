import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. Cấu hình giao diện Trạm Tuân Thủ Thông Minh
st.set_page_config(page_title="AI Thuế TNCN - Trạm Tuân Thủ Thông Minh", page_icon="🛡️", layout="wide")

# CSS Nhận diện thương hiệu (Xanh Navy & Vàng Gold)
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #001F5B;} 
    .stButton>button {background-color: #D4AF37; color: #001F5B; font-weight: bold; border-radius: 8px; width: 100%; border: none; padding: 12px;}
    .stButton>button:hover {background-color: #b5952f; color: #ffffff; box-shadow: 0 4px 8px rgba(0,0,0,0.2);}
    .status-box {background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 6px solid #D4AF37; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 25px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AI Thuế TNCN - Smart Compliance Hub")
st.markdown('<div class="status-box"><b>Hệ thống Chẩn đoán Rủi ro Thuế:</b> Chuyên rà soát bảng lương, phụ cấp và cấu trúc thu nhập để đảm bảo tính tuân thủ pháp lý cao nhất cho Doanh nghiệp.</div>', unsafe_allow_html=True)

# Lấy API Key từ Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

# 2. Giao diện nhập liệu
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Nhập dữ liệu lương")
    salary_data = st.text_area(
        "Dán dữ liệu từ Excel hoặc mô tả cấu trúc lương tại đây:", 
        height=250,
        placeholder="VD: Nguyễn Văn A, Lương 20tr, Phụ cấp xăng xe 5tr..."
    )

with col2:
    st.subheader("📁 Tải tệp tài liệu")
    st.info("Hệ thống hỗ trợ đọc trực tiếp: Ảnh chụp bảng lương, File PDF, BCTC hoặc Hợp đồng.")
    uploaded_file = st.file_uploader("Kéo thả tài liệu vào đây...", type=["jpg", "png", "pdf", "txt", "csv"])

# 3. Xử lý phân tích chuyên sâu
st.markdown("---")
if st.button("🚀 KÍCH HOẠT QUÉT RỦI RO THUẾ"):
    if not api_key:
        st.error("Lỗi: Chưa tìm thấy API Key trong cấu hình Secrets của Streamlit.")
    elif not salary_data and not uploaded_file:
        st.error("Vui lòng cung cấp dữ liệu đầu vào để AI bắt đầu làm việc.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # SỬ DỤNG MÔ HÌNH THẾ HỆ MỚI (Cập nhật theo danh sách của bạn)
            model = genai.GenerativeModel('gemini-2.5-flash')

            with st.spinner("⏳ Trí tuệ nhân tạo đang đối soát dữ liệu với Luật Thuế hiện hành..."):
                
                analysis_content = []
                
                # Prompt nghiệp vụ chuyên sâu cho Trạm Tuân Thủ
                system_prompt = """
                Bạn là 'Chuyên gia Thuế AI' thuộc hệ thống Trạm Tuân Thủ Thông Minh (Smart Compliance Hub).
                Nhiệm vụ: Phân tích dữ liệu tiền lương/thu nhập và cảnh báo rủi ro Thuế TNCN.

                CẤU TRÚC BÁO CÁO:
                1. 🔍 ĐÁNH GIÁ TỔNG QUAN: Tóm tắt các nhóm thu nhập phát hiện được.
                2. 🚨 CẢNH BÁO RỦI RO: 
                   - Chỉ ra các khoản phụ cấp vượt định mức miễn thuế.
                   - Cảnh báo các rủi ro truy thu do thiếu chứng từ hợp lệ.
                   - Nhận diện các dấu hiệu lách luật BHXH qua lương.
                3. 💡 KIẾN NGHỊ TUÂN THỦ: Đưa ra giải pháp điều chỉnh cấu trúc lương để tối ưu thuế một cách hợp pháp.
                """
                analysis_content.append(system_prompt)

                if salary_data:
                    analysis_content.append(f"Dữ liệu nhập tay: {salary_data}")

                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    
                    # Tải file lên hệ thống AI đời mới
                    ai_document = genai.upload_file(path=tmp_path)
                    analysis_content.append(ai_document)

                # Gọi AI thực hiện báo cáo
                response = model.generate_content(analysis_content)
                
                if uploaded_file:
                    os.remove(tmp_path)

            st.success("✅ Phân tích hoàn tất!")
            st.markdown("### 📋 BÁO CÁO CHẨN ĐOÁN CHI TIẾT")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Hệ thống gặp sự cố kết nối: {e}")
