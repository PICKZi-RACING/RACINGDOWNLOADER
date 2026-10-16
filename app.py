import sys
import os
import multiprocessing

# ป้องกันโปรแกรมเด้งหน้าต่างกากบาทแดง (Failed to execute script) เมื่อรันแบบ --noconsole
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

import customtkinter as ctk
import yt_dlp
import imageio_ffmpeg
import threading
import subprocess
from tkinter import filedialog, messagebox, Menu

# ตั้งค่าธีมเริ่มต้นให้เป็นโหมดมืด (Dark Mode)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# กำหนดฟอนต์หลักของโปรแกรมทุกส่วนเป็น Cordia New
FONT_MAIN = "Cordia New"


def get_resource_path(relative_path):
    """ดึงพาธไฟล์ทรัพยากร รองรับทั้งตอนรันปกติและตอนแปลงเป็น .exe (PyInstaller)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# พจนานุกรมคำแปลภาษา (TH / EN)
TRANSLATIONS = {
    'TH': {
        'title': 'RACINGDOWNLOADER',
        'url_label': 'วางลิงก์สื่อที่นี่:',
        'url_placeholder': 'https://www.youtube.com/watch?v=...',
        'paste_btn': 'วาง',
        'mode_label': 'ประเภทการดาวน์โหลด:',
        'video_radio': 'วิดีโอ (Video MP4)',
        'audio_radio': 'เสียงเท่านั้น (Audio)',
        'v_res_label': 'ความละเอียดวิดีโอ:',
        'v_fps_label': 'เฟรมเรต (FPS):',
        'a_type_label': 'ฟอร์แมตเสียง:',
        'a_quality_label': 'คุณภาพเสียง:',
        'path_prefix': 'ปลายทาง:',
        'select_folder': 'เลือกโฟลเดอร์',
        'download_btn': 'เริ่มดาวน์โหลด',
        'status_ready': 'พร้อมใช้งาน',
        'status_not_ready': 'ไม่พร้อมใช้งานโปรดอัพเดท',
        'status_checking': 'กำลังตรวจสอบระบบ...',
        'status_update_hint': 'กรุณากดปุ่มอัพเดทที่มุมซ้ายล่างก่อนใช้งาน',
        'update_btn': 'อัพเดท',
        'info_title': 'แพลตฟอร์มที่รองรับการดาวน์โหลด:',
        'info_text': (
            "สามารถคัดลอกลิงก์มาวางเพื่อดาวน์โหลดได้จากหลายแพลตฟอร์ม เช่น:\n"
            "- YouTube, YouTube Shorts, YouTube Music\n"
            "- Facebook (วิดีโอสาธารณะ และ Reels)\n"
            "- TikTok (วิดีโอและเสียง)\n"
            "- Instagram (Posts, Reels, Stories สาธารณะ)\n"
            "- X (Twitter), Twitch (Clips), SoundCloud, Vimeo, Dailymotion, Bilibili และเว็บไซต์อื่นๆ อีกมากมาย"
        ),
        'mp3_max': '320 kbps (คุณภาพสูงสุด)',
        'alert_warning': 'แจ้งเตือน',
        'alert_fill_url': 'กรุณากรอกลิงก์ที่ต้องการดาวน์โหลด',
        'alert_sys_not_ready': 'ระบบไม่พร้อมใช้งาน กรุณากดปุ่มอัพเดทที่มุมซ้ายล่างก่อน',
        'downloading': 'กำลังดาวน์โหลด',
        'converting': 'กำลังรวมไฟล์และประมวลผล...',
        'download_complete': 'ดาวน์โหลดเสร็จสมบูรณ์',
        'download_error': 'เกิดข้อผิดพลาดในการดาวน์โหลด',
        'success_title': 'สำเร็จ',
        'success_msg': 'ดาวน์โหลดและบันทึกไฟล์เรียบร้อยแล้ว',
        'error_title': 'ข้อผิดพลาด',
        'error_msg': 'ไม่สามารถดาวน์โหลดได้:\n',
        'preparing': 'กำลังเตรียมการดาวน์โหลด...',
        'ctx_cut': 'ตัด',
        'ctx_copy': 'คัดลอก',
        'ctx_paste': 'วาง',
        'ctx_select_all': 'เลือกทั้งหมด'
    },
    'EN': {
        'title': 'RACINGDOWNLOADER',
        'url_label': 'Paste media URL here:',
        'url_placeholder': 'https://www.youtube.com/watch?v=...',
        'paste_btn': 'Paste',
        'mode_label': 'Download Mode:',
        'video_radio': 'Video (MP4)',
        'audio_radio': 'Audio Only',
        'v_res_label': 'Video Quality:',
        'v_fps_label': 'Frame Rate (FPS):',
        'a_type_label': 'Audio Format:',
        'a_quality_label': 'Audio Quality:',
        'path_prefix': 'Destination:',
        'select_folder': 'Browse',
        'download_btn': 'Start Download',
        'status_ready': 'Ready to use',
        'status_not_ready': 'Not Ready - Please Update',
        'status_checking': 'Checking system...',
        'status_update_hint': 'Please click Update at bottom-left before downloading',
        'update_btn': 'Update',
        'info_title': 'Supported Platforms:',
        'info_text': (
            "Paste URLs to download media from supported platforms, including:\n"
            "- YouTube, YouTube Shorts, YouTube Music\n"
            "- Facebook (Public Videos & Reels)\n"
            "- TikTok (Video & Audio)\n"
            "- Instagram (Public Posts, Reels, Stories)\n"
            "- X (Twitter), Twitch (Clips), SoundCloud, Vimeo, Dailymotion, Bilibili and many more"
        ),
        'mp3_max': '320 kbps (Max Quality)',
        'alert_warning': 'Warning',
        'alert_fill_url': 'Please enter a URL to download.',
        'alert_sys_not_ready': 'System is not ready. Please click the Update button first.',
        'downloading': 'Downloading',
        'converting': 'Processing and merging files...',
        'download_complete': 'Download Completed',
        'download_error': 'Download Error Occurred',
        'success_title': 'Success',
        'success_msg': 'File downloaded and saved successfully.',
        'error_title': 'Error',
        'error_msg': 'Download failed:\n',
        'preparing': 'Preparing download...',
        'ctx_cut': 'Cut',
        'ctx_copy': 'Copy',
        'ctx_paste': 'Paste',
        'ctx_select_all': 'Select All'
    }
}


class MediaDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_lang = 'TH'
        self.is_system_ready = False
        self.is_checking_update = True

        self.title("RACINGDOWNLOADER")
        self.geometry("780x730")
        self.resizable(False, False)

        # โหลดไฟล์โลโก้ไอคอนของโปรแกรม (logo.ico)
        self.load_app_icon()

        # ตำแหน่งจัดเก็บไฟล์ดาวน์โหลด
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

        self.setup_ui()
        
        # ตรวจสอบและอัพเดทระบบเมื่อเริ่มโปรแกรม
        self.start_auto_update()

    def load_app_icon(self):
        """ตั้งค่าไอคอนมุมซ้ายบนของหน้าต่างโปรแกรม"""
        icon_candidates = ["logo.ico", "logo.icon", "logo.png"]
        for icon_name in icon_candidates:
            icon_path = get_resource_path(icon_name)
            if os.path.exists(icon_path):
                try:
                    self.iconbitmap(icon_path)
                    break
                except Exception:
                    pass

    def setup_ui(self):
        # แถบท็อปบาร์สำหรับเมนูปรับสไลด์เปลี่ยนภาษา (มุมซ้ายบน)
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=30, pady=(15, 0))

        # สวิตช์สไลด์เลือกภาษา
        self.lang_switch = ctk.CTkSegmentedButton(
            self.top_bar,
            values=["TH", "EN"],
            command=self.change_language,
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            width=100,
            height=28
        )
        self.lang_switch.set("TH")
        self.lang_switch.pack(side="left")

        # หัวข้อหลัก
        self.title_label = ctk.CTkLabel(
            self, 
            text="RACINGDOWNLOADER", 
            font=ctk.CTkFont(family=FONT_MAIN, size=28, weight="bold")
        )
        self.title_label.pack(pady=(5, 10))

        # กรอก URL
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.pack(fill="x", padx=30, pady=5)

        self.url_label = ctk.CTkLabel(
            self.url_frame, 
            text=TRANSLATIONS['TH']['url_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold")
        )
        self.url_label.pack(anchor="w", padx=15, pady=(8, 0))

        self.url_input_container = ctk.CTkFrame(self.url_frame, fg_color="transparent")
        self.url_input_container.pack(fill="x", padx=15, pady=(0, 12))

        self.url_entry = ctk.CTkEntry(
            self.url_input_container, 
            placeholder_text=TRANSLATIONS['TH']['url_placeholder'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # ปุ่มวางลิงก์ (Paste Button)
        self.btn_quick_paste = ctk.CTkButton(
            self.url_input_container,
            text=TRANSLATIONS['TH']['paste_btn'],
            command=self.quick_paste,
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            width=65,
            height=32,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.btn_quick_paste.pack(side="right")

        # ระบบคัดลอก/วาง
        self.enable_copy_paste(self.url_entry)

        # ตัวเลือกประเภทไฟล์ (Dropdown CTkOptionMenu)
        self.type_frame = ctk.CTkFrame(self)
        self.type_frame.pack(fill="x", padx=30, pady=8)

        self.mode_label = ctk.CTkLabel(
            self.type_frame, 
            text=TRANSLATIONS['TH']['mode_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=18, weight="bold")
        )
        self.mode_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.mode_option = ctk.CTkOptionMenu(
            self.type_frame,
            values=[
                TRANSLATIONS['TH']['video_radio'],
                TRANSLATIONS['TH']['audio_radio']
            ],
            command=self.toggle_options,
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            dropdown_font=ctk.CTkFont(family=FONT_MAIN, size=16),
            width=220
        )
        self.mode_option.set(TRANSLATIONS['TH']['video_radio'])
        self.mode_option.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        # เฟรมการตั้งค่าคุณภาพวิดีโอ (Video Options)
        self.video_options_frame = ctk.CTkFrame(self)
        self.video_options_frame.pack(fill="x", padx=30, pady=5)

        self.v_res_label = ctk.CTkLabel(
            self.video_options_frame, 
            text=TRANSLATIONS['TH']['v_res_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.v_res_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.v_res_option = ctk.CTkOptionMenu(
            self.video_options_frame,
            values=[
                "4K Ultra HD (2160p)", 
                "1080p Full HD", 
                "720p HD", 
                "480p"
            ],
            font=ctk.CTkFont(family=FONT_MAIN, size=16),
            dropdown_font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.v_res_option.set("1080p Full HD")
        self.v_res_option.grid(row=0, column=1, padx=15, pady=8)

        self.v_fps_label = ctk.CTkLabel(
            self.video_options_frame, 
            text=TRANSLATIONS['TH']['v_fps_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.v_fps_label.grid(row=0, column=2, padx=15, pady=8, sticky="w")

        self.v_fps_option = ctk.CTkOptionMenu(
            self.video_options_frame,
            values=["60 FPS", "30 FPS"],
            font=ctk.CTkFont(family=FONT_MAIN, size=16),
            dropdown_font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.v_fps_option.set("60 FPS")
        self.v_fps_option.grid(row=0, column=3, padx=15, pady=8)

        # เฟรมการตั้งค่าคุณภาพเสียง (Audio Options)
        self.audio_options_frame = ctk.CTkFrame(self)

        self.a_type_label = ctk.CTkLabel(
            self.audio_options_frame, 
            text=TRANSLATIONS['TH']['a_type_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.a_type_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.a_type_option = ctk.CTkOptionMenu(
            self.audio_options_frame,
            values=["MP3", "WAV"],
            command=self.update_audio_quality_options,
            font=ctk.CTkFont(family=FONT_MAIN, size=16),
            dropdown_font=ctk.CTkFont(family=FONT_MAIN, size=16),
            width=100
        )
        self.a_type_option.set("MP3")
        self.a_type_option.grid(row=0, column=1, padx=(5, 15), pady=8)

        self.a_quality_label = ctk.CTkLabel(
            self.audio_options_frame, 
            text=TRANSLATIONS['TH']['a_quality_label'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16)
        )
        self.a_quality_label.grid(row=0, column=2, padx=15, pady=8, sticky="w")

        self.a_quality_option = ctk.CTkOptionMenu(
            self.audio_options_frame,
            values=[TRANSLATIONS['TH']['mp3_max'], "192 kbps", "128 kbps"],
            font=ctk.CTkFont(family=FONT_MAIN, size=16),
            dropdown_font=ctk.CTkFont(family=FONT_MAIN, size=16),
            width=230
        )
        self.a_quality_option.set(TRANSLATIONS['TH']['mp3_max'])
        self.a_quality_option.grid(row=0, column=3, padx=(5, 15), pady=8)

        # การเลือกโฟลเดอร์ปลายทาง
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(fill="x", padx=30, pady=8)

        self.path_label = ctk.CTkLabel(
            self.path_frame, 
            text=f"{TRANSLATIONS['TH']['path_prefix']} {self.download_path}", 
            font=ctk.CTkFont(family=FONT_MAIN, size=16),
            anchor="w"
        )
        self.path_label.pack(side="left", padx=15, pady=8, fill="x", expand=True)

        self.path_btn = ctk.CTkButton(
            self.path_frame, 
            text=TRANSLATIONS['TH']['select_folder'], 
            command=self.select_folder,
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            width=110
        )
        self.path_btn.pack(side="right", padx=15, pady=8)

        # ปุ่มดาวน์โหลด
        self.download_btn = ctk.CTkButton(
            self, 
            text=TRANSLATIONS['TH']['download_btn'], 
            command=self.start_download_thread,
            font=ctk.CTkFont(family=FONT_MAIN, size=20, weight="bold"),
            height=42
        )
        self.download_btn.pack(fill="x", padx=30, pady=8)

        # แถบแสดงความคืบหน้า
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=30, pady=4)
        self.progress_bar.set(0)

        # ข้อความแสดงสถานะความคืบหน้า
        self.status_label = ctk.CTkLabel(
            self, 
            text=TRANSLATIONS['TH']['status_checking'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            text_color="#cccccc"
        )
        self.status_label.pack(pady=2)

        # รายละเอียดแพลตฟอร์มที่รองรับ
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="both", expand=True, padx=30, pady=(8, 5))

        self.info_title = ctk.CTkLabel(
            self.info_frame, 
            text=TRANSLATIONS['TH']['info_title'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold")
        )
        self.info_title.pack(anchor="w", padx=15, pady=(6, 0))

        self.info_label = ctk.CTkLabel(
            self.info_frame, 
            text=TRANSLATIONS['TH']['info_text'], 
            font=ctk.CTkFont(family=FONT_MAIN, size=15),
            justify="left",
            anchor="w"
        )
        self.info_label.pack(anchor="w", padx=15, pady=(0, 6))

        # แถบล่างสุดสำหรับสถานะระบบ (ซ้าย) และปุ่มเปลี่ยนธีม (ขวา)
        self.bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_bar.pack(fill="x", padx=30, pady=(0, 10))

        # ข้อความสถานะระบบ (ซ้ายล่าง)
        self.system_status_label = ctk.CTkLabel(
            self.bottom_bar,
            text=TRANSLATIONS['TH']['status_checking'],
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            text_color="#cccccc"
        )
        self.system_status_label.pack(side="left", padx=(0, 10))

        # ปุ่มอัพเดทสีเขียว
        self.update_btn = ctk.CTkButton(
            self.bottom_bar,
            text=TRANSLATIONS['TH']['update_btn'],
            command=self.start_auto_update,
            font=ctk.CTkFont(family=FONT_MAIN, size=16, weight="bold"),
            width=75,
            height=28,
            fg_color="#27ae60",
            hover_color="#219150",
            text_color="white"
        )

        # ปุ่มสลับธีมรูปพระอาทิตย์ (ขวาล่าง)
        self.theme_btn = ctk.CTkButton(
            self.bottom_bar,
            text="☀",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=16),
            width=32,
            height=32,
            corner_radius=16,
            fg_color=("gray75", "gray25"),
            text_color=("black", "gold"),
            hover_color=("gray65", "gray35")
        )
        self.theme_btn.pack(side="right")

    def quick_paste(self):
        """วางข้อความจากคลิปบอร์ดทันที"""
        try:
            text = self.clipboard_get()
            if text:
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, text.strip())
        except Exception:
            pass

    def enable_copy_paste(self, entry_widget):
        """ระบบจัดการคัดลอก/วาง และตรวจจับปุ่มกายภาพ Keycode 86 (Ctrl+อ) และ Win+V"""
        def paste_action(event=None):
            try:
                text = self.clipboard_get()
                if text:
                    try:
                        entry_widget.delete("sel.first", "sel.last")
                    except Exception:
                        pass
                    entry_widget.insert("insert", text)
            except Exception:
                pass
            return "break"

        def copy_action(event=None):
            try:
                text = entry_widget.selection_get()
                self.clipboard_clear()
                self.clipboard_append(text)
            except Exception:
                pass
            return "break"

        def cut_action(event=None):
            try:
                text = entry_widget.selection_get()
                self.clipboard_clear()
                self.clipboard_append(text)
                entry_widget.delete("sel.first", "sel.last")
            except Exception:
                pass
            return "break"

        def select_all_action(event=None):
            entry_widget.select_range(0, 'end')
            entry_widget.icursor('end')
            return "break"

        targets = [entry_widget]
        if hasattr(entry_widget, "_entry"):
            targets.append(entry_widget._entry)

        for target in targets:
            target.bind("<<Paste>>", paste_action)
            target.bind("<<Copy>>", copy_action)
            target.bind("<<Cut>>", cut_action)
            target.bind("<<SelectAll>>", select_all_action)

            def key_handler(event):
                is_ctrl = (event.state & 0x0004 != 0) or (event.state & 0x0008 != 0)
                if is_ctrl:
                    if event.keycode == 86 or str(event.keysym).lower() in ["v", "thai_o", "o"]:
                        return paste_action()
                    elif event.keycode == 67 or str(event.keysym).lower() in ["c", "thai_ae"]:
                        return copy_action()
                    elif event.keycode == 88 or str(event.keysym).lower() in ["x", "thai_pa"]:
                        return cut_action()
                    elif event.keycode == 65 or str(event.keysym).lower() in ["a", "thai_fo"]:
                        return select_all_action()

            target.bind("<Key>", key_handler)

        def show_context_menu(event):
            t = TRANSLATIONS[self.current_lang]
            current_mode = ctk.get_appearance_mode()
            
            bg_col = "#2b2b2b" if current_mode == "Dark" else "#f0f0f0"
            fg_col = "#ffffff" if current_mode == "Dark" else "#000000"

            menu = Menu(
                self, 
                tearoff=0, 
                font=(FONT_MAIN, 14),
                bg=bg_col,
                fg=fg_col,
                activebackground="#1f6aa5",
                activeforeground="#ffffff"
            )
            menu.add_command(label=t['ctx_cut'], command=cut_action)
            menu.add_command(label=t['ctx_copy'], command=copy_action)
            menu.add_command(label=t['ctx_paste'], command=paste_action)
            menu.add_separator()
            menu.add_command(label=t['ctx_select_all'], command=select_all_action)

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        for target in targets:
            target.bind("<Button-3>", show_context_menu)
            target.bind("<Button-2>", show_context_menu)

    def change_language(self, lang_choice):
        old_t = TRANSLATIONS[self.current_lang]
        is_video = (self.mode_option.get() == old_t['video_radio'])

        self.current_lang = lang_choice
        t = TRANSLATIONS[lang_choice]

        self.url_label.configure(text=t['url_label'])
        self.url_entry.configure(placeholder_text=t['url_placeholder'])
        self.btn_quick_paste.configure(text=t['paste_btn'])
        self.mode_label.configure(text=t['mode_label'])

        self.mode_option.configure(values=[t['video_radio'], t['audio_radio']])
        self.mode_option.set(t['video_radio'] if is_video else t['audio_radio'])

        self.v_res_label.configure(text=t['v_res_label'])
        self.v_fps_label.configure(text=t['v_fps_label'])
        self.a_type_label.configure(text=t['a_type_label'])
        self.a_quality_label.configure(text=t['a_quality_label'])
        self.path_label.configure(text=f"{t['path_prefix']} {self.download_path}")
        self.path_btn.configure(text=t['select_folder'])
        self.download_btn.configure(text=t['download_btn'])
        self.info_title.configure(text=t['info_title'])
        self.info_label.configure(text=t['info_text'])
        self.update_btn.configure(text=t['update_btn'])

        self.update_audio_quality_options()
        self.update_system_status_ui()

    def update_system_status_ui(self):
        t = TRANSLATIONS[self.current_lang]
        if self.is_checking_update:
            self.system_status_label.configure(text=t['status_checking'], text_color="#cccccc")
            self.status_label.configure(text=t['status_checking'], text_color="#cccccc")
            self.update_btn.pack_forget()
        elif self.is_system_ready:
            self.system_status_label.configure(text=t['status_ready'], text_color="#2ecc71")
            self.status_label.configure(text=t['status_ready'], text_color="#cccccc")
            self.update_btn.pack_forget()
        else:
            self.system_status_label.configure(text=t['status_not_ready'], text_color="#e74c3c")
            self.status_label.configure(text=t['status_update_hint'], text_color="#e74c3c")
            self.update_btn.pack(side="left")

    def toggle_options(self, choice=None):
        t = TRANSLATIONS[self.current_lang]
        if self.mode_option.get() == t['video_radio']:
            self.audio_options_frame.pack_forget()
            self.video_options_frame.pack(fill="x", padx=30, pady=5, after=self.type_frame)
        else:
            self.video_options_frame.pack_forget()
            self.audio_options_frame.pack(fill="x", padx=30, pady=5, after=self.type_frame)

    def update_audio_quality_options(self, choice=None):
        if choice is None:
            choice = self.a_type_option.get()

        t = TRANSLATIONS[self.current_lang]
        if choice == "MP3":
            self.a_quality_option.configure(values=[t['mp3_max'], "192 kbps", "128 kbps"])
            self.a_quality_option.set(t['mp3_max'])
        elif choice == "WAV":
            self.a_quality_option.configure(values=["24-bit / 96 kHz", "16-bit / 44.1 kHz"])
            self.a_quality_option.set("24-bit / 96 kHz")

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            t = TRANSLATIONS[self.current_lang]
            self.path_label.configure(text=f"{t['path_prefix']} {self.download_path}")

    def start_auto_update(self):
        self.is_checking_update = True
        self.update_system_status_ui()
        threading.Thread(target=self.auto_update_ytdlp, daemon=True).start()

    def auto_update_ytdlp(self):
        # ถ้าอยู่ในรูปแบบไฟล์ .exe (PyInstaller) ให้ข้ามการเรียก pip เพื่อป้องกันการเปิดตัวเองซ้ำวนลูป
        if getattr(sys, 'frozen', False):
            self.is_system_ready = True
            self.is_checking_update = False
            self.update_system_status_ui()
            return

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
            self.is_system_ready = True
        except Exception:
            self.is_system_ready = False
        finally:
            self.is_checking_update = False
            self.update_system_status_ui()

    def start_download_thread(self):
        t = TRANSLATIONS[self.current_lang]
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning(t['alert_warning'], t['alert_fill_url'])
            return

        if not self.is_system_ready:
            messagebox.showwarning(t['alert_warning'], t['alert_sys_not_ready'])
            return

        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text=t['preparing'], text_color="#3498db")

        threading.Thread(target=self.download_media, args=(url,), daemon=True).start()

    def progress_hook(self, d):
        t = TRANSLATIONS[self.current_lang]
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = downloaded_bytes / total_bytes
                self.progress_bar.set(percentage)
                speed = d.get('speed') or 0
                speed_mb = (speed / 1024 / 1024) if speed else 0
                self.status_label.configure(
                    text=f"{t['downloading']}: {percentage*100:.1f}% ({speed_mb:.2f} MB/s)",
                    text_color="#3498db"
                )
        elif d['status'] == 'finished':
            self.progress_bar.set(1.0)
            self.status_label.configure(text=t['converting'], text_color="#f39c12")

    def download_media(self, url):
        t = TRANSLATIONS[self.current_lang]
        try:
            selected_mode = self.mode_option.get()
            mode = "video" if selected_mode == t['video_radio'] else "audio"
            out_template = os.path.join(self.download_path, '%(title)s.%(ext)s')

            try:
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg_exe = None

            ydl_opts = {
                'outtmpl': out_template,
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'noplaylist': True,
                'overwrites': True,
                'retries': 10,
                'fragment_retries': 10,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['mweb', 'ios', 'android', 'web'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }

            if ffmpeg_exe:
                ydl_opts['ffmpeg_location'] = ffmpeg_exe

            if mode == "audio":
                a_type = self.a_type_option.get()
                a_quality = self.a_quality_option.get()
                ydl_opts['format'] = 'bestaudio/best'

                if a_type == "MP3":
                    kbps = "320" if "320" in a_quality else ("192" if "192" in a_quality else "128")
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': kbps,
                    }]
                elif a_type == "WAV":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                    }]
                    if "96 kHz" in a_quality:
                        ydl_opts['postprocessor_args'] = ['-ar', '96000', '-acodec', 'pcm_s24le']
                    else:
                        ydl_opts['postprocessor_args'] = ['-ar', '44100', '-acodec', 'pcm_s16le']

            else:  # Video mode
                res_str = self.v_res_option.get()
                fps_str = self.v_fps_option.get()

                max_res = 2160 if "4K" in res_str else (1080 if "1080p" in res_str else (720 if "720p" in res_str else 480))
                max_fps = 60 if "60" in fps_str else 30

                ydl_opts['format'] = f'bestvideo[height<={max_res}][fps<={max_fps}]+bestaudio/best[height<={max_res}]/best'
                ydl_opts['merge_output_format'] = 'mp4'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(text=t['download_complete'], text_color="#2ecc71")
            messagebox.showinfo(t['success_title'], t['success_msg'])

        except Exception as e:
            self.status_label.configure(text=t['download_error'], text_color="#e74c3c")
            messagebox.showerror(t['error_title'], f"{t['error_msg']}{str(e)}")

        finally:
            self.download_btn.configure(state="normal")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MediaDownloaderApp()
    app.mainloop()