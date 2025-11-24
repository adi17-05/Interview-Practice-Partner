# Interview Practice Partner

A Streamlit-based application for practicing job interviews with an AI partner.

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
