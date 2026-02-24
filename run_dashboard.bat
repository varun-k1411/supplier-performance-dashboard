@echo off
cd /d "C:\Users\Lenovo\PycharmProjects\Supplier Performance Trends"
call .venv\Scripts\activate
streamlit run dashboard/app.py
pause