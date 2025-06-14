import tkinter as tk
from tkinter import messagebox, ttk
import shelve
import os
from datetime import datetime
import matplotlib.pyplot as plt
import csv
import sys

class BudgetPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Budget Planner")
        self.root.geometry("600x500")
        self.is_dark_mode = False
        self.data = {"income": [], "expenses": [], "savings_goal": 0}
        self.categories = ["Food", "Entertainment", "Bills", "Shopping", "Other"]
        self.load_data()
        self.create_widgets()
        
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg="white")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(self.main_frame, text="Home Budget Planner", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.main_frame, text="Amount:").pack()
        self.amount_entry = tk.Entry(self.main_frame)
        self.amount_entry.pack()
        tk.Label(self.main_frame, text="Description:").pack()
        self.desc_entry = tk.Entry(self.main_frame)
        self.desc_entry.pack()
        tk.Label(self.main_frame, text="Category:").pack()
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_menu = ttk.Combobox(self.main_frame, textvariable=self.category_var, values=self.categories)
        self.category_menu.pack()
        tk.Label(self.main_frame, text="Filter Summary by Month (YYYY-MM):").pack()
        self.month_entry = tk.Entry(self.main_frame)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))
        self.month_entry.pack()
        tk.Button(self.main_frame, text="Add Income", command=self.add_income).pack(pady=5)
        tk.Button(self.main_frame, text="Add Expense", command=self.add_expense).pack(pady=5)
        tk.Button(self.main_frame, text="Set Savings Goal", command=self.set_savings_goal).pack(pady=5)
        tk.Button(self.main_frame, text="View Summary", command=self.view_summary).pack(pady=5)
        tk.Button(self.main_frame, text="Show Chart", command=self.show_chart).pack(pady=5)
        tk.Button(self.main_frame, text="Edit Transactions", command=self.edit_transactions).pack(pady=5)
        tk.Button(self.main_frame, text="Export to CSV", command=self.export_to_csv).pack(pady=5)
        tk.Button(self.main_frame, text="Toggle Theme", command=self.toggle_theme).pack(pady=5)
        
    def add_income(self):
        amount = self.get_amount()
        desc = self.desc_entry.get()
        category = self.category_var.get()
        if amount and desc:
            self.data["income"].append({"amount": amount, "desc": desc, "category": category, "date": str(datetime.now())})
            self.save_data()
            messagebox.showinfo("Success", f"Added Income: {desc} (${amount}) in {category}")
            self.check_budget_alert()
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Please enter amount and description!")
            
    def add_expense(self):
        amount = self.get_amount()
        desc = self.desc_entry.get()
        category = self.category_var.get()
        if amount and desc:
            self.data["expenses"].append({"amount": amount, "desc": desc, "category": category, "date": str(datetime.now())})
            self.save_data()
            messagebox.showinfo("Success", f"Added Expense: {desc} (${amount}) in {category}")
            self.check_budget_alert()
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Please enter amount and description!")
            
    def set_savings_goal(self):
        amount = self.get_amount()
        if amount:
            self.data["savings_goal"] = amount
            self.save_data()
            messagebox.showinfo("Success", f"Savings Goal set to ${amount}")
            self.check_budget_alert()
            self.clear_entries()
        else:
            messagebox.showerror("Error", "Please enter a valid amount!")
            
    def view_summary(self):
        month_filter = self.month_entry.get().strip()
        if not month_filter or not all(c.isdigit() or c == '-' for c in month_filter):
            month_filter = datetime.now().strftime("%Y-%m")
        total_income = sum(item["amount"] for item in self.data["income"] if item["date"].startswith(month_filter))
        total_expenses = sum(item["amount"] for item in self.data["expenses"] if item["date"].startswith(month_filter))
        category_totals = {cat: sum(item["amount"] for item in self.data["expenses"] if item["date"].startswith(month_filter) and item["category"] == cat) for cat in self.categories}
        balance = total_income - total_expenses
        savings_progress = min(balance, self.data["savings_goal"]) if self.data["savings_goal"] > 0 else 0
        summary = f"Budget Summary for {month_filter}:\n\nTotal Income: ${total_income:.2f}\nTotal Expenses: ${total_expenses:.2f}\nBalance: ${balance:.2f}\nSavings Goal: ${self.data['savings_goal']:.2f}\nSavings Progress: ${savings_progress:.2f}\n\nExpenses by Category:\n"
        summary += "\n".join(f"{cat}: ${total:.2f}" for cat, total in category_totals.items() if total > 0)
        summary += "\n\nRecent Transactions:\n"
        recent_income = [item for item in self.data["income"][-3:] if item["date"].startswith(month_filter)] if self.data["income"] else []
        recent_expenses = [item for item in self.data["expenses"][-3:] if item["date"].startswith(month_filter)] if self.data["expenses"] else []
        for item in recent_income:
            summary += f"[Income] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})\n"
        for item in recent_expenses:
            summary += f"[Expense] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})\n"
        messagebox.showinfo("Summary", summary if total_income or total_expenses else "No transactions for this month.")
        
    def show_chart(self):
        month_filter = self.month_entry.get().strip()
        if not month_filter:
            month_filter = datetime.now().strftime("%Y-%m")
        total_income = sum(item["amount"] for item in self.data["income"] if item["date"].startswith(month_filter))
        category_totals = {cat: sum(item["amount"] for item in self.data["expenses"] if item["date"].startswith(month_filter) and item["category"] == cat) for cat in self.categories}
        plt.figure(figsize=(8, 5))
        plt.bar(["Income"] + self.categories, [total_income] + [category_totals[cat] for cat in self.categories], color=["green"] + ["red" for _ in self.categories])
        plt.title(f"Income vs Expenses by Category ({month_filter})")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def edit_transactions(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transactions")
        edit_window.geometry("500x400")
        tk.Label(edit_window, text="Select Transaction to Edit:").pack(pady=10)
        listbox = tk.Listbox(edit_window, width=60)
        listbox.pack(pady=10)
        if not self.data["income"] and not self.data["expenses"]:
            listbox.insert(tk.END, "No transactions to edit.")
        else:
            for i, item in enumerate(self.data["income"]):
                listbox.insert(tk.END, f"[Income] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})")
            for i, item in enumerate(self.data["expenses"]):
                listbox.insert(tk.END, f"[Expense] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})")
        
        def edit_selected():
            selected = listbox.curselection()
            if not selected:
                messagebox.showerror("Error", "Please select a transaction to edit!")
                return
            index = selected[0]
            if index < len(self.data["income"]):
                trans_type = "income"
                trans_index = index
            else:
                trans_type = "expenses"
                trans_index = index - len(self.data["income"])
            transaction = self.data[trans_type][trans_index]
            edit_dialog = tk.Toplevel(edit_window)
            edit_dialog.title("Edit Transaction")
            edit_dialog.geometry("300x200")
            tk.Label(edit_dialog, text="Amount:").pack()
            amount_entry = tk.Entry(edit_dialog)
            amount_entry.insert(0, str(transaction["amount"]))
            amount_entry.pack()
            tk.Label(edit_dialog, text="Description:").pack()
            desc_entry = tk.Entry(edit_dialog)
            desc_entry.insert(0, transaction["desc"])
            desc_entry.pack()
            tk.Label(edit_dialog, text="Category:").pack()
            category_var = tk.StringVar(value=transaction["category"])
            category_menu = ttk.Combobox(edit_dialog, textvariable=category_var, values=self.categories)
            category_menu.pack()
            def save_edit():
                new_amount = float(amount_entry.get())
                new_desc = desc_entry.get()
                new_category = category_var.get()
                if new_amount and new_desc:
                    self.data[trans_type][trans_index] = {"amount": new_amount, "desc": new_desc, "category": new_category, "date": transaction["date"]}
                    self.save_data()
                    messagebox.showinfo("Success", "Transaction updated!")
                    edit_dialog.destroy()
                    edit_window.destroy()
                else:
                    messagebox.showerror("Error", "Please enter amount and description!")
            tk.Button(edit_dialog, text="Save Changes", command=save_edit).pack(pady=10)
        
        tk.Button(edit_window, text="Edit Selected", command=edit_selected).pack(pady=10)
        
    def export_to_csv(self):
        with open("budget_export.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Description", "Amount", "Category", "Date"])
            for item in self.data["income"]:
                writer.writerow(["Income", item["desc"], item["amount"], item["category"], item["date"]])
            for item in self.data["expenses"]:
                writer.writerow(["Expense", item["desc"], item["amount"], item["category"], item["date"]])
        messagebox.showinfo("Success", "Budget exported to budget_export.csv!")
        
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.main_frame.configure(bg="gray20")
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg="gray20", fg="white")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="gray40", fg="white")
        else:
            self.main_frame.configure(bg="white")
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg="white", fg="black")
                elif isinstance(widget, tk.Button):
                    widget.configure(bg="SystemButtonFace", fg="black")
        
    def check_budget_alert(self):
        total_income = sum(item["amount"] for item in self.data["income"])
        total_expenses = sum(item["amount"] for item in self.data["expenses"])
        balance = total_income - total_expenses
        if total_expenses > total_income * 0.8 and total_income > 0:
            messagebox.showwarning("Budget Alert", "Warning: Expenses are more than 80% of your income!")
        if self.data["savings_goal"] > 0 and balance < self.data["savings_goal"] * 0.5:
            messagebox.showwarning("Savings Alert", "Warning: Your balance is less than 50% of your savings goal!")
            
    def get_amount(self):
        try:
            return float(self.amount_entry.get())
        except ValueError:
            return None
            
    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.category_var.set(self.categories[0])
        
    def save_data(self):
        try:
            with shelve.open("budget_data.db") as db:
                db["data"] = self.data
            print("Data saved to budget_data.db")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            
    def load_data(self):
        if os.path.exists("budget_data.db"):
            try:
                with shelve.open("budget_data.db") as db:
                    self.data = db.get("data", {"income": [], "expenses": [], "savings_goal": 0})
                print(f"Data loaded from budget_data.db: {self.data}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                self.data = {"income": [], "expenses": [], "savings_goal": 0}
        else:
            self.save_data()

if __name__ == "__main__":
    if os.environ.get("DISPLAY") is None and sys.platform != "win32":
        print("Error: No display environment. Run this on a system with a graphical interface.")
    else:
        root = tk.Tk()
        app = BudgetPlanner(root)
        root.mainloop()