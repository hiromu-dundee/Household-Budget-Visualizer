# Household Budget Visualizer (Tkinter GUI App)

A Japanese-compatible, fully-featured **household budget visualizer** built with Python and Tkinter.  
This application loads CSV files with income/expense data and visualizes your budget using intuitive graphs and UI tools.

---

## 🚀 Features

- 📊 **Bar charts / pie charts** for category-based expenses
- 🔄 **Switch between monthly and daily views**
- 📈 **Category-wise trend graphs (line plots)**
- 💰 **Automatic calculation of income, expenses, and net balance**
- 🧾 **Add new expenses and append to CSV**
- 🎯 **Monthly budget settings (saved in JSON)**
- 🧩 **Fixed vs Variable expense categorization**
- 🔍 **Search by remarks and date range**
- 🌐 **Full Japanese language support (via japanize-matplotlib)**

---

## 📁 File Structure

| Filename                  | Description                                     |
|---------------------------|-------------------------------------------------|
| `profit_loss_statement.py`| Main application script (Tkinter GUI)           |
| `budget.json`             | Monthly budget per category (auto-generated)    |
| `fv_config.json`          | Fixed/Variable category config (auto-generated) |
| `your_data.csv`           | Your expense CSV file (user-provided)           |

---

## 🖼 GUI Overview

- Monthly bar charts comparing **actual vs budget**
- Daily pie charts for **expense breakdown**
- Line plots showing **category trends**
- Input window to **add new expenses**
- Search panel to **filter by remarks or date**

---

## 📦 Dependencies

Install required packages with:

```bash
pip install matplotlib japanize-matplotlib
```

---

## 🏁 How to Run
```bash
python profit_loss_statement.py
```

---

## 🗂 CSV Format
```bash
Date,Amount,Item,Category,Remarks
2024-04-01,500,Lunch,Food,Restaurant
2024-04-03,800,Electric Bill,Utilities,Base Fee
2024-05-02,3000,Dinner,Food,Family outing
```
- Date format : ```YYYY-MM-DD``` 
- Amount : Integer (in your currency)
- Categories : are customizable (e.g., Foods, Drinks, Outdoor...)

---

## ✍Adding New Expenses
Use the "**Add Expense**" button in the GUI to input new records.
The application appends them directly to the currently loaded CSV-File.

---

## 📈Future Enhancements (Ideas)
- AI-powered expense prediction.
- OCR-based receipt input
- Cross-platform or mobile support
- Cloud sync and backup options