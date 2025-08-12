# 1. IMPORT CÁC THƯ VIỆN CẦN THIẾT
import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

#========================================================================================
# HÀM HỖ TRỢ
#========================================================================================

def extract_text_from_image(image):
    """Hàm này nhận đầu vào là một đối tượng ảnh (PIL Image) và trả về văn bản được trích xuất."""
    return pytesseract.image_to_string(image, lang='vie')

#========================================================================================
# GIAO DIỆN ỨNG DỤNG STREAMLIT
#========================================================================================

# 2. THIẾT KẾ GIAO DIỆN
st.set_page_config(page_title="Trợ lý OCR Thông minh", page_icon="📄")

st.title("📄 Trợ lý OCR Thông minh")
st.write("Tải lên file ảnh (JPG, PNG) hoặc PDF để trích xuất văn bản Tiếng Việt.") # 

# Tạo một nơi để người dùng có thể tải file lên
uploaded_file = st.file_uploader(
    "Tải lên file ảnh hoặc PDF của bạn...",
    type=['pdf', 'png', 'jpg', 'jpeg'] # 
)


# 3. VIẾT LOGIC XỬ LÝ
# Chỉ thực hiện khi người dùng đã tải file lên
if uploaded_file is not None: # 
    extracted_text = ""
    # Hiển thị thông báo đang xử lý
    with st.spinner("Đang xử lý, vui lòng chờ..."): # 
        # Đọc dữ liệu từ file đã tải lên
        file_bytes = uploaded_file.getvalue()
        
        # Kiểm tra loại file dựa trên đuôi file
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf': # 
            try:
                # Chuyển đổi PDF từ bytes thành danh sách các ảnh
                images = convert_from_bytes(file_bytes) # 
                all_text = []
                # Lặp qua từng trang (ảnh) và trích xuất văn bản
                for img in images:
                    all_text.append(extract_text_from_image(img)) # 
                extracted_text = "\n\n".join(all_text) # [cite: 41]
            except Exception as e:
                st.error(f"Lỗi khi xử lý file PDF: {e}")
                
        elif file_extension in ['png', 'jpg', 'jpeg']: # 
            try:
                # Mở file ảnh trực tiếp
                image = Image.open(io.BytesIO(file_bytes)) # 
                extracted_text = extract_text_from_image(image) # 
            except Exception as e:
                st.error(f"Lỗi khi xử lý file ảnh: {e}")
                
    # 4. HIỂN THỊ KẾT QUẢ
    if extracted_text:
        st.header("Kết quả trích xuất:")
        # Hiển thị văn bản trong một vùng văn bản có thể cuộn
        st.text_area("Văn bản:", extracted_text, height=400) # 
        
        # Thêm nút để tải về kết quả
        st.download_button(
            label="Tải kết quả xuống (.txt)", # 
            data=extracted_text.encode('utf-8'),
            file_name=f"ket_qua_{uploaded_file.name}.txt",
            mime="text/plain"
        )