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

def resize_image(image, max_width=1500):
    """Giảm kích thước ảnh nếu chiều rộng của nó lớn hơn max_width để tối ưu bộ nhớ."""
    try:
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            resized_image = image.resize((max_width, new_height), Image.LANCZOS)
            return resized_image
        return image
    except Exception:
        return image

def process_file(file_bytes, file_extension):
    """
    Hàm trung tâm xử lý file đầu vào (ảnh hoặc PDF) và trả về văn bản được trích xuất.
    """
    extracted_text = ""
    try:
        if file_extension == 'pdf':
            images = convert_from_bytes(file_bytes)
            all_text = []
            # Thêm st.progress để người dùng thấy tiến trình xử lý PDF
            progress_bar = st.progress(0)
            for i, img in enumerate(images):
                optimized_img = resize_image(img)
                all_text.append(pytesseract.image_to_string(optimized_img, lang='vie'))
                # Cập nhật thanh tiến trình
                progress_bar.progress((i + 1) / len(images))
            extracted_text = "\n\n--- Hết trang ---\n\n".join(all_text)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            image = Image.open(io.BytesIO(file_bytes))
            optimized_img = resize_image(image)
            extracted_text = pytesseract.image_to_string(optimized_img, lang='vie')
        return extracted_text, None
    except Exception as e:
        return None, f"Đã xảy ra lỗi trong quá trình xử lý: {e}"

# ========================================================================================
# GIAO DIỆN CHÍNH CỦA ỨNG DỤNG
# ========================================================================================

st.title("📄 Trợ lý OCR Thông minh")
st.write("Trích xuất văn bản Tiếng Việt từ file ảnh hoặc PDF. Hỗ trợ tải lên nhiều file cùng lúc.")

# Cột cho phần tải lên và hướng dẫn
col1, col2 = st.columns([2, 1])

with col1:
    # THAY ĐỔI QUAN TRỌNG: Thêm accept_multiple_files=True
    uploaded_files = st.file_uploader(
        "Tải lên MỘT hoặc NHIỀU file ảnh (JPG, PNG) hoặc PDF...",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True  # <-- Cho phép tải nhiều file
    )

with col2:
    with st.expander("💡 Mẹo sử dụng", expanded=True):
        st.info("""
        - Bạn có thể kéo thả nhiều file vào đây cùng một lúc.
        - Kết quả của mỗi file sẽ được hiển thị trong một khung riêng biệt bên dưới.
        - Để có kết quả tốt nhất, hãy sử dụng ảnh rõ nét và chữ không bị mờ.
        """)

# Xử lý nếu người dùng đã tải file lên
if uploaded_files:
    st.markdown("---")
    st.header("Kết quả trích xuất")

    # Lặp qua từng file đã tải lên
    for uploaded_file in uploaded_files:
        # Sử dụng st.expander để tạo một khu vực riêng cho mỗi file
        with st.expander(f"Kết quả cho file: {uploaded_file.name}", expanded=True):
            with st.spinner(f"Đang xử lý file '{uploaded_file.name}'..."):
                file_bytes = uploaded_file.getvalue()
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                # Gọi hàm xử lý trung tâm
                text, error = process_file(file_bytes, file_extension)

            # Hiển thị kết quả hoặc lỗi
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
