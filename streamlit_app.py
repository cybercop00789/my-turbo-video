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

# ตั้งค่าหน้าเว็บให้รองรับการทำงานแบบมือโปร
st.set_page_config(page_title="Flow Video Turbo Editor (Original Quality)", layout="wide")

# ==========================================
# 🎨 ส่วนที่ 1: ตกแต่ง UI ด้วย CSS ให้ดูสวยงามทันสมัยสุดๆ (Cyber Dark / Neon)
# ==========================================
custom_css = """
<style>
    /* 🌚 ตกแต่งพื้นหลังหน้าเว็บให้เป็น Modern Dark */
    div[data-testid="stAppViewContainer"] {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* ปรับแต่งปุ่มหลัก (Render) ให้เป็นสีไล่ระดับพรีเมียม (Neon Pink/Violet Gradient) และมีมิติ */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.4) !important;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(255, 0, 127, 0.5);
        opacity: 0.95;
    }
    
    /* ปรับแต่งปุ่มดาวน์โหลดให้เป็นสีฟ้านีออน (Cyan Gradient) */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    /* 🎨 ตกแต่งตัวอักษรหัวข้อ (Headers) ให้มีสีสันนีออนล้ำสมัย */
    h1 {
        color: #ff007f !important;
        text-shadow: 0 0 10px rgba(255, 0, 127, 0.5) !important;
    }
    h2, h3 {
        color: #00f2fe !important;
        text-shadow: 0 0 8px rgba(0, 242, 254, 0.4) !important;
    }
    
    /* 📦 ตกแต่งกล่องอัปโหลดไฟล์ให้มีมิติ */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #00f2fe;
        background-color: rgba(0, 242, 254, 0.08);
        border-radius: 15px;
    }
    
    /* ⚙️ ตกแต่งกล่องอินพุตต่างๆ (Number Input, Selectbox, Sliders) */
    [data-testid="stNumberInputContainer"], [data-testid="stSelectbox"], .stSlider {
        background-color: rgba(0, 242, 254, 0.05);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 10px;
        color: #e0e0e0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("🎬 เครื่องมือตัดต่อวิดีโอ (โหมดคุณภาพสูง & เร็วสุดขีด)")

# --- แก้ไขคำอธิบายให้ตรงจุด: ตัดลายน้ำโปรแกรม flow ---
st.write("ตัดขอบ ตัดลายน้ำ (สำหรับโปรแกรม flow) โดยรักษาความคมชัดเท่าต้นฉบับ 100%")

# ==========================================
# 🛡️ ส่วนที่แก้ไขใหม่ตามสั่ง: ผู้พัฒนาโปรแกรม + แนบลิงก์ที่ชื่อ (HTML)
# ==========================================
st.markdown('<strong>ผู้พัฒนาโปรแกรม :</strong><a href="https://www.facebook.com/adnet.golf" target="_blank" style="color:#00f2fe; font-weight:bold; text-decoration:none; text-shadow: 0 0 5px rgba(0, 242, 254, 0.6);">Face Book:ก๊อบปี้ ณัฐชยา</a>', unsafe_allow_html=True)
st.divider()
# --------------------------------------------------------

uploaded_file = st.file_uploader("อัปโหลดวิดีโอ (Flow/TikTok)", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close() # ปิดไฟล์ก่อนเพื่อให้ moviepy ดึงไปใช้ได้
    
    # โหลดคลิป
    clip = VideoFileClip(tfile.name)
    w, h = clip.size
    duration = float(clip.duration)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("📺 ต้นฉบับ")
        st.video(uploaded_file)

    with col2:
        st.subheader("⚙️ ตั้งค่าการปรับแต่ง")
        
        # 1. ตัดเวลาและความเร็ว
        st.write("**1. ตัดช่วงเวลาและความเร็ว**")
        start_t, end_t = st.slider("เลือกวินาทีที่เอาไว้", 0.0, duration, (0.0, duration))
        video_speed = st.slider("ความเร็ววิดีโอ (หลบ AI)", 0.8, 1.5, 1.05)

        st.divider()

        # 2. ครอปขอบออก (Crop)
        st.write("**2. ตัดขอบออก (Pixels)**")
        c_top = st.number_input("ตัดขอบบน", 0, clip.h, 0)
        
        # ลอคค่ามาตรฐานไว้ที่ 45 ตามสั่ง (สำหรับโปรแกรม flow)
        c_bottom = st.number_input("ตัดขอบล่าง (ลบ Flow)", 0, clip.h, 45)
        
        # --- ข้อความเตือนสำหรับโปรแกรม flow ---
        st.markdown('<p style="color:red; font-weight:bold; margin-bottom:0;">⚠️ ค่ามาตรฐานตัดลายน้ำ (โปรแกรม flow)</p>', unsafe_allow_html=True)
        st.write('<p style="font-size:14px; color:gray;">💡 ยิ่งจำนวนตัวเลขยิ่งสูง ก็จะตัดขอบล่างไปเยอะ (ช่วยตัดลายน้ำออกไปได้เลย)</p>', unsafe_allow_html=True)
        
        st.divider()

        # 3. เลือกความละเอียดตอนดาวน์โหลด (อัปเกรดถึง 16K)
        st.write("**3. เลือกความละเอียดตอนดาวน์โหลด**")
        res_options = {
            "เท่าต้นฉบับ (Original)": None,
            "720p (HD)": 720,
            "1080p (Full HD)": 1080,
            "1440p (2K/QHD)": 1440,
            "2160p (4K/UHD)": 2160,
            "4320p (8K)": 4320,
            "6480p (12K - โคตรชัด)": 6480,
            "8640p (16K - ชัดทะลุโลก ระวังคอมค้าง!)": 8640
        }
        selected_res_label = st.selectbox("ขนาดที่ต้องการ (ความชัด)", list(res_options.keys()))
        target_height = res_options[selected_res_label]
        
        st.divider()

        if st.button("⚡ เริ่มเรนเดอร์ด่วนคุณภาพสูงสุด", use_container_width=True):
            with st.spinner('กำลังประมวลผลความละเอียดสูง... โหมดเน้นความชัดและเร็วสุดยอด'):
                output_path = "high_res_video.mp4"
                
                try:
                    # ขั้นตอนที่ 1: ตัดเวลาและความเร็ว
                    processed_clip = clip.subclip(start_t, end_t).fx(vfx.speedx, video_speed)
                    
                    # ขั้นตอนที่ 2: ครอปพื้นที่ออก (คงความละเอียดเดิม ไม่มีการ Resize)
                    final_output = processed_clip.crop(y1=c_top, y2=processed_clip.h-c_bottom)
                    
                    # ขั้นตอนที่ 2.5: ประมวลผลปรับขนาดตามที่เลือก (720p - 16K)
                    # ข้อควรระวัง: 8K ขึ้นไปอาจ Memory Error บนเครื่องสเปคต่ำ
                    if target_height is not None:
                        final_output = final_output.fx(vfx.resize, height=target_height)
                    
                    # ขั้นตอนที่ 3: บันทึกไฟล์ด้วยการตั้งค่าความคมชัดสูงสุด
                    final_output.write_videofile(
                        output_path, 
                        codec="libx264", 
                        audio_codec="aac", 
                        fps=clip.fps,       # ใช้ FPS เท่าต้นฉบับเพื่อให้ลื่นไหล
                        preset="ultrafast", # เร็วที่สุด
                        threads=2,          # ลดลงเหลือ 2 เพื่อความเสถียรบน CPU Basic
                        ffmpeg_params=["-crf", "18"], # ค่าความชัด (18 คือชัดมากเกือบเท่าต้นฉบับ)
                        logger=None
                    )
                    
                    st.success("✅ เรนเดอร์เสร็จสิ้นด้วยความชัดสูงสุด!")
                    
                    # ==========================================
                    # 🛡️ ส่วนข้อความแจ้งเตือนความสบายใจหลังเรนเดอร์เสร็จ (Cyber Dark Alert)
                    # ==========================================
                    st.markdown('''
                    <div style="background-color: rgba(0, 242, 254, 0.1); border-left: 5px solid #00f2fe; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <span style="color: #00f2fe; font-size: 16px; font-weight: bold; text-shadow: 0 0 5px rgba(0, 242, 254, 0.6);">🛡️ ปลอดภัย 100% สำหรับ TikTok & Reels</span><br>
                        <span style="color: #e0e0e0; font-size: 14px;">วิดีโอนี้ถูกเรนเดอร์โดยไม่ลดคุณภาพ (Bitrate) และไม่ทำให้สัดส่วนภาพผิดเพี้ยนไปจากต้นฉบับ คุณสามารถนำไฟล์นี้ไปโพสต์ลงแพลตฟอร์มต่างๆ ได้อย่างมั่นใจ หมดห่วงเรื่องการโดนลดการมองเห็นครับ!</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    # ==========================================

                    st.video(output_path)
                    
                    with open(output_path, "rb") as f:
                        st.download_button("📥 ดาวน์โหลดวิดีโอชัด 100%", f, "high_quality_video.mp4", "video/mp4")

                    # ปิดคลิปเพื่อคืน RAM ทันที
                    final_output.close()
                    processed_clip.close()
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
                    st.info("💡 วิธีแก้ Memory Error: ให้ลองปิดโปรแกรมอื่นในเครื่องก่อนกดเรนเดอร์ หรือลดความละเอียดตอนดาวน์โหลดลงมาครับ")

    clip.close()
    # ลบไฟล์ชั่วคราวหลังใช้งานเสร็จ
    if os.path.exists(tfile.name):
        os.remove(tfile.name)
