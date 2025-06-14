import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import csv

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
        tk.Button(self.main_frame, text="Delete Transaction", command=self.delete_transaction).pack(pady=5)
        tk.Button(self.main_frame, text="View Transaction History", command=self.view_transaction_history).pack(pady=5)
        tk.Button(self.main_frame, text="Export to CSV", command=self.export_to_csv).pack(pady=5)
        tk.Button(self.main_frame, text="Toggle Theme", command=self.toggle_theme).pack(pady=5)
        
    def add_income(self):
        amount = self.get_amount()
        desc = self.desc_entry.get()
        category = self.category_var.get()
        if amount and desc:
            self.data["income"].append({
                "amount": amount,
                "desc": desc,
                "category": category,
                "date": str(datetime.now())
            })
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
            self.data["expenses"].append({
                "amount": amount,
                "desc": desc,
                "category": category,
                "date": str(datetime.now())
            })
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
        month_filter = self.month_entry.get()
        if not month_filter:
            month_filter = datetime.now().strftime("%Y-%m")
        
        total_income = 0
        total_expenses = 0
        category_totals = {cat: 0 for cat in self.categories}
        
        
        for item in self.data["income"]:
            if item["date"].startswith(month_filter):
                total_income += item["amount"]
        for item in self.data["expenses"]:
            if item["date"].startswith(month_filter):
                total_expenses += item["amount"]
                category_totals[item["category"]] += item["amount"]
        
        balance = total_income - total_expenses
        savings_progress = min(total_income - total_expenses, self.data["savings_goal"])
        
        summary = f"Budget Summary for {month_filter}:\n\n"
        summary += f"Total Income: ${total_income:.2f}\n"
        summary += f"Total Expenses: ${total_expenses:.2f}\n"
        summary += f"Balance: ${balance:.2f}\n"
        summary += f"Savings Goal: ${self.data['savings_goal']:.2f}\n"
        summary += f"Savings Progress: ${savings_progress:.2f}\n\n"
        summary += "Expenses by Category:\n"
        for cat, total in category_totals.items():
            summary += f"{cat}: ${total:.2f}\n"
        summary += "\nRecent Transactions:\n"
        for item in self.data["income"][-3:]:
            if item["date"].startswith(month_filter):
                summary += f"[Income] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})\n"
        for item in self.data["expenses"][-3:]:
            if item["date"].startswith(month_filter):
                summary += f"[Expense] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})\n"
        
        messagebox.showinfo("Summary", summary)
        
    def show_chart(self):
        month_filter = self.month_entry.get()
        if not month_filter:
            month_filter = datetime.now().strftime("%Y-%m")
        
        total_income = sum(item["amount"] for item in self.data["income"] if item["date"].startswith(month_filter))
        category_totals = {cat: 0 for cat in self.categories}
        for item in self.data["expenses"]:
            if item["date"].startswith(month_filter):
                category_totals[item["category"]] += item["amount"]
        
        plt.figure(figsize=(8, 5))
        plt.bar(["Income"] + self.categories, [total_income] + [category_totals[cat] for cat in self.categories],
                color=["green"] + ["red" for _ in self.categories])
        plt.title(f"Income vs Expenses by Category ({month_filter})")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def delete_transaction(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Transaction")
        delete_window.geometry("500x400")
        
        tk.Label(delete_window, text="Select Transaction to Delete:").pack(pady=10)
        
        listbox = tk.Listbox(delete_window, width=60)
        listbox.pack(pady=10)
        
        for i, item in enumerate(self.data["income"]):
            listbox.insert(tk.END, f"[Income] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})")
        for i, item in enumerate(self.data["expenses"]):
            listbox.insert(tk.END, f"[Expense] {item['desc']}: ${item['amount']} ({item['category']}, {item['date'][:10]})")
        
        def delete_selected():
            selected = listbox.curselection()
            if not selected:
                messagebox.showerror("Error", "Please select a transaction!")
                return
            
            index = selected[0]
            if index < len(self.data["income"]):
                self.data["income"].pop(index)
            else:
                self.data["expenses"].pop(index - len(self.data["income"]))
            self.save_data()
            messagebox.showinfo("Success", "Transaction deleted!")
            delete_window.destroy()
        
        tk.Button(delete_window, text="Delete Selected", command=delete_selected).pack(pady=10)
        
    def view_transaction_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("600x400")
        
        tree = ttk.Treeview(history_window, columns=("Type", "Description", "Amount", "Category", "Date"), show="headings")
        tree.heading("Type", text="Type")
        tree.heading("Description", text="Description")
        tree.heading("Amount", text="Amount ($)")
        tree.heading("Category", text="Category")
        tree.heading("Date", text="Date")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        for item in self.data["income"]:
            tree.insert("", tk.END, values=("Income", item["desc"], f"${item['amount']:.2f}", item["category"], item["date"][:10]))
        for item in self.data["expenses"]:
            tree.insert("", tk.END, values=("Expense", item["desc"], f"${item['amount']:.2f}", item["category"], item["date"][:10]))
        
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
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
        if total_expenses > total_income * 0.8:
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
        with open("budget_data.json", "w") as f:
            json.dump(self.data, f, indent=4)
            
    def load_data(self):
        if os.path.exists("budget_data.json"):
            with open("budget_data.json", "r") as f:
                self.data = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetPlanner(root)
    root.mainloop()