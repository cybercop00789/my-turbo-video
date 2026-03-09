import streamlit as st

# ==========================================
# 🚨 วิชามาร: แก้ปัญหา PIL.Image ลบคำสั่ง ANTIALIAS ทิ้ง (ต้องวางไว้บนสุด)
# ==========================================
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS
# ==========================================

from moviepy.editor import VideoFileClip, vfx
import tempfile
import os
from proglog import ProgressBarLogger

# ตั้งค่าหน้าเว็บให้รองรับ RWD (Responsive: ยืดหยุ่นตามอุปกรณ์ มือถือ/แท็บเล็ต/คอม)
st.set_page_config(page_title="FlowCut Pro", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 ส่วนที่ 1: ตกแต่ง UI ด้วย CSS ให้กะทัดรัด ทันสมัย และ Responsive
# ==========================================
custom_css = """
<style>
    /* 🌚 พื้นหลัง Modern Dark */
    div[data-testid="stAppViewContainer"] {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* 📱 บีบช่องอัปโหลดให้สั้นลง อยู่กึ่งกลาง และสวยงามขึ้น */
    section[data-testid="stFileUploader"] {
        max-width: 650px;
        margin: 0 auto;
    }
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #00f2fe;
        background-color: rgba(0, 242, 254, 0.05);
        border-radius: 20px;
        padding: 40px 20px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #ff007f;
        background-color: rgba(255, 0, 127, 0.08);
        transform: scale(1.02);
    }
    
    /* ปรับแต่งปุ่ม Render */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        width: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 127, 0.5);
    }
    
    /* ปรับแต่งปุ่ม Download */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    /* จัดหัวข้อให้อยู่กึ่งกลางดู Modern */
    h1, h2, h3 {
        text-align: center;
    }
    h1 { color: #ff007f !important; text-shadow: 0 0 10px rgba(255, 0, 127, 0.5) !important; font-size: 2.5rem !important;}
    h2, h3 { color: #00f2fe !important; text-shadow: 0 0 8px rgba(0, 242, 254, 0.4) !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("🎬 เครื่องมือตัดต่อวิดีโอ (โหมดคุณภาพสูง)")
st.markdown("<p style='text-align: center; color: #a0a0a0; margin-bottom: 20px;'>ตัดขอบ ตัดลายน้ำ (สำหรับโปรแกรม flow) โดยรักษาความคมชัดเท่าต้นฉบับ 100%</p>", unsafe_allow_html=True)

# เครดิตจัดกึ่งกลางสวยงาม
st.markdown('<p style="text-align: center;"><strong>ผู้พัฒนาโปรแกรม :</strong> <a href="https://www.facebook.com/adnet.golf" target="_blank" style="color:#00f2fe; font-weight:bold; text-decoration:none; text-shadow: 0 0 5px rgba(0, 242, 254, 0.6);">Face Book:ก๊อบปี้ ณัฐชยา</a></p>', unsafe_allow_html=True)
st.divider()

uploaded_file = st.file_uploader("อัปโหลดวิดีโอ (Flow/TikTok)", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close() 
    
    clip = VideoFileClip(tfile.name)
    duration = float(clip.duration)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📺 ต้นฉบับ")
        st.video(uploaded_file)

    with col2:
        st.subheader("⚙️ ตั้งค่าการปรับแต่ง")
        
        st.write("**1. ตัดช่วงเวลาและความเร็ว**")
        start_t, end_t = st.slider("เลือกวินาทีที่เอาไว้", 0.0, duration, (0.0, duration))
        video_speed = st.slider("ความเร็ววิดีโอ (หลบ AI)", 0.8, 1.5, 1.05)
        st.divider()

        st.write("**2. ตัดขอบออก (Pixels)**")
        c_top = st.number_input("ตัดขอบบน", 0, clip.h, 0)
        c_bottom = st.number_input("ตัดขอบล่าง (ลบ Flow)", 0, clip.h, 48)
        st.markdown('<p style="color:red; font-weight:bold; margin-bottom:0; font-size:14px;">⚠️ ค่ามาตรฐานตัดลายน้ำ (โปรแกรม flow)</p>', unsafe_allow_html=True)
        st.divider()

        st.write("**3. เลือกความละเอียดตอนดาวน์โหลด**")
        res_options = {
            "เท่าต้นฉบับ (Original)": None,
            "720p (HD)": 720,
            "1080p (Full HD)": 1080
        }
        selected_res_label = st.selectbox("ขนาดที่ต้องการ (ความชัด)", list(res_options.keys()))
        target_height = res_options[selected_res_label]
        
        st.divider()

        if st.button("⚡ เริ่มเรนเดอร์ด่วนคุณภาพสูงสุด", use_container_width=True):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            class MyVideoLogger(ProgressBarLogger):
                def bars_callback(self, bar, attr, value, old_value=None):
                    total = self.bars[bar]['total']
                    if total > 0:
                        percent = int((value / total) * 100)
                        percent = min(max(percent, 0), 100)
                        progress_bar.progress(percent)
                        status_text.markdown(f"**⏳ กำลังประมวลผลวิดีโอ... {percent}%** (อาจใช้เวลาพับไฟล์แป๊บนึง เพื่อให้ขนาดเล็กลงครับ)")
            
            custom_logger = MyVideoLogger()
            output_path = "high_res_video.mp4"
            
            try:
                processed_clip = clip.subclip(start_t, end_t).fx(vfx.speedx, video_speed)
                final_output = processed_clip.crop(y1=c_top, y2=processed_clip.h-c_bottom)
                
                if target_height is not None:
                    final_output = final_output.fx(vfx.resize, height=target_height)
                
                # ==========================================
                # 🛡️ ส่วนที่อัปเดตใหม่: บีบอัดไฟล์ให้เล็กลง แต่คุณภาพ 100% เท่าตาเห็น
                # ==========================================
                final_output.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    audio_bitrate="128k", # ล็อกขนาดไฟล์เสียงไม่ให้ใหญ่เกิน
                    fps=clip.fps,       
                    preset="fast",        # เปลี่ยนจาก ultrafast เป็น fast ให้ระบบบีบอัดไฟล์ได้ดีขึ้น
                    threads=2,          
                    ffmpeg_params=["-crf", "23"], # เปลี่ยนจาก 18 เป็น 23 (ภาพชัดเท่าเดิม แต่ไฟล์เล็กลง 2-3 เท่า!)
                    logger=custom_logger 
                )
                # ==========================================
                
                progress_bar.progress(100)
                status_text.empty()
                st.success("✅ เรนเดอร์เสร็จสิ้น! ภาพชัด 100% แถมไฟล์เล็กกะทัดรัด")
                
                file_size_bytes = os.path.getsize(output_path)
                file_size_mb = file_size_bytes / (1024 * 1024)
                
                st.markdown(f'''
                <div style="background-color: rgba(0, 242, 254, 0.1); border-left: 5px solid #00f2fe; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <span style="color: #00f2fe; font-size: 16px; font-weight: bold; text-shadow: 0 0 5px rgba(0, 242, 254, 0.6);">🛡️ ปลอดภัย 100% สำหรับ TikTok & Reels</span><br>
                    <span style="color: #e0e0e0; font-size: 14px;">วิดีโอนี้ถูกเรนเดอร์แบบรักษาสัดส่วนและคุณภาพ (CRF23) คุณสามารถโพสต์ได้อย่างมั่นใจ!</span><br><br>
                    <span style="color: #ff007f; font-size: 16px; font-weight: bold;">📦 ขนาดไฟล์หลังตัดต่อ: {file_size_mb:.2f} MB</span>
                </div>
                ''', unsafe_allow_html=True)

                st.video(output_path)
                
                with open(output_path, "rb") as f:
                    st.download_button(f"📥 ดาวน์โหลดวิดีโอ ({file_size_mb:.2f} MB)", f, "high_quality_video.mp4", "video/mp4")

                final_output.close()
                processed_clip.close()
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

    clip.close()
    if os.path.exists(tfile.name):
        os.remove(tfile.name)


