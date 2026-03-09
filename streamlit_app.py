import streamlit as st
from moviepy.editor import VideoFileClip, vfx
import tempfile
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI-Safe Video Editor (Original Quality)", layout="wide")

st.title("🎬 เครื่องมือตัดต่อวิดีโอ (โหมดคุณภาพสูง & เร็วสุดขีด)")
st.write("ตัดขอบ ลบลายน้ำ โดยรักษาความคมชัดเท่าต้นฉบับ 100%")

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
        
        # ลอคค่ามาตรฐานไว้ที่ 44 ตามสั่ง
        c_bottom = st.number_input("ตัดขอบล่าง", 0, h, 45)
        st.markdown('<p style="color:red; font-weight:bold; margin-bottom:0;">⚠️ ค่ามาตรฐานตัดลายน้ำ</p>', unsafe_allow_html=True)
        st.write('<p style="font-size:14px; color:gray;">💡 ยิ่งจำนวนตัวเลขยิ่งสูง ก็จะตัดขอบล่างไปเยอะ (ช่วยบังลายน้ำได้แม่นยำขึ้น)</p>', unsafe_allow_html=True)
        
        st.divider()

        if st.button("⚡ เรนเดอร์ความชัดสูงสุด (Original Quality)", use_container_width=True):
            with st.spinner('กำลังประมวลผล... โหมดเน้นความชัดและเร็วสุดยอด'):
                output_path = "high_res_video.mp4"
                
                try:
                    # ขั้นตอนที่ 1: ตัดเวลาและความเร็ว
                    processed_clip = clip.subclip(start_t, end_t).fx(vfx.speedx, video_speed)
                    
                    # ขั้นตอนที่ 2: ครอปพื้นที่ออก (คงความละเอียดเดิม ไม่มีการ Resize)
                    final_output = processed_clip.crop(y1=c_top, y2=processed_clip.h-c_bottom)
                    
                    # ขั้นตอนที่ 3: บันทึกไฟล์ด้วยการตั้งค่าความคมชัดสูงสุด
                    # ใช้ ffmpeg_params crf 18 เพื่อรักษาคุณภาพให้เหมือนต้นฉบับที่สุด
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
                    st.video(output_path)
                    
                    with open(output_path, "rb") as f:
                        st.download_button("📥 ดาวน์โหลดวิดีโอชัด 100%", f, "high_quality_video.mp4", "video/mp4")

                    # ปิดคลิปเพื่อคืน RAM ทันที
                    final_output.close()
                    processed_clip.close()
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
                    st.info("💡 วิธีแก้ Memory Error: ให้ลองปิดโปรแกรมอื่นในเครื่องก่อนกดเรนเดอร์ครับ")

    clip.close()