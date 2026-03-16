# ============================================
# 🤖 Анна PRO v6.2 — Self-Improving Edition
# ПОВНЕ меню з 9 режимами повернуто!
# ============================================

# ---------------- IMPORTS ----------------
import streamlit as st
import requests
import os
import base64
import json
import io
from datetime import datetime
from pathlib import Path
from gtts import gTTS

# ---------------- CONFIG ----------------
BASE_PATH = Path(__file__).parent
OLLAMA_HOST = "127.0.0.1:11434"
TIMEOUT = 120
HISTORY_FILE = BASE_PATH / "anna_history.json"
PROGRESS_FILE = BASE_PATH / "anna_progress.json"

# 🔍 Пошук медіа
ANNA_VIDEO_PATH = ANNA_IMAGE_PATH = None
for f in BASE_PATH.iterdir():
    if f.is_file() and any(x in f.name.lower() for x in ['anna', 'girl']):
        if f.suffix.lower() in ['.mp4', '.avi', '.mov']:
            ANNA_VIDEO_PATH = str(f)
            break
        elif f.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            ANNA_IMAGE_PATH = str(f)

# ---------------- 💾 MEMORY & LEARNING ----------------
def load_json_file(filepath, default):
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default

def save_json_file(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"⚠️ Помилка: {e}")

def load_history():
    data = load_json_file(HISTORY_FILE, {'history': [], 'mode': '🧑‍🏫 Обучение', 'last_model': None})
    return data.get('history', []), data.get('mode', '🧑‍🏫 Обучение'), data.get('last_model', None)

def save_history(history, mode, model):
    save_json_file(HISTORY_FILE, {
        'history': history[-100:],
        'mode': mode,
        'last_model': model,
        'updated': datetime.now().isoformat()
    })

def load_user_progress():
    return load_json_file(PROGRESS_FILE, {
        'current_level': 'Початківець',
        'question_count': 0,
        'learning_streak': 0,
        'last_session': None,
        'ratings': {'thumbs_up': 0, 'thumbs_down': 0}
    })

def save_user_progress(progress):
    save_json_file(PROGRESS_FILE, progress)

def rate_answer(message_idx, rating):
    progress = load_user_progress()
    if rating == 'thumbs_up':
        progress['ratings']['thumbs_up'] += 1
        st.toast("👍 Дякую! Радий що допоміг!", icon="👍")
    else:
        progress['ratings']['thumbs_down'] += 1
        st.toast("👎 Вибачте! Покращусь наступного разу.", icon="👎")
    save_user_progress(progress)

def adjust_user_level(question):
    progress = load_user_progress()
    progress['question_count'] += 1
    today = datetime.now().date().isoformat()
    if progress['last_session'] != today:
        progress['learning_streak'] += 1
        progress['last_session'] = today
    save_user_progress(progress)

