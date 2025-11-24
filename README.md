# Interview Practice Partner

<table>
  <tr>
    <th>📄 Overview</th>
    <th>✨ What It Does</th>
    <th>🔑 Key Features</th>
  </tr>
  <tr>
    <td>
      The AI Interview Practice Partner is an intelligent, multi-agent
      interview preparation platform designed to transform traditional
      Q&A practice into an adaptive, realistic, and personalized
      experience.
    </td>
    <td>
      • Simulates realistic interview sessions <br>
      • Generates role-specific, intelligent questions <br>
      • Performs real-time answer evaluation <br>
      • Supports a voice-first experience <br>
      • Provides comprehensive improvement insights
    </td>
    <td>
      • 🎥 Immersive interview interface <br>
      • 🤖 Four-Agent System (Orchestrator, Interviewer, Critic, Memory) <br>
      • 🎯 5-Dimension evaluation system <br>
      • 🔄 Adaptive question flow <br>
      • 🛡️ Resilience with fallback & retry logic
    </td>
  </tr>

  <tr>
    <th>🧰 Technology Stack</th>
    <th>👥 Use Cases</th>
    <th>⚙️ How It Works</th>
  </tr>
  <tr>
    <td>
      <b>Frontend:</b> Streamlit, HTML, CSS, JavaScript <br>
      <b>Backend:</b> Python, Gemini API <br>
      <b>AI:</b> Multi-agent orchestration
    </td>
    <td>
      • 👨‍💼 Job seekers <br>
      • 🎓 Students & graduates <br>
      • 🔄 Career switchers <br>
      • 📈 Working professionals
    </td>
    <td>
      • Pre-flight setup – 30 sec <br>
      • Interview session – 10–20 min <br>
      • Review & feedback – 5 min
    </td>
  </tr>

  <tr>
    <th>🌟 What Makes It Unique</th>
    <th>🧪 Technical Highlights</th>
    <th>🔮 Future Vision</th>
  </tr>
  <tr>
    <td>
      • Production-ready architecture <br>
      • Intelligent multi-agent integration <br>
      • Resilience-first backend design <br>
      • User-centric, interactive interface
    </td>
    <td>
      • Multi-agent orchestration diagram <br>
      • Robust fallback strategies <br>
      • Clear data-flow design <br>
      • Performance-focused architecture
    </td>
    <td>
      • Mobile applications <br>
      • Multi-language support <br>
      • Advanced AI analytics <br>
      • VR-based interview simulations
    </td>
  </tr>

  <tr>
    <th>🚀 Getting Started</th>
    <th>📁 Project Structure</th>
    <th>🏆 Success Stories</th>
  </tr>
  <tr>
    <td>
      • Quick setup commands <br>
      • Link to detailed setup guide
    </td>
    <td>
      • Complete directory tree <br>
      • Description of major modules
    </td>
    <td>
      • User testimonials <br>
      • Improvements in interview readiness
    </td>
  </tr>

</table>

<br>

## 🎯 Key Highlights
- ✅ Comprehensive yet compact  
- ✅ User-friendly for all audiences  
- ✅ Perfect for portfolio or documentation  
- ✅ Includes features, use cases, tech, and roadmap  
- ✅ Highly visual and easy to read  


## 📸 Overview

### Preflight view 1
![Screenshot 1](images/Screenshot%202025-11-24 121955.png)

### Preflight view 2
![Screenshot 2](images/Screenshot%202025-11-24 122013.png)

### Interview 1
![Screenshot 3](images/Screenshot%202025-11-24 122035.png)

### Interview 2
![Screenshot 4](images/Screenshot%202025-11-24 122358.png)

### Review 1
![Screenshot 5](images/Screenshot%202025-11-24 122414.png)



## 📊 User Flow Diagram
![User Flow Diagram](images/user_flow_diagram.svg)

## 🤖 Agent Orchestration Diagram
![Agent Flow Diagram](images/agent_flow_diagram.svg)

## Prerequisites

- Python 3.10 - 3.12 (Python 3.14 is currently unsupported due to dependency issues)
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)

## Setup

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd interview-practice-partner
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    - Windows:
        ```powershell
        .\venv\Scripts\activate
        ```
    - macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables**:
    - Create a `.env` file in the root directory.
    - Add your Google API key:
        ```
        GOOGLE_API_KEY=your_api_key_here
        ```

## Running the Application

To start the application, run:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.



