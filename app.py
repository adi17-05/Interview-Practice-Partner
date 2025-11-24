from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import streamlit as st
from streamlit_mic_recorder import mic_recorder  # type: ignore

from interview_partner.agents.orchestrator import Orchestrator
from interview_partner.agents.memory_agent import MemoryAgent
from interview_partner.data.rubrics import RUBRIC_DESCRIPTIONS, RUBRIC_TITLES
from interview_partner.core.audio import transcribe_audio_bytes, text_to_speech_bytes


APP_TITLE = "Interview Practice Partner"


def _init_session_state() -> None:
    if "view" not in st.session_state:
        st.session_state["view"] = "🚀 Pre-flight"
    if "orchestrator" not in st.session_state:
        st.session_state["orchestrator"] = None
    if "current_question" not in st.session_state:
        st.session_state["current_question"] = None
    if "session_summary" not in st.session_state:
        st.session_state["session_summary"] = None
    if "tts_cache" not in st.session_state:
        st.session_state["tts_cache"] = {}
    if "transcribed_answer" not in st.session_state:
        st.session_state["transcribed_answer"] = ""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = ""


def _sidebar() -> None:
    with st.sidebar:
        st.title("Navigation")
        options = ["🚀 Pre-flight", "🎙️ Interview", "📼 Review"]
        try:
            idx = options.index(st.session_state["view"])
        except ValueError:
            idx = 0

        view = st.radio(
            "View",
            options=options,
            index=idx,
            label_visibility="collapsed",
        )
        st.session_state["view"] = view

        st.markdown("---")
        
        # CSS is injected in main() now to ensure it covers everything including header
        
        st.markdown("### Rubric")
        
        rubric_html = '<div class="rubric-grid">'
        for k, desc in RUBRIC_DESCRIPTIONS.items():
            title = RUBRIC_TITLES.get(k, k)
            rubric_html += f"""<div class="rubric-card">
<div class="rubric-title"><span>🔹</span> {title}</div>
<div class="rubric-desc">{desc}</div>
</div>"""
        rubric_html += "</div>"
        
        st.markdown(rubric_html, unsafe_allow_html=True)