# ---------------- 🎤 VOICE ----------------
def text_to_speech(text, lang='ru'):
    try:
        lang_map = {'Українська': 'uk', 'Русский': 'ru', 'English': 'en', 'Deutsch': 'de'}
        text = text[:400] if len(text) > 400 else text
        tts = gTTS(text=text, lang=lang_map.get(lang, 'ru'), slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except:
        return None

# ---------------- 📚 MODES (ПОВНЕ МЕНЮ - 9 РЕЖИМІВ!) ----------------
MODES = {
    "🇩🇪 German Coach": {
        "name": "German Coach",
        "subjects": ["A1 Початківець", "A2 Елементарний", "B1 Середній", "B2 Вище середнього", "C1 Просунутий"],
        "prompt": "You are Anna, a professional German teacher. Explain in {lang}. Level: {level}. Keep it simple and practical."
    },
    "🧑‍🏫 Обучение": {
        "name": "Обучение",
        "subjects": ["Python & Django", "SQL и базы данных", "Машинное обучение", "Анализ данных", "Web разработка", "DevOps & Docker"],
        "prompt": "Ты - опытный преподаватель. Объясняй сложные концепции шаг за шагом, используй примеры и аналогии. Отвечай на {lang}."
    },
    "📊 Аналитика": {
        "name": "Аналитика",
        "subjects": ["Анализ данных", "Визуализация", "Статистика", "Бизнес-аналитика", "Data Mining"],
        "prompt": "Ты - эксперт по анализу данных. Анализируй информацию, находи закономерности, предлагай инсайты. Отвечай на {lang}."
    },
    "💻 Программирование": {
        "name": "Программирование",
        "subjects": ["Python", "JavaScript", "Java", "C++", "Web Dev", "API", "Algorithms"],
        "prompt": "Ты - senior разработчик. Предоставляй чистый, оптимизированный код с объяснениями. Отвечай на {lang}."
    },
    "📈 Data Science": {
        "name": "Data Science",
        "subjects": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "MLOps", "Statistics"],
        "prompt": "Ты - data scientist. Помогай с машинным обучением, статистикой, визуализацией данных. Отвечай на {lang}."
    },
    "🗣️ Подготовка к собеседованию": {
        "name": "Подготовка к собеседованию",
        "subjects": ["Технические вопросы", "Алгоритмы", "System Design", "Поведенческие вопросы", "HR вопросы"],
        "prompt": "Ты - карьерный консультант. Готовь к техническим и поведенческим собеседованиям. Задавай вопросы и давай обратную связь. Отвечай на {lang}."
    },
    "📝 Оптимизация резюме": {
        "name": "Оптимизация резюме",
        "subjects": ["CV Review", "LinkedIn", "Cover Letter", "Portfolio", "Personal Branding"],
        "prompt": "Ты - HR-эксперт. Анализируй резюме, предлагай улучшения, готовь к подаче на позиции. Отвечай на {lang}."
    },
    "🔍 Код-ревью": {
        "name": "Код-ревью",
        "subjects": ["Python", "JavaScript", "SQL", "Code Quality", "Security", "Performance"],
        "prompt": "Ты - технический лидер. Анализируй код на качество, безопасность, производительность. Давай конкретные рекомендации. Отвечай на {lang}."
    },
    "❓ Вопрос-ответ": {
        "name": "Вопрос-ответ",
        "subjects": ["IT общее", "Карьера", "Обучение", "Технологии", "Другое"],
        "prompt": "Ты - полезный ассистент. Отвечай на вопросы точно и информативно. Отвечай на {lang}."
    }
}

