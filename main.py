import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from database import PayrollDatabase
from excel_handler import ExcelHandler
from ollama_analyzer import OllamaAnalyzer


class PayrollSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll Anytime")
        self.root.geometry("1400x850")
        self.root.configure(bg='#FFFFFF')
        
        self.db = PayrollDatabase()
        self.excel_handler = ExcelHandler(self.db)
        self.ollama_analyzer = OllamaAnalyzer(self.db)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        self.setup_styles()
        self.create_main_interface()

    def setup_styles(self):
        """配置Tk样式"""
        style = ttk.Style()
        
        style.theme_use('clam')
        
        style.configure('TNotebook', 
                      background='#FFFFFF',
                      borderwidth=0)
        
        style.configure('TNotebook.Tab',
                      background='#F5F5F7',
                      foreground='#1D1D1F',
                      padding=[24, 12])
        
        style.map('TNotebook.Tab',
                  background=[('selected', '#FFFFFF')],
                  foreground=[('selected', '#007AFF')])
        
        style.configure('Treeview',
                      background='#FFFFFF',
                      foreground='#1D1D1F',
                      rowheight=30,
                      fieldbackground='#FFFFFF',
                      borderwidth=0)
        
        style.configure('Treeview.Heading',
                      background='#F5F5F7',
                      foreground='#1D1D1F')
        
        style.configure('Modern.TButton',
                      background='#007AFF',
                      foreground='white',
                      borderwidth=0)
        
        style.map('Modern.TButton',
                  background=[('active', '#0056B3')])

    def create_main_interface(self):
        navbar = tk.Frame(self.root, bg='#FFFFFF', height=60)
        navbar.pack(fill=tk.X)
        navbar.pack_propagate(False)
        
        title_frame = tk.Frame(navbar, bg='#FFFFFF')
        title_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        title_label = tk.Label(title_frame, 
                              text="Payroll Anytime",
                              font=('Segoe UI', 14, 'bold'),
                              bg='#FFFFFF',
                              fg='#1D1D1F')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                text="Simple • Intuitive • Powerful",
                                font=('Segoe UI', 9),
                                bg='#FFFFFF',
                                fg='#86868B')
        subtitle_label.pack()

        date_selector = tk.Frame(navbar, bg='#FFFFFF')
        date_selector.pack(side=tk.LEFT, padx=40, pady=15)
        
        tk.Label(date_selector, text="Year", 
                font=('Segoe UI', 10),
                bg='#FFFFFF',
                fg='#86868B').pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spinbox = ttk.Spinbox(date_selector, from_=2020, to=2030, textvariable=self.year_var, width=10)
        year_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_selector, text="Month",
                font=('Segoe UI', 10),
                bg='#FFFFFF',
                fg='#86868B').pack(side=tk.LEFT, padx=5)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_spinbox = ttk.Spinbox(date_selector, from_=1, to=12, textvariable=self.month_var, width=8)
        month_spinbox.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(navbar,
                              text="Refresh",
                              command=self.refresh_data,
                              bg='#F5F5F7',
                              fg='#1D1D1F',
                              borderwidth=0,
                              font=('Segoe UI', 10),
                              cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=30, pady=15)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.employee_tab = ttk.Frame(notebook)
        self.attendance_tab = ttk.Frame(notebook)
        self.performance_tab = ttk.Frame(notebook)
        self.payroll_tab = ttk.Frame(notebook)
        self.ai_tab = ttk.Frame(notebook)
        
        notebook.add(self.employee_tab, text="  👥 Employees  ")
        notebook.add(self.attendance_tab, text="  📅 Attendance  ")
        notebook.add(self.performance_tab, text="  ⭐ Performance  ")
        notebook.add(self.payroll_tab, text="  💰 Payroll  ")
        notebook.add(self.ai_tab, text="  🤖 AI Analysis  ")
        
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_performance_tab()
        self.create_payroll_tab()
        self.create_ai_tab()

    def create_employee_tab(self):
        toolbar = tk.Frame(self.employee_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, " Add", "#007AFF", self.add_employee_dialog)
        self.create_button(btn_frame, " Edit", "#F5F5F7", self.edit_employee_dialog)
        self.create_button(btn_frame, " Delete", "#F5F5F7", self.delete_employee)
        self.create_button(btn_frame, " Export", "#F5F5F7", self.export_employee_list)
        
        search_frame = tk.Frame(toolbar, bg='#FFFFFF')
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        self.employee_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.employee_search_var, width=20, font=('Segoe UI', 10), bg='#F5F5F7', fg='#1D1D1F', relief='flat', insertbackground='white')
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Search", command=self.search_employee, bg='#007AFF', fg='white', borderwidth=0, font=('Segoe UI', 10), cursor='hand2').pack(side=tk.LEFT)

        self.create_employee_table()

    def create_attendance_tab(self):
        toolbar = tk.Frame(self.attendance_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, " Import", "#007AFF", self.import_attendance)
        self.create_button(btn_frame, " Template", "#F5F5F7", self.generate_attendance_template)
        
        self.create_attendance_table()

    def create_performance_tab(self):
        toolbar = tk.Frame(self.performance_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, " Import", "#007AFF", self.import_performance)
        self.create_button(btn_frame, " Template", "#F5F5F7", self.generate_performance_template)
        
        self.create_performance_table()

    def create_payroll_tab(self):
        toolbar = tk.Frame(self.payroll_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, " Calculate", "#007AFF", self.calculate_all_salaries)
        self.create_button(btn_frame, " Export", "#F5F5F7", self.export_payroll)
        
        self.create_payroll_table()

    def create_ai_tab(self):
        toolbar = tk.Frame(self.ai_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X)
        
        tk.Label(toolbar, text="Select Analysis:", font=('Segoe UI', 10, 'bold'), bg='#FFFFFF', fg='#1D1D1F').pack(side=tk.LEFT, padx=10)
        
        functions = [
            (" Overall Analysis", self.analyze_overall),
            (" Employee Analysis", self.analyze_employee),
            (" Trend Prediction", self.predict_trend),
            (" Performance Review", self.generate_performance_review)
        ]
        
        for text, command in functions:
            self.create_button(toolbar, text, "#007AFF", command)
        
        ttk.Separator(self.ai_tab, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.ai_output = tk.Text(self.ai_tab, height=20, width=100, wrap=tk.WORD, font=('Segoe UI', 10), bg='#F5F5F7', fg='#1D1D1F')
        self.ai_output.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(self.ai_tab, orient=tk.VERTICAL, command=self.ai_output.yview)
        self.ai_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_button(self, parent, text, bg_color, command):
        """创建按钮 - 不使用 padx/pady"""
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=bg_color,
                       fg='white',
                       borderwidth=0,
                       font=('Segoe UI', 10),
                       cursor='hand2',
                       relief='flat')
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def create_employee_table(self):
        columns = ('ID', 'Name', 'Dept', 'Position', 'Salary', 'Date', 'Status')
        self.employee_tree = ttk.Treeview(self.employee_tab, columns=columns, show='headings')
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120, anchor='w')
        
        scrollbar = ttk.Scrollbar(self.employee_tab, orient=tk.VERTICAL, command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)

        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_employee_data()

    def create_attendance_table(self):
        columns = ('ID', 'Name', 'Dept', 'Days', 'Late', 'Leave', 'Overtime')
        self.attendance_tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings')
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=100, anchor='w')
        
        scrollbar = ttk.Scrollbar(self.attendance_tab, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)

        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_attendance_data()

    def create_performance_table(self):
        columns = ('ID', 'Name', 'Score', 'Grade', 'Formula')
        self.performance_tree = ttk.Treeview(self.performance_tab, columns=columns, show='headings')
        
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=140, anchor='w')
        
        scrollbar = ttk.Scrollbar(self.performance_tab, orient=tk.VERTICAL, command=self.performance_tree.yview)
        self.performance_tree.configure(yscrollcommand=scrollbar.set)

        self.performance_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_performance_data()

    def create_payroll_table(self):
        columns = ('ID', 'Name', 'Dept', 'Base', 'Attend', 'Bonus',
                  'Social', 'Fund', 'Total', 'Gross', 'Net')
        self.payroll_tree = ttk.Treeview(self.payroll_tab, columns=columns, show='headings')
        
        for col in columns:
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=100, anchor='w')
        
        scrollbar = ttk.Scrollbar(self.payroll_tab, orient=tk.VERTICAL, command=self.payroll_tree.yview)
        self.payroll_tree.configure(yscrollcommand=scrollbar.set)

        self.payroll_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_payroll_data()

    def load_employee_data(self):
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        employees = self.db.get_all_employees()

        for emp in employees:
            self.employee_tree.insert('', tk.END, values=(
                emp['employee_id'],
                emp['name'],
                emp['department'],
                emp['position'],
                f"{emp['basic_salary']:.2f}",
                emp['entry_date'],
                emp['status']
            ))

    def load_attendance_data(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        year = int(self.year_var.get())
        month = int(self.month_var.get())

        attendance_records = self.db.get_all_attendance(year, month)

        for record in attendance_records:
            employee = self.db.get_employee(record['employee_id'])
            if employee:
                self.attendance_tree.insert('', tk.END, values=(
                    record['employee_id'],
                    employee['name'],
                    employee['department'],
                    record['work_days'],
                    record['late_days'],
                    record['leave_days'],
                    record['overtime_hours']
                ))

    def load_performance_data(self):
        for item in self.performance_tree.get_children():
            self.performance_tree.delete(item)

        year = int(self.year_var.get())
        month = int(self.month_var.get())

        employees = self.db.get_all_employees()

        for emp in employees:
            performance = self.db.get_performance(emp['employee_id'], year, month)
            if performance:
                self.performance_tree.insert('', tk.END, values=(
                    emp['employee_id'],
                    emp['name'],
                    performance['score'],
                    performance['grade'],
                    performance['bonus_formula']
                ))
            else:
                self.performance_tree.insert('', tk.END, values=(
                    emp['employee_id'],
                    emp['name'],
                    '',
                    '',
                    ''
                ))

    def load_payroll_data(self):
        for item in self.payroll_tree.get_children():
            self.payroll_tree.delete(item)

        year = int(self.year_var.get())
        month = int(self.month_var.get())

        payroll_records = self.db.get_payroll(year, month)

        for record in payroll_records:
            self.payroll_tree.insert('', tk.END, values=(
                record['employee_id'],
                record['name'],
                record['department'],
                f"{record['basic_salary']:.2f}",
                f"{record['attendance_salary']:.2f}",
                f"{record['performance_bonus']:.2f}",
                f"{record['social_deduction']:.2f}",
                f"{record['fund_deduction']:.2f}",
                f"{record['total_deduction']:.2f}",
                f"{record['gross_salary']:.2f}",
                f"{record['net_salary']:.2f}"
            ))

    def add_employee_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Employee - Payroll Anytime")
        dialog.geometry("400x500")
        dialog.configure(bg='#FFFFFF')
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg='#FFFFFF')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(main_frame, text="Add New Employee", font=('Segoe UI', 12, 'bold'), bg='#FFFFFF', fg='#1D1D1F').pack(pady=(0, 20))

        fields = [
            ('Employee ID', ''),
            ('Name', ''),
            ('Department', ''),
            ('Position', ''),
            ('Base Salary', '5000'),
            ('Social Rate (0-1)', '0.08'),
            ('Housing Fund Rate (0-1)', '0.12'),
            ('Medical Rate (0-1)', '0.02'),
            ('Unemployment Rate (0-1)', '0.005'),
            ('Entry Date', datetime.now().strftime('%Y-%m-%d'))
        ]

        entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(main_frame, text=label, bg='#FFFFFF', fg='#86868B', font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w')
            entry = tk.Entry(main_frame, font=('Segoe UI', 10), bg='#F5F5F7', fg='#1D1D1F', relief='flat', insertbackground='white')
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky='ew')
            entries[label] = entry

        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=30)

        save_btn = tk.Button(button_frame, text="Save Employee", command=self.save_employee, dialog=dialog, entries=entries, bg='#007AFF', fg='white', borderwidth=0, font=('Segoe UI', 10), cursor='hand2', relief='flat')
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg='#F5F5F7', fg='#1D1D1F', borderwidth=0, font=('Segoe UI', 10), cursor='hand2', relief='flat')
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def save_employee(self, dialog, entries):
        try:
            employee_data = {
                'employee_id': entries['Employee ID'].get().strip(),
                'name': entries['Name'].get().strip(),
                'department': entries['Department'].get().strip(),
                'position': entries['Position'].get().strip(),
                'basic_salary': float(entries['Base Salary'].get()),
                'base_social_rate': float(entries['Social Rate (0-1)'].get()),
                'base_fund_rate': float(entries['Housing Fund Rate (0-1)'].get()),
                'base_medical_rate': float(entries['Medical Rate (0-1)'].get()),
                'unemployed_rate': float(entries['Unemployment Rate (0-1)'].get()),
                'entry_date': entries['Entry Date'].get().strip()
            }

            if not employee_data['employee_id'] or not employee_data['name']:
                messagebox.showerror("Error", "ID and Name are required")
                return

            if self.db.add_employee(employee_data):
                messagebox.showinfo("Success", "Employee added successfully")
                self.load_employee_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add employee")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def edit_employee_dialog(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee")
            return

        messagebox.showinfo("Info", "Edit feature coming soon")

    def delete_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an employee")
            return

        employee_id = self.employee_tree.item(selected[0])['values'][0]
        employee_name = self.employee_tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Confirm", f"Delete {employee_name}?"):
            if self.db.delete_employee(employee_id):
                messagebox.showinfo("Success", "Employee deleted successfully")
                self.load_employee_data()
            else:
                messagebox.showerror("Error", "Failed to delete employee")

    def search_employee(self):
        keyword = self.employee_search_var.get().strip().lower()

        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        employees = self.db.get_all_employees()

        for emp in employees:
            if (keyword in emp['employee_id'].lower() or
                keyword in emp['name'].lower() or
                keyword in emp['department'].lower()):

                self.employee_tree.insert('', tk.END, values=(
                    emp['employee_id'],
                    emp['name'],
                    emp['department'],
                    emp['position'],
                    f"{emp['basic_salary']:.2f}",
                    emp['entry_date'],
                    emp['status']
                ))

    def export_employee_list(self):
        result = self.excel_handler.export_employee_list()
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

    def import_attendance(self):
        messagebox.showinfo("Info", "Import feature coming soon")

    def generate_attendance_template(self):
        result = self.excel_handler.generate_attendance_template()
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

    def import_performance(self):
        messagebox.showinfo("Info", "Import feature coming soon")

    def generate_performance_template(self):
        result = self.excel_handler.generate_performance_template()
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

    def calculate_all_salaries(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        employees = self.db.get_all_employees()

        if not employees:
            messagebox.showwarning("Warning", "No employees found")
            return

        if messagebox.askyesno("Confirm", f"Calculate salaries for {year}/{month}?"):
            success = 0
            failed = 0
            
            for emp in employees:
                if self.db.calculate_salary(emp['employee_id'], year, month):
                    success += 1
                else:
                    failed += 1
            
            messagebox.showinfo("Done", f"Success: {success}, Failed: {failed}")
            self.load_payroll_data()

    def export_payroll(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        result = self.excel_handler.export_payroll_to_excel(year, month)

        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

    def refresh_data(self):
        self.current_year = int(self.year_var.get())
        self.current_month = int(self.month_var.get())

        self.load_employee_data()
        self.load_attendance_data()
        self.load_performance_data()
        self.load_payroll_data()
        messagebox.showinfo("Info", "Data refreshed")

    def analyze_overall(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        self.ai_output.delete(1.0, tk.END)
        self.ai_output.insert(tk.END, "Analyzing...\n")
        self.ai_output.insert(tk.END, f"Year: {year}, Month: {month}\n")
        self.ai_output.insert(tk.END, "-" * 50 + "\n")
        self.root.update()

        result = self.ollama_analyzer.analyze_salary_data(year, month)

        self.ai_output.insert(tk.END, "\n" + "-" * 50 + "\n")
        if not result:
            self.ai_output.insert(tk.END, "No data received\n")
        elif "failed" in result.lower():
            self.ai_output.insert(tk.END, f"Error: {result}\n")
        else:
            self.ai_output.insert(tk.END, result + "\n")

        self.ai_output.insert(tk.END, "-" * 50 + "\n")
        self.ai_output.insert(tk.END, "Done\n")
        self.ai_output.see(tk.END)

    def analyze_employee(self):
        messagebox.showinfo("Info", "Employee analysis coming soon")

    def predict_trend(self):
        messagebox.showinfo("Info", "Trend prediction coming soon")

    def generate_performance_review(self):
        messagebox.showinfo("Info", "Performance review coming soon")


def main():
    root = tk.Tk()
    app = PayrollSystemGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
