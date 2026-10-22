"""Automated 1-Minute Demo Video Generator with AI Voice for Bill & Document Sloth."""

import os
import sys
import time
import subprocess
from gtts import gTTS
from playwright.sync_api import sync_playwright

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

VOICEOVER_TEXT = (
    "Welcome to Bill and Document Sloth, built for Hacktoberfest Week 3 Slow and Steady. "
    "Managing paperwork is exhausting: cryptic filenames, hidden payment due dates, and manual spreadsheets. "
    "With Bill and Document Sloth, you simply drop your documents once and relax. "
    "Our local AI instantly parses utility bills, receipts, and warranties, extracting providers, exact amounts, and deadlines without any data leaving your computer. "
    "Click Review to inspect the original PDF side-by-side with extracted fields. You can even run deep reasoning with Google Gemma model. "
    "Approve with one click, and your document is organized into clean folders with smart standardized filenames. "
    "On the dashboard, Prior Labs TabPFN-3.5 forecasts next month utility spending and detects cost anomalies, while upcoming deadlines are proactively tracked. "
    "Stop sorting paperwork. Start living. Bill and Document Sloth is open-source on GitHub."
)

def generate_audio(output_audio_path: str):
    print("[1/3] Generating AI voiceover with gTTS...")
    tts = gTTS(text=VOICEOVER_TEXT, lang='en', tld='com')
    tts.save(output_audio_path)
    print(f"      Voiceover generated at {output_audio_path}")

def record_walkthrough(output_dir: str):
    print("[2/3] Recording interactive browser walkthrough using Edge...")
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=output_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()

        # Part 1: Open Dashboard (0 to 10s)
        page.goto("http://127.0.0.1:8000")
        page.wait_for_timeout(7000)

        # Part 2: Click Load Demo Pack (10 to 22s)
        page.evaluate("handleGenerateDemo()")
        page.wait_for_timeout(10000)

        # Part 3: Go to Documents and Review (22 to 36s)
        page.evaluate("switchTab('documents')")
        page.wait_for_timeout(4000)

        # Open Review modal for first bill
        page.evaluate("openReviewModal(1)")
        page.wait_for_timeout(10000)

        # Part 4: Run Gemma Reasoning (36 to 48s)
        page.evaluate("handleGemmaExtract()")
        page.wait_for_timeout(9000)

        # Close Review modal (48 to 56s)
        page.evaluate("closeReviewModal()")
        page.wait_for_timeout(3000)

        # Part 5: Show Upcoming Deadlines (56 to 64s)
        page.evaluate("switchTab('deadlines')")
        page.wait_for_timeout(10000)

        # Part 6: Show Privacy & Sponsor Showcase (64 to 75s)
        page.evaluate("switchTab('privacy')")
        page.wait_for_timeout(12000)

        context.close()
        browser.close()
        print("      Browser walkthrough recorded.")

def merge_video_audio(video_dir: str, audio_path: str, output_final_mp4: str):
    print("[3/3] Merging video with AI voiceover using FFmpeg...")
    files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".webm")]
    if not files:
        raise FileNotFoundError("No recorded video found in " + video_dir)
    raw_video = files[0]

    cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_final_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"\nSUCCESS! 1-Minute Demo Video generated at:\n{output_final_mp4}")

def main():
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    temp_video_dir = os.path.join(assets_dir, "temp_record")
    temp_audio_path = os.path.join(assets_dir, "temp_voiceover.mp3")
    final_video_path = os.path.join(assets_dir, "demo_video.mp4")

    # Start FastAPI server if not running
    server_process = None
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:8000/api/dashboard", timeout=2)
        print("Server is active on port 8000.")
    except Exception:
        print("Starting local server on port 8000...")
        server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
        time.sleep(3)

    try:
        generate_audio(temp_audio_path)
        record_walkthrough(temp_video_dir)
        merge_video_audio(temp_video_dir, temp_audio_path, final_video_path)
    finally:
        if server_process:
            server_process.terminate()
        # Clean up temporary raw video folder and voiceover file
        try:
            import shutil
            if os.path.exists(temp_video_dir):
                shutil.rmtree(temp_video_dir)
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