# ---------------- STYLES ----------------
def inject_custom_css():
    st.markdown("""
    <style>
    .stApp { font-family: 'Inter', sans-serif; }
    .chat-u { background:linear-gradient(135deg,#667eea,#764ba2); color:white; padding:1rem 1.4rem; border-radius:1.2rem 1.2rem 0.3rem 1.2rem; margin:0.7rem 0; max-width:85%; margin-left:auto; }
    .chat-a { background:#f0f2f6; padding:1rem 1.4rem; border-radius:1.2rem 1.2rem 1.2rem 0.3rem; margin:0.7rem 0; max-width:85%; border-left:5px solid #667eea; }
    .typing { display:inline-flex; gap:5px; padding:0.5rem; }
    .typing span { width:10px; height:10px; background:#667eea; border-radius:50%; animation:bounce 1.4s infinite; }
    .typing span:nth-child(2){animation-delay:0.2s}
    .typing span:nth-child(3){animation-delay:0.4s}
    @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-10px)} }
    @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
    .input-section { background:white; padding:1.5rem; border-radius:1rem; box-shadow:0 2px 10px rgba(0,0,0,0.1); margin:1.5rem 0; }
    .hint { background:#f0fdf4; border-left:4px solid #10b981; padding:1rem; border-radius:0.5rem; margin:1rem 0; color:#065f46; }
    .progress-card { background:linear-gradient(135deg,#667eea20,#764ba220); padding:1rem; border-radius:0.8rem; margin:0.5rem 0; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def check_ollama():
    try:
        r = requests.get(f"http://{OLLAMA_HOST}/api/tags", timeout=5)
        return r.status_code == 200, [m['name'] for m in r.json().get('models', [])]
    except:
        return False, []

def ask_ollama(prompt, model, temp, tokens):
    try:
        r = requests.post(f"http://{OLLAMA_HOST}/api/generate",
            json={"model":model,"prompt":prompt,"stream":False,
                  "options":{"temperature":temp,"num_predict":tokens,"num_ctx":2048}},
            timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("response", "").strip()
        return f"❌ Код {r.status_code}"
    except:
        return "⏰ Тайм-аут"

# ---------------- UI ----------------
EMOTIONS = {"neutral": ("👋", "Привіт! 💫"), "thinking": ("🤔", "Думаю..."), 
            "happy": ("😊", "Готово!"), "empathetic": ("🤗", "Разом впораємось!")}

def show_anna(emotion="neutral"):
    emoji, phrase = EMOTIONS.get(emotion, EMOTIONS["neutral"])
    
    if ANNA_VIDEO_PATH:
        try:
            with open(ANNA_VIDEO_PATH, "rb") as f:
                video_b64 = base64.b64encode(f.read()).decode()
            html = f'''<div style="text-align:center;padding:1rem;">
                <div style="width:250px;height:250px;margin:0 auto;border-radius:50%;overflow:hidden;border:5px solid #667eea;box-shadow:0 0 50px #667eea80;animation:pulse 3s ease-in-out infinite;">
                    <video autoplay loop muted playsinline style="width:100%;height:100%;object-fit:cover;">
                        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                    </video>
                </div>
                <div style="margin-top:1rem;font-style:italic;color:#666;">{emoji} {phrase}</div>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)
        except:
            st.markdown('<div style="text-align:center;font-size:5rem;padding:3rem;">🎬</div>', unsafe_allow_html=True)
    elif ANNA_IMAGE_PATH:
        try:
            with open(ANNA_IMAGE_PATH, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            ext = "png" if ANNA_IMAGE_PATH.endswith(".png") else "jpeg"
            html = f'''<div style="text-align:center;padding:1rem;">
                <div style="width:250px;height:250px;margin:0 auto;border-radius:50%;overflow:hidden;border:5px solid #667eea;box-shadow:0 0 50px #667eea80;animation:pulse 3s ease-in-out infinite;">
                    <img src="data:image/{ext};base64,{img_b64}" style="width:100%;height:100%;object-fit:cover;">
                </div>
                <div style="margin-top:1rem;font-style:italic;color:#666;">{emoji} {phrase}</div>
            </div>'''
            st.markdown(html, unsafe_allow_html=True)
        except:
            st.markdown('<div style="text-align:center;font-size:5rem;padding:3rem;">🖼️</div>', unsafe_allow_html=True)
    else:
        html = f'''<div style="text-align:center;padding:1rem;">
            <div style="width:250px;height:250px;margin:0 auto;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;border:5px solid #667eea;box-shadow:0 0 50px #667eea80;animation:pulse 3s ease-in-out infinite;">
                <div style="font-size:5rem;">🤖</div>
            </div>
            <div style="margin-top:1rem;font-style:italic;color:#666;">{emoji} {phrase}</div>
        </div>'''
        st.markdown(html, unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
def render_sidebar():
    with st.sidebar:
        show_anna(st.session_state.emotion)
        st.title("🛡️ Панель")
        
        progress = load_user_progress()
        st.markdown("### 📊 Ваш прогрес")
        st.markdown(f"""
        <div class="progress-card">
            <div>📚 Рівень: <b>{progress['current_level']}</b></div>
            <div>❓ Питань: {progress['question_count']}</div>
            <div>🔥 Серія: {progress['learning_streak']} днів</div>
            <div>👍 Успіхів: {progress['ratings']['thumbs_up']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ok, models = check_ollama()
        if not ok:
            st.error("❌ Ollama не працює")
            st.stop()
        st.success(f"✅ Ollama: {len(models)} моделей")
        
        st.markdown("---")
        st.markdown("## 🎯 Режим роботи")
        
        mode_keys = list(MODES.keys())
        mode = st.selectbox(" ", mode_keys, label_visibility="collapsed",
                           index=mode_keys.index(st.session_state.mode) if st.session_state.mode in mode_keys else 0)
        st.session_state.mode = mode
        
        mode_info = MODES[mode]
        st.markdown(f"**{mode_info['name']}**")
        subject = st.selectbox("📚 Предметная область", mode_info["subjects"])
        st.session_state.current_subject = subject
        lang = st.radio("🌐 Мова", ["Українська","Русский","English","Deutsch"], index=1)
        
        if mode == "🇩🇪 German Coach":
            level = st.select_slider("📊 Рівень", ["A1","A2","B1","B2","C1"], value="A1")
        else:
            level = st.select_slider("📊 Досвід", ["Початківець","Середній","Досвідчений"], value="Середній")
        
        st.markdown("---")
        model = st.selectbox("🤖 Модель", models, label_visibility="collapsed",
                           index=models.index(st.session_state.last_model) if st.session_state.last_model in models else 0)
        st.session_state.last_model = model
        
        temp = st.slider("🎲 Креативність", 0.1, 1.0, 0.3, 0.1)
        tokens = st.slider("📝 Довжина", 100, 800, 400, 50)
        
        st.markdown("---")
        voice_enabled = st.checkbox("🔊 Озвучувати", value=st.session_state.get('voice_enabled', False))
        st.session_state.voice_enabled = voice_enabled
        
        st.markdown("---")
        if st.button("🗑️ Очистити чат", use_container_width=True):
            st.session_state.history = []
            st.session_state.emotion = "neutral"
            st.rerun()
        
        return mode, subject, lang, level, model, temp, tokens

# ---------------- MAIN ----------------
def main():
    st.set_page_config(page_title="🤖 Анна PRO v6.2", page_icon="🤖", layout="wide")
    inject_custom_css()
    
    saved_history, saved_mode, saved_model = load_history()
    
    for k,v in {"history":saved_history,"emotion":"neutral","mode":saved_mode,
                "last_model":saved_model,"voice_enabled":False,"current_subject":"Python & Django"}.items():
        if k not in st.session_state:
            st.session_state[k] = v
    
    st.markdown("""
    <div style="text-align:center;padding:2rem;background:linear-gradient(135deg,#667eea15,#764ba215);border-radius:1.5rem;margin-bottom:2rem;">
        <h1 style="margin:0;color:#667eea;font-size:2.5rem;">🤖 Анна PRO</h1>
        <p style="margin:0.5rem 0 0;opacity:0.7;">v6.2 • 9 режимів + Self-Improving</p>
    </div>
    """, unsafe_allow_html=True)
    
    mode, subject, lang, level, model, temp, tokens = render_sidebar()
    
    mode_name = MODES[mode]["name"]
    st.markdown(f"### {mode_name} — {subject} | {level}")
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### ✏️ Ваше запитання:")
    
    q = st.text_area("Напишіть запитання:", height=100, key="input_area",
                    placeholder="Опишіть ваше запитання детально...", label_visibility="collapsed")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        send_clicked = st.button("🚀 Надіслати", type="primary", use_container_width=True, disabled=not q.strip())
    with col2:
        st.button("🎤 Голос", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if send_clicked:
        ts = datetime.now().strftime("%H:%M")
        st.session_state.history.append({"u": q, "t": ts, "mode": mode, "subject": subject})
        st.session_state.emotion = "thinking"
        st.rerun()
    
    if st.session_state.emotion == "thinking" and st.session_state.history:
        last = st.session_state.history[-1]
        if "a" not in last:
            st.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
            st.caption("🤔 Анна думає...")
            
            prompt = f"{MODES[mode]['prompt'].format(lang=lang, level=level)}\n\nTopic: {subject}\n\nQuestion: {last['u']}"
            answer = ask_ollama(prompt, model, temp, tokens)
            last["a"] = answer
            
            adjust_user_level(last['u'])
            
            if st.session_state.voice_enabled and answer and len(answer) > 20:
                st.markdown("### 🔊 Озвучення:")
                audio_data = text_to_speech(answer, lang)
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
            
            st.session_state.emotion = "happy" if len(answer) > 20 else "empathetic"
            save_history(st.session_state.history, mode, model)
            st.rerun()
    
    if st.session_state.history:
        st.markdown("### 📜 Історія діалогу")
        for i, msg in enumerate(reversed(st.session_state.history[-10:])):
            idx = len(st.session_state.history) - 1 - i
            if "u" in msg:
                st.markdown(f'<div class="chat-u"><small>⏰ {msg["t"]}</small><br>{msg["u"]}</div>', unsafe_allow_html=True)
            if "a" in msg:
                st.markdown(f'<div class="chat-a"><small>⏰ {msg["t"]}</small><br>{msg["a"]}</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("👍", key=f"up_{idx}"):
                        rate_answer(idx, 'thumbs_up')
                        st.rerun()
                with col2:
                    if st.button("👎", key=f"down_{idx}"):
                        rate_answer(idx, 'thumbs_down')
                        st.rerun()
                
                if st.button(f"🔊", key=f"voice_{idx}"):
                    audio = text_to_speech(msg["a"], lang)
                    if audio:
                        st.audio(audio, format='audio/mp3')
        
        st.markdown('''
        <div class="hint">
            💡 <strong>Продовжуйте діалог:</strong> Напишіть нове запитання і натисніть "🚀 Надіслати"<br>
            📊 <strong>Анна вдосконалюється:</strong> Оцінюйте відповіді 👍/👎
        </div>
        ''', unsafe_allow_html=True)
    
    st.caption(f"🤖 Анна PRO v6.2 | `{model}` | 💙 9 режимів + Self-Improving | 💾 {HISTORY_FILE.name}")

if __name__ == "__main__":
    main()