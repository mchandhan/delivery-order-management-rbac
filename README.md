# Nova Nexus — Manufacturing AI Assistant & Order Management System

Welcome to the **Nova Nexus** project! This is a full-stack web application designed to streamline manufacturing order management. It features a conversational AI assistant that extracts order details from natural language, an admin dashboard, user order tracking, and role-based authentication.

## 🚀 Key Features

1. **AI Chat Assistant (Nova)**
   - Powered by Hugging Face's Inference API, the assistant understands natural language inputs.
   - Extracts order specifications (part name, material, quantity, deadline) even from conversational text or typos.
   - Outputs structured JSON to automate order creation.

2. **Role-Based Portals**
   - **User Dashboard** (`user.html`): Users can track their own orders, chat with Nova to place new orders, and view their chat history.
   - **Admin Dashboard** (`admin.html`): Administrators can oversee all incoming orders, update order statuses, manage user accounts, and review chat logs.

3. **Secure & Lightweight Backend**
   - Built with **Python / Flask** acting as the API and server.
   - Uses **SQLite** (`orders.db`) for lightweight, file-based relational data storage (Users, Orders, Chat History).
   - Secures AI API keys using environment variables (`.env`).

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, Vanilla JavaScript, CSS.
- **Backend**: Python 3, Flask, Flask-CORS.
- **Database**: SQLite.
- **AI Integration**: Hugging Face Inference API (`router.huggingface.co`).

---

## 📂 Project Structure

| File / Folder | Purpose |
| :--- | :--- |
| `app.py` | Main Flask backend. Handles database initialization, API endpoints, and AI proxy routing. |
| `index3.html` | The AI Chat Assistant interface (Nova Nexus). |
| `admin.html` | The Admin management dashboard. |
| `user.html` | The User-specific order dashboard. |
| `log_siign.html` | The landing page handling user Login and Signup. |
| `register.html` | Account registration page (often linked from the landing page). |
| `.env` | Hidden file for storing the `HF_API_KEY`. |
| `orders.db` | Auto-generated SQLite database file containing user, order, and chat tables. |
| `requirements.txt` | Python dependencies required to run the application. |

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- **Python 3.7+** installed on your machine.
- An active internet connection to communicate with the Hugging Face AI API.
- A Hugging Face account and an API Key.

### 2. Clone the Repository
Navigate into the project directory (or clone it to your machine):
```powershell
cd C:\Users\mchan\Downloads\ai-chatbot1\ai-chatbot
```

### 3. Install Dependencies
Install the required Python packages using pip:
```powershell
pip install -r requirements.txt
```
*(Dependencies include `flask`, `flask-cors`, `python-dotenv`, and `requests`)*

### 4. Configure the Environment
Create a file named `.env` in the root directory (in the same folder as `app.py`). Add your Hugging Face API key inside:
```env
HF_API_KEY=your_huggingface_api_key_here
```
*Note: The backend securely loads this key to authenticate requests to the AI model without exposing it in the browser.*

---

## ▶️ Running the Application

1. **Start the Flask Server**
   Run the following command in your terminal:
   ```powershell
   python app.py
   ```
   *The server will start on port 8080. The SQLite database and tables will be initialized automatically if they don't already exist.*

2. **Access the Application**
   Open your web browser and navigate to:
   - **Main Entry / Login:** [http://localhost:8080/](http://localhost:8080/)
   - Based on your role (User vs Admin), you will be directed to the respective dashboards upon logging in.

---

## 🧠 How the AI Works (Behind the Scenes)
When a user chats with Nova:
1. The browser sends the chat history to the Flask server (`/api/chat`).
2. Flask injects a strict **System Prompt** instructing the AI to act as a manufacturing assistant and extract specific data fields.
3. The request is securely forwarded to Hugging Face via Python's `requests` library.
4. If an order intent is detected, the AI appends a structured JSON block (e.g., `{"action": "create_order", "data": {"partName": "...", "material": "...", "quantity": ..., "deadline": "..."}}`) to its response.
5. The frontend or backend parses this JSON to automate the database insertion (`INSERT INTO orders...`).

---

## 🚧 Challenges & Limitations

### Local LLM Constraints (Ollama)
- **Problem**: Early versions using local models (like Qwen3 9B via Ollama) were too slow for a fluid chat experience and required a powerful GPU.
- **Solution**: Migrated to **DeepSeek via Hugging Face Router**. This provided a 10x speed boost and removed the hardware requirement from the local machine.

### Simplified Login & Authentication
- **Limitation**: The login system does not use secure password hashing, tokens, or strict session management. Passwords are saved and verified in plain text.
- **Reason**: This application was built as a **practice project**. The authentication architecture was intentionally simplified to focus on learning core Flask routing, database connections, and AI integration rather than advanced security infrastructure.
