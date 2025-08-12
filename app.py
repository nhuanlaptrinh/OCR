import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io

# ========================================================================================
# CẤU HÌNH TRANG
# ========================================================================================
st.set_page_config(
    page_title="Trợ lý OCR Thông minh",
    page_icon="📄",
    layout="wide"
)

# ========================================================================================
# HÀM HỖ TRỢ (LOGIC XỬ LÝ)
# ========================================================================================

@st.cache_data  # Sử dụng cache để không xử lý lại file đã xử lý
def process_file(file_bytes, file_extension, selected_lang):
    """
    Hàm trung tâm xử lý file đầu vào (ảnh hoặc PDF) và trả về văn bản được trích xuất.
    """
    extracted_text = ""
    try:
        if file_extension == 'pdf':
            images = convert_from_bytes(file_bytes)
            all_text = []
            progress_bar = st.progress(0, text="Đang xử lý file PDF...")
            for i, img in enumerate(images):
                all_text.append(pytesseract.image_to_string(img, lang=selected_lang))
                progress_bar.progress((i + 1) / len(images))
            extracted_text = "\n\n--- Hết trang ---\n\n".join(all_text)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = pytesseract.image_to_string(image, lang=selected_lang)
        return extracted_text, None
    except Exception as e:
        return None, f"Đã xảy ra lỗi trong quá trình xử lý: {e}"

# ========================================================================================
# GIAO DIỆN CHÍNH CỦA ỨNG DỤNG
# ========================================================================================

st.title("📄 Trợ lý OCR Thông minh")
st.write("Trích xuất văn bản từ file ảnh hoặc PDF. Hỗ trợ Tiếng Việt và Tiếng Anh.")

# Cột cho phần tải lên và các tùy chọn
col1, col2 = st.columns([2, 1])

with col1:
    # THÊM LỰA CHỌN NGÔN NGỮ
    lang_option = st.radio(
        "Chọn ngôn ngữ trong tài liệu:",
        ("Chỉ Tiếng Việt", "Chỉ Tiếng Anh", "Tiếng Việt + Tiếng Anh"),
        horizontal=True,
    )

    # Chuyển đổi lựa chọn của người dùng thành mã ngôn ngữ cho Tesseract
    lang_code_map = {
        "Chỉ Tiếng Việt": "vie",
        "Chỉ Tiếng Anh": "eng",
        "Tiếng Việt + Tiếng Anh": "vie+eng"
    }
    selected_lang_code = lang_code_map[lang_option]
    
    # Tiện ích tải file
    uploaded_files = st.file_uploader(
        "Tải lên MỘT hoặc NHIỀU file...",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )

with col2:
    with st.expander("💡 Mẹo sử dụng", expanded=True):
        st.info("""
        - **Chọn đúng ngôn ngữ** để có kết quả chính xác nhất.
        - Chọn **"Tiếng Việt + Tiếng Anh"** nếu tài liệu của bạn chứa cả hai loại ngôn ngữ.
        - Để có kết quả tốt nhất, hãy sử dụng ảnh rõ nét, chữ không bị mờ.
        """)

# Xử lý nếu người dùng đã tải file lên
if uploaded_files:
    st.markdown("---")
    st.header("Kết quả trích xuất")

    for uploaded_file in uploaded_files:
        with st.expander(f"Kết quả cho file: {uploaded_file.name}", expanded=True):
            with st.spinner(f"Đang xử lý '{uploaded_file.name}' với chế độ '{lang_option}'..."):
                file_bytes = uploaded_file.getvalue()
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                # Gọi hàm xử lý và truyền vào ngôn ngữ đã chọn
                text, error = process_file(file_bytes, file_extension, selected_lang_code)

            if error:
                st.error(error)
            else:
                st.text_area("Văn bản:", text, height=300, key=f"text_{uploaded_file.name}")
                st.download_button(
                    label="📥 Tải kết quả này",
                    data=text.encode('utf-8'),
                    file_name=f"ket_qua_{uploaded_file.name}.txt",
                    mime="text/plain",
                    key=f"download_{uploaded_file.name}"
                )
