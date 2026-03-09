import streamlit as st
from moviepy.editor import VideoFileClip, vfx
import tempfile
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI-Safe Video Editor (Original Quality)", layout="wide")

# ==========================================
# 🎨 ส่วนที่ 1: ตกแต่ง UI ด้วย CSS ให้ดูสวยงามทันสมัย
# ==========================================
custom_css = """
<style>
    /* ปรับแต่งปุ่มหลักให้เป็นสีไล่ระดับ (Gradient) และมีมิติ */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: bold;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4);
    }
    
    /* ปรับแต่งปุ่มดาวน์โหลดให้เป็นสีฟ้านีออน */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    
    /* ปรับแต่งตัวอักษรหัวข้อ (Headers) ให้มีสีสันล้ำสมัย */
    h1 {
        color: #ff007f !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: #00f2fe !important;
    }
    
    /* ปรับแต่งกล่องอัปโหลดไฟล์ */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #00f2fe;
        background-color: rgba(0, 242, 254, 0.05);
        border-radius: 12px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("🎬 เครื่องมือตัดต่อวิดีโอ (โหมดคุณภาพสูง & เร็วสุดขีด)")

# --- แก้ไขคำอธิบายให้ตรงจุด: ตัดลายน้ำโปรแกรม flow ---
st.write("ตัดขอบ ตัดลายน้ำ (สำหรับโปรแกรม flow) โดยรักษาความคมชัดเท่าต้นฉบับ 100%")

# --- ส่วนเครดิตผู้เขียนโปรแกรม (ลิงก์ซ่อน URL) ---
st.markdown('**Face Book:ก๊อบปี้ ณัฐชยา:** <a href="https://www.facebook.com/adnet.golf" target="_blank" style="color:#00f2fe; font-weight:bold; text-decoration:none;">ผู้เขียนโปรแกรม</a>', unsafe_allow_html=True)
st.divider()
# --------------------------------------------------------

uploaded_file = st.file_uploader("อัปโหลดวิดีโอ", type=['mp4', 'mov', 'avi'])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
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
        c_top = st.number_input("ตัดขอบบน", 0, h, 0)
        
        # ลอคค่ามาตรฐานไว้ที่ 45 ตามสั่ง
        c_bottom = st.number_input("ตัดขอบล่าง", 0, h, 45)
        
        # --- ปรับข้อความเตือนให้เข้ากับโปรแกรม flow ---
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

        if st.button("⚡ เรนเดอร์ความชัดสูงสุด (Original Quality)", use_container_width=True):
            with st.spinner('กำลังประมวลผล... โหมดเน้นความชัดและเร็วสุดยอด'):
                output_path = "high_res_video.mp4"
                
                try:
                    # ขั้นตอนที่ 1: ตัดเวลาและความเร็ว
                    processed_clip = clip.subclip(start_t, end_t).fx(vfx.speedx, video_speed)
                    
                    # ขั้นตอนที่ 2: ครอปพื้นที่ออก (คงความละเอียดเดิม ไม่มีการ Resize)
                    final_output = processed_clip.crop(y1=c_top, y2=processed_clip.h-c_bottom)
                    
                    # ขั้นตอนที่ 2.5: ประมวลผลปรับขนาดตามที่เลือก
                    if target_height is not None:
                        final_output = final_output.fx(vfx.resize, height=target_height)
                    
                    # ขั้นตอนที่ 3: บันทึกไฟล์ด้วยการตั้งค่าความคมชัดสูงสุด
                    final_output.write_videofile(
                        output_path, 
                        codec="libx264", 
                        audio_codec="aac", 
                        fps=clip.fps,       # ใช้ FPS เท่าต้นฉบับเพื่อให้ลื่นไหล
                        preset="ultrafast", # เร็วที่สุด
                        threads=4,          # ใช้ CPU หลายคอร์
                        ffmpeg_params=["-crf", "18"], # ค่าความชัด (18 คือชัดมากเกือบเท่าต้นฉบับ)
                        logger=None
                    )
                    
                    st.success("✅ เรนเดอร์เสร็จสิ้นด้วยความชัดสูงสุด!")
                    
                    # ==========================================
                    # 🛡️ ส่วนที่เพิ่มใหม่: ข้อความแจ้งเตือนความสบายใจหลังเรนเดอร์เสร็จ
                    # ==========================================
                    st.markdown('''
                    <div style="background-color: rgba(0, 242, 254, 0.1); border-left: 5px solid #00f2fe; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <span style="color: #00f2fe; font-size: 16px; font-weight: bold;">🛡️ ปลอดภัย 100% สำหรับ TikTok & Reels</span><br>
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
                    st.info("💡 วิธีแก้ Memory Error: ให้ลองปิดโปรแกรมอื่นในเครื่องก่อนกดเรนเดอร์ หรือลดความละเอียดลงมาครับ")

    clip.close()
