

# 💰 Personal Finance Management Dashboard

## 📌 Overview

The **Personal Finance Management Dashboard** is a web application that helps users **track, analyze, and optimize** their financial activities.
Unlike traditional expense trackers, this dashboard integrates **AI-powered insights, predictive alerts, and a conversational interface**, making it **smarter, interactive, and more user-friendly**.

The goal is to help users not only *record* expenses but also *understand* their financial habits and make better money decisions.

---

## 🚀 Key Features

✅ **Expense & Income Tracking** – Add daily expenses/income with categories (food, travel, bills, shopping, etc.)
✅ **Budget Planner** – Set monthly/weekly budgets and get progress reports
✅ **AI-Powered Spending Coach** – Personalized suggestions (e.g., “You spent 30% more on food than last week”)
✅ **Predictive Alerts** – Warns if you’re about to exceed your budget based on current spending trends
✅ **Voice & Chatbot Interface** – Add or query expenses using natural language (e.g., “How much did I spend on groceries?”)
✅ **Smart Investment Suggestions** – Recommend safe saving/investment options based on leftover balance
✅ **Community Insights** – Compare spending trends with anonymized peer groups (age/location-based)
✅ **Data Visualization** – Charts & graphs for category-wise spending, monthly comparisons, and savings patterns

---

## 🛠️ Tech Stack

### Frontend

* **HTML, CSS, JavaScript** → Dashboard UI
* **React.js / Vue.js** (optional) → Modern SPA design
* **Chart.js / D3.js** → Interactive financial charts

### Backend

* **Python (Flask / Django)** → REST APIs
* **SQLite / PostgreSQL / MongoDB** → Store transactions & budgets
* **Natural Language Processing (NLP)** → Chatbot & voice queries
* **Machine Learning (Scikit-learn / TensorFlow)** → Predictions & insights

### Additional Integrations

* **Speech-to-Text API** (Google / OpenAI Whisper) → Voice inputs
* **Authentication** (JWT / Firebase) → Secure login/signup
* **Deployment** → AWS / Heroku / GCP

---

## 📂 Project Structure

```
📦 Personal-Finance-Dashboard
 ┣ 📂 backend
 ┃ ┣ 📜 app.py              # Flask backend
 ┃ ┣ 📜 models.py           # Database models
 ┃ ┗ 📜 routes.py           # API routes
 ┣ 📂 frontend
 ┃ ┣ 📜 index.html          # Main dashboard UI
 ┃ ┣ 📜 style.css           # Styling
 ┃ ┣ 📜 app.js              # Frontend logic
 ┃ ┗ 📜 charts.js           # Visualization
 ┣ 📂 ml
 ┃ ┣ 📜 predictor.py        # Spending prediction model
 ┃ ┗ 📜 coach.py            # AI finance coach
 ┣ 📜 requirements.txt      # Python dependencies
 ┣ 📜 README.md             # Documentation
 ┗ 📜 LICENSE
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/personal-finance-dashboard.git
cd personal-finance-dashboard
```

### 2. Backend Setup (Flask Example)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. Frontend Setup

Simply open `frontend/index.html` in your browser OR use a live server (`npm install -g live-server`).

### 4. Database Setup

* Default: **SQLite**
* Run migration script:

```bash
python models.py
```

---

## 📊 Example Use Cases

* Track daily expenses with categories
* Set a budget of ₹10,000/month and get alerts when nearing limits
* Ask chatbot: *“Show me food expenses this month”* → Chart response
* Predict next month’s savings → *“₹5,200 expected based on current pace”*
* Suggestion: *“You saved ₹5,000 this month. Consider investing in FD @7%”*

---

## 🌟 Future Enhancements

* 🔗 **Bank Integration (UPI/Net Banking)** for automatic transaction fetch
* 📱 **Mobile App (Flutter/React Native)** for accessibility
* 🧠 **AI-powered financial goal planning** (buying a car, house, etc.)
* 💳 **Credit Score Tracker & Loan Recommendation**

---

## 🎯 Why This Project is Unique?

Unlike existing apps (Google Pay, Mint, Walnut), this dashboard:

1. Uses **AI insights + chatbot/voice** to *explain spending habits conversationally*.
2. Provides **predictive alerts** before overspending occurs.
3. Adds **gamification & community insights** to encourage better saving.

---

## 👨‍💻 Author

**Kakulooru Mahesh**
B.Tech | AI & Software Engineering Enthusiast