def _render_preflight() -> None:
    st.header("🚀 Pre-Flight Dashboard")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="input-label">User ID</div>', unsafe_allow_html=True)
        user_id = st.text_input(
            "User ID",
            value=st.session_state.get("user_id", ""),
            placeholder="e.g. harshitha.candidate01",
            label_visibility="collapsed",
        )
        st.session_state["user_id"] = user_id.strip() or "anonymous"

        st.markdown('<div class="input-label">Target Role</div>', unsafe_allow_html=True)
        role = st.selectbox(
            "Target role",
            ["Software Engineer", "Sales", "Customer Support"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown('<div class="input-label">Interviewer Tone</div>', unsafe_allow_html=True)
        tone = st.radio(
            "Interviewer tone",
            options=["Friendly", "Neutral", "Grilling"],
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown('<div class="input-label">Mode</div>', unsafe_allow_html=True)
        mode_label = st.radio(
            "Mode",
            ["Normal Interview", "Weak Spot Drill"],
            horizontal=True,
            label_visibility="collapsed",
        )
        mode = "drill" if "Drill" in mode_label else "normal"

        st.markdown('<div class="input-label">Questions per Session</div>', unsafe_allow_html=True)
        max_questions = st.slider(
            "Questions per session",
            min_value=5,
            max_value=8,
            value=6,
            label_visibility="collapsed",
        )

        st.session_state["max_questions"] = max_questions

        if st.button("🎙️ Start Session", type="primary"):
            orch = Orchestrator(
                user_id=st.session_state["user_id"],
                role=role,
                mode=mode,
                tone=tone,
                max_questions=max_questions,
            )
            first_question = orch.start_interview()

            st.session_state["orchestrator"] = orch
            st.session_state["current_question"] = first_question
            st.session_state["view"] = "🎙️ Interview"
            st.session_state["transcribed_answer"] = ""
            st.session_state["tts_cache"] = {}

            st.rerun()

    with col_right:
        st.markdown('<div class="weak-spot-col">', unsafe_allow_html=True)
        st.subheader("Weak-spot overview")

        if st.session_state["user_id"]:
            mem = MemoryAgent(user_id=st.session_state["user_id"])
            weak_spots = mem.get_weak_spots()
        else:
            weak_spots = []

        if weak_spots:
            st.write("Based on your past sessions, focus on:")
            for topic in weak_spots:
                st.markdown(f"- ✅ **{topic}**")
        else:
            st.write("No stored history yet. Complete a session to build your weak-spot map.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Optional: resume & JD upload could plug into a future Resume RAG service.")


def _play_question_audio(question: str) -> None:
    if not question:
        return

    tts_cache: Dict[str, Optional[bytes]] = st.session_state["tts_cache"]

    if question not in tts_cache:
        audio_bytes = text_to_speech_bytes(question)
        tts_cache[question] = audio_bytes
        st.session_state["tts_cache"] = tts_cache

    audio_bytes = tts_cache.get(question)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav", start_time=0)


def _render_interview_room() -> None:
    from pathlib import Path
    
    orch: Optional[Orchestrator] = st.session_state.get("orchestrator")
    if orch is None:
        st.warning("Start a session from the Pre-flight view first.")
        return

    question = st.session_state.get("current_question") or orch.current_question
    if not question:
        question = orch.start_interview()
        st.session_state["current_question"] = question

    # Question Overlay
    st.markdown(f"""
        <div class="question-overlay">
            <h3>🎯 Current Question</h3>
            <p>{question}</p>
        </div>
    """, unsafe_allow_html=True)

    # Google Meet-style Video Grid using components.html for proper rendering
    import streamlit.components.v1 as components
    
    video_grid_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; padding: 0; background: #202124; }
            .video-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                padding: 20px;
            }
            .video-container {
                position: relative;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                height: 400px;
                overflow: hidden;
            }
            .ai-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .candidate-container {
                background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            }
            .ai-avatar {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 64px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            }
            .participant-label {
                position: absolute;
                bottom: 12px;
                left: 12px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                backdrop-filter: blur(10px);
            }
            .status-indicator {
                position: absolute;
                top: 12px;
                right: 12px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #34a853;
                box-shadow: 0 0 8px rgba(52, 168, 83, 0.6);
            }
            #candidate-video {
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: none;
            }
            .webcam-placeholder {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #9aa0a6;
                text-align: center;
            }
            .camera-toggle {
                position: absolute;
                top: 12px;
                right: 12px;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(0, 0, 0, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                cursor: pointer;
                font-size: 20px;
                backdrop-filter: blur(10px);
                transition: all 0.2s ease;
                z-index: 10;
            }
            .camera-toggle:hover {
                background: rgba(0, 0, 0, 0.8);
                transform: scale(1.1);
            }
        </style>
    </head>
    <body>
        <div class="video-grid">
            <div class="video-container ai-container">
                <div class="ai-avatar">🤖</div>
                <div class="participant-label">AI Interviewer</div>
                <div class="status-indicator"></div>
            </div>
            
            <div class="video-container candidate-container">
                <video id="candidate-video" autoplay muted playsinline></video>
                <div id="webcam-placeholder" class="webcam-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 80px; height: 80px; margin-bottom: 16px; opacity: 0.6;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p id="camera-status">Initializing camera...</p>
                </div>
                <button id="camera-toggle" class="camera-toggle" onclick="toggleCamera()">📹</button>
                <div class="participant-label">You</div>
            </div>
        </div>
        
        <script>
        (function() {
            console.log("Webcam initialization script loaded");
            let localStream = null;
            let videoElement = null;
            let cameraEnabled = true;

            async function initializeWebcam() {
                console.log("Attempting to initialize webcam...");
                const statusEl = document.getElementById("camera-status");
                
                try {
                    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                        throw new Error("Camera not supported in this browser");
                    }
                    
                    console.log("Requesting camera access...");
                    localStream = await navigator.mediaDevices.getUserMedia({
                        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "user" },
                        audio: false
                    });
                    
                    console.log("Camera access granted!");
                    videoElement = document.getElementById("candidate-video");
                    
                    if (videoElement) {
                        videoElement.srcObject = localStream;
                        videoElement.style.display = "block";
                        await videoElement.play();
                        console.log("Video playing");
                        
                        const placeholder = document.getElementById("webcam-placeholder");
                        if (placeholder) placeholder.style.display = "none";
                    }
                    
                    return true;
                } catch (error) {
                    console.error("Camera error:", error);
                    let errorMessage = "Unable to access camera";
                    
                    if (error.name === "NotAllowedError") {
                        errorMessage = "Camera access denied. Please allow permissions.";
                    } else if (error.name === "NotFoundError") {
                        errorMessage = "No camera found.";
                    } else if (error.name === "NotReadableError") {
                        errorMessage = "Camera in use by another app.";
                    } else {
                        errorMessage = error.message;
                    }
                    
                    if (statusEl) statusEl.textContent = errorMessage;
                    return false;
                }
            }

            window.toggleCamera = function() {
                console.log("Toggle camera clicked");
                if (localStream) {
                    const videoTrack = localStream.getVideoTracks()[0];
                    if (videoTrack) {
                        cameraEnabled = !cameraEnabled;
                        videoTrack.enabled = cameraEnabled;
                        
                        const button = document.getElementById("camera-toggle");
                        if (button) {
                            button.innerHTML = cameraEnabled ? "📹" : "📹❌";
                            button.style.background = cameraEnabled ? "rgba(0, 0, 0, 0.6)" : "rgba(234, 67, 53, 0.8)";
                        }
                        
                        if (videoElement) {
                            videoElement.style.opacity = cameraEnabled ? "1" : "0.3";
                        }
                    }
                } else {
                    console.log("No stream, initializing...");
                    initializeWebcam();
                }
            };

            setTimeout(() => initializeWebcam(), 500);
        })();
        </script>
    </body>
    </html>
    """
    
    components.html(video_grid_html, height=460)

    # Audio Player for Question with AI spotlight
    with st.expander("🔊 Play question as audio", expanded=False):
        # Trigger AI speaking animation when audio starts
        st.markdown("""
            <script>
            // Start AI speaking animation when expander is opened
            if (window.startAISpeaking) {
                window.startAISpeaking();
                // Stop after 5 seconds (adjust based on typical question length)
                setTimeout(function() {
                    if (window.stopAISpeaking) window.stopAISpeaking();
                }, 5000);
            }
            </script>
        """, unsafe_allow_html=True)
        _play_question_audio(question)

    st.markdown("---")

    # Answer Section
    st.subheader("🎤 Your Answer")

    audio_dict = mic_recorder(
        start_prompt="🎙️ Record answer",
        stop_prompt="⏹️ Stop recording",
        key="answer_recorder",
    )

    if audio_dict is not None:
        audio_bytes: bytes = audio_dict["bytes"]  # type: ignore[index]
        st.audio(audio_bytes, format="audio/wav")
        if st.button("📝 Transcribe recording"):
            with st.spinner("Transcribing..."):
                try:
                    transcript = transcribe_audio_bytes(audio_bytes)
                except Exception as e:  # pragma: no cover - runtime only
                    st.error(f"Transcription failed: {e}")
                    transcript = ""
                st.session_state["transcribed_answer"] = transcript

    answer_text = st.text_area(
        "Or type your answer here",
        value=st.session_state.get("transcribed_answer", ""),
        height=160,
        key="answer_text_area",
        placeholder="Share your thoughts, experiences, and insights..."
    )

    # Lightweight pacing / length indicator
    if answer_text:
        word_count = len(answer_text.split())
        if word_count < 30:
            st.info("💡 Hint: very short answer. Consider adding more context and concrete details.")
        elif word_count > 220:
            st.warning("⚠️ Hint: long answer. Consider being more concise and structured.")

    col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
    with col_submit2:
        if st.button("➡️ Submit Answer", type="primary", use_container_width=True):
            if not answer_text.strip():
                st.warning("Please record or type an answer before submitting.")
                return

            with st.spinner("Evaluating and generating next question..."):
                next_q = orch.submit_answer(answer_text.strip())
                st.session_state["current_question"] = next_q
                st.session_state["transcribed_answer"] = ""
                st.session_state["orchestrator"] = orch  # persist updates

            if orch.finished:
                with st.spinner("Finalizing session summary..."):
                    summary = orch.finalize_session()
                    st.session_state["session_summary"] = summary
                    st.session_state["view"] = "📼 Review"
                st.success("Interview complete! Moving to review.")
                st.rerun()
            else:
                st.rerun()


def _render_review() -> None:
    st.header("📼 Game Tape Review")

    summary: Optional[Dict[str, Any]] = st.session_state.get("session_summary")
    orch: Optional[Orchestrator] = st.session_state.get("orchestrator")

    if summary is None and orch is not None:
        latest = orch.get_latest_session()
        summary = latest
        st.session_state["session_summary"] = summary

    if summary is None:
        st.info("No session summary available yet. Complete an interview first.")
        return

    st.subheader("Overall summary")
    st.write(summary.get("summary_text", ""))

    cols = st.columns(2)
    with cols[0]:
        st.markdown("#### Weak spot topics")
        weak_topics = summary.get("weak_spot_topics", [])
        if weak_topics:
            for t in weak_topics:
                st.markdown(f"- ⚠️ **{t}**")
        else:
            st.write("No weak spots recorded (nice job!).")

    with cols[1]:
        st.markdown("#### Strength topics")
        strengths = summary.get("strength_topics", [])
        if strengths:
            for t in strengths:
                st.markdown(f"- 💪 **{t}**")
        else:
            st.write("No specific strengths extracted.")

    st.markdown("---")

    evaluations: List[Dict[str, Any]] = summary.get("evaluations", [])
    st.subheader("Per-question breakdown")

    for idx, ev in enumerate(evaluations, start=1):
        with st.expander(f"Q{idx}: {ev.get('question', '')[:80]}..."):
            st.markdown(f"**Question**: {ev.get('question', '')}")
            st.markdown(f"**Your answer**:\n\n{ev.get('answer', '')}")

            scores = ev.get("scores", {})
            if scores:
                st.markdown("**Scores (0–10)**")
                score_cols = st.columns(len(scores))
                for (k, v), col in zip(scores.items(), score_cols):
                    with col:
                        st.metric(k, v)

            st.markdown("**Strengths**")
            strengths = ev.get("strengths", []) or ["—"]
            st.write(", ".join(strengths))

            st.markdown("**Weak spots**")
            weak_spots = ev.get("weak_spots", []) or ["—"]
            st.write(", ".join(weak_spots))

            st.markdown("**Coach comments**")
            st.write(ev.get("comments", ""))

    st.markdown("---")

    show_json = st.checkbox("🔍 Show scoring rubric JSON (debug / explainability)")
    if show_json:
        st.json(summary)

    if st.button("Start Weak Spot Drill based on this session"):
        if orch is None:
            st.warning("No active orchestrator. Go to Pre-flight to start a new session.")
            return
        # Start a new drill-mode session wired to the same user.
        orch = Orchestrator(
            user_id=orch.user_id,
            role=orch.role,
            mode="drill",
            tone=orch.tone,
            max_questions=st.session_state.get("max_questions", 6),
        )
        first_q = orch.start_interview()
        st.session_state["orchestrator"] = orch
        st.session_state["current_question"] = first_q
        st.session_state["session_summary"] = None
        st.session_state["view"] = "🎙️ Interview"
        st.session_state["transcribed_answer"] = ""
        st.session_state["tts_cache"] = {}
        st.success("Weak Spot Drill session started.")
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="⚡",
        layout="wide",
    )

    _init_session_state()

    # Inject CSS globally
    from pathlib import Path
    try:
        css_path = Path("static/style.css")
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {e}")

    # Custom Header
    st.markdown('<div class="main-header">Interview Practice Partner</div>', unsafe_allow_html=True)
    _sidebar()

    view = st.session_state["view"]
    if view == "🚀 Pre-flight":
        _render_preflight()
    elif view == "🎙️ Interview":
        _render_interview_room()
    else:
        _render_review()


if __name__ == "__main__":
    main()
