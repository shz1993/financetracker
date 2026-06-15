# 💰 Personal Finance Tracker

Track your income and expenses, visualize spending patterns, and get AI-powered saving tips.

## Live Demo
[Press here for live demo!](https://financetracker-3vdbqd9eyl34dogdrmxubj.streamlit.app/)

## Features
- User authentication (login/register)
- Add, delete, and search income/expense transactions
- Interactive charts (pie chart, bar chart, spending trends)
- AI-powered saving insights and tips
- Export financial reports to PDF
- Filter transactions by monthly, yearly, or all time

## Tech Stack
- Streamlit (frontend)
- SQLAlchemy + PostgreSQL (database)
- Plotly (interactive charts)
- FPDF2 (PDF export)
- Groq API (AI insights - optional)
- bcrypt (password hashing)

## How to Run Locally
1. Clone repo
2. Install requirements: `pip install -r requirements.txt`
3. Create `.streamlit/secrets.toml` with your database URL
4. Run `streamlit run app.py`

## Database Schema
- **users** - User accounts and authentication
- **categories** - Transaction categories with icons
- **transactions** - Income and expense records

## Example Questions (AI Insights)
- "Analyze my spending and give me saving tips"
- "What are my top spending categories?"
- "How much did I save this month?"
- "Show me my spending trends"

## Example Transactions
- Income: Salary, Freelance, Investment
- Expense: Food, Rent, Transport, Health, Entertainment

## PDF Report Includes
- Financial summary (income, expense, balance)
- AI-powered saving tips
- Complete transaction history

## Environment Variables (`.streamlit/secrets.toml`)
```toml
DATABASE_URL = "postgresql://user:password@host:port/database"
GROQ_API_KEY = "your_groq_api_key_here"  # Optional