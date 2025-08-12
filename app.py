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
    except Exception as e:
        # Bỏ qua lỗi nếu không thể resize
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
            for img in images:
                optimized_img = resize_image(img)
                all_text.append(pytesseract.image_to_string(optimized_img, lang='vie'))
            extracted_text = "\n\n--- Hết trang ---\n\n".join(all_text)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            image = Image.open(io.BytesIO(file_bytes))
            optimized_img = resize_image(image)
            extracted_text = pytesseract.image_to_string(optimized_img, lang='vie')
        return extracted_text, None  # Trả về text và không có lỗi
    except Exception as e:
        return None, f"Đã xảy ra lỗi trong quá trình xử lý: {e}" # Trả về không có text và thông báo lỗi

# ========================================================================================
# GIAO DIỆN CHÍNH CỦA ỨNG DỤNG
# ========================================================================================

st.title("📄 Trợ lý OCR Thông minh")
st.write("Trích xuất văn bản Tiếng Việt từ file ảnh hoặc PDF một cách nhanh chóng và hiệu quả.")

# Khởi tạo session_state nếu chưa có
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'last_uploaded_filename' not in st.session_state:
    st.session_state.last_uploaded_filename = None

# Cột cho phần tải lên và hướng dẫn
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Tải lên file ảnh (JPG, PNG) hoặc PDF của bạn...",
        type=['pdf', 'png', 'jpg', 'jpeg']
    )

with col2:
    with st.expander("💡 Mẹo sử dụng", expanded=False):
        st.info("""
        - Để có kết quả tốt nhất, hãy sử dụng ảnh rõ nét, chữ không bị mờ, nghiêng.
        - Giới hạn tải lên là 200MB, nhưng file nhỏ hơn sẽ được xử lý nhanh hơn.
        - Đối với PDF nhiều trang, ứng dụng sẽ nối kết quả của tất cả các trang lại.
        """)

# Xử lý file nếu có file mới được tải lên
if uploaded_file is not None:
    # Chỉ xử lý nếu file này chưa được xử lý trước đó
    if uploaded_file.name != st.session_state.last_uploaded_filename:
        with st.spinner(f"Đang xử lý file '{uploaded_file.name}', vui lòng chờ..."):
            file_bytes = uploaded_file.getvalue()
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Gọi hàm xử lý trung tâm
            text, error = process_file(file_bytes, file_extension)
            
            # Lưu kết quả vào session_state
            st.session_state.extracted_text = text
            st.session_state.error_message = error
            st.session_state.last_uploaded_filename = uploaded_file.name
        
        # Hiển thị thông báo thành công hoặc thất bại
        if st.session_state.error_message:
            st.error(st.session_state.error_message)
        else:
            st.success(f"Đã xử lý thành công file '{uploaded_file.name}'!")


# Hiển thị kết quả nếu có
if st.session_state.extracted_text:
    st.markdown("---")
    st.header("Kết quả trích xuất")
    st.text_area("Văn bản:", st.session_state.extracted_text, height=400, key="result_text")

    # Chia cột cho các nút hành động
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])

    with btn_col1:
        st.download_button(
            label="📥 Tải kết quả xuống",
            data=st.session_state.extracted_text.encode('utf-8'),
            file_name=f"ket_qua_{st.session_state.last_uploaded_filename}.txt",
            mime="text/plain"
        )
    
    with btn_col2:
        # Nút xóa kết quả
        if st.button("🔄 Xóa & làm lại"):
            st.session_state.extracted_text = None
            st.session_state.error_message = None
            st.session_state.last_uploaded_filename = None
            # Dùng st.experimental_rerun() để tải lại trang ngay lập tức
            st.experimental_rerun()
