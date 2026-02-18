import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database import PayrollDatabase
from excel_handler import ExcelHandler

class PayrollSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("工资核算系统")
        self.root.geometry("1200x700")
        self.db = PayrollDatabase()
        self.excel_handler = ExcelHandler(self.db)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.create_main_interface()

    def create_main_interface(self):
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Label(toolbar, text="年月:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spinbox = ttk.Spinbox(toolbar, from_=2020, to=2030, textvariable=self.year_var, width=8)
        year_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="年").pack(side=tk.LEFT)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_spinbox = ttk.Spinbox(toolbar, from_=1, to=12, textvariable=self.month_var, width=5)
        month_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="月").pack(side=tk.LEFT)
        
        ttk.Button(toolbar, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=5)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.employee_tab = ttk.Frame(notebook)
        self.attendance_tab = ttk.Frame(notebook)
        self.performance_tab = ttk.Frame(notebook)
        self.payroll_tab = ttk.Frame(notebook)
        
        notebook.add(self.employee_tab, text="👥 员工管理")
        notebook.add(self.attendance_tab, text="📅 考勤管理")
        notebook.add(self.performance_tab, text="⭐ 绩效管理")
        notebook.add(self.payroll_tab, text="💰 工资核算")
        
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_performance_tab()
        self.create_payroll_tab()

    def create_employee_tab(self):
        toolbar = ttk.Frame(self.employee_tab, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="➕ 添加员工", command=self.add_employee_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="✏️ 编辑员工", command=self.edit_employee_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🗑️ 删除员工", command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📤 导出员工列表", command=self.export_employee_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(toolbar, text="搜索:").pack(side=tk.LEFT, padx=(20, 5))
        self.employee_search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.employee_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🔍", command=self.search_employee).pack(side=tk.LEFT)

        columns = ('工号', '姓名', '部门', '职位', '基本工资', '入职日期', '状态')
        self.employee_tree = ttk.Treeview(self.employee_tab, columns=columns, show='headings')
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.employee_tab, orient=tk.VERTICAL, command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        self.employee_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_employee_data()

    def create_attendance_tab(self):
        toolbar = ttk.Frame(self.attendance_tab, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="📥 导入考勤", command=self.import_attendance).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📋 生成模板", command=self.generate_attendance_template).pack(side=tk.LEFT, padx=5)

        columns = ('工号', '姓名', '部门', '工作天数', '迟到天数', '请假天数', '加班小时')
        self.attendance_tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings')
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.attendance_tab, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_attendance_data()

    def create_performance_tab(self):
        toolbar = ttk.Frame(self.performance_tab, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="📥 导入绩效", command=self.import_performance).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📋 生成模板", command=self.generate_performance_template).pack(side=tk.LEFT, padx=5)

        columns = ('工号', '姓名', '绩效分数', '绩效等级', '奖金公式')
        self.performance_tree = ttk.Treeview(self.performance_tab, columns=columns, show='headings')
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.performance_tab, orient=tk.VERTICAL, command=self.performance_tree.yview)
        self.performance_tree.configure(yscrollcommand=scrollbar.set)
        self.performance_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_performance_data()

    def create_payroll_tab(self):
        toolbar = ttk.Frame(self.payroll_tab, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="🧮 计算工资", command=self.calculate_all_salaries).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="📤 导出工资表", command=self.export_payroll).pack(side=tk.LEFT, padx=5)

        columns = ('工号', '姓名', '部门', '基本工资', '出勤工资', '绩效奖金',
                  '社保扣款', '公积金扣款', '总扣款', '应发工资', '实发工资')
        self.payroll_tree = ttk.Treeview(self.payroll_tab, columns=columns, show='headings')
        for col in columns:
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=100)
        
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
                emp['employee_id'], emp['name'], emp['department'], emp['position'],
                f"{emp['basic_salary']:.2f}", emp['entry_date'], emp['status']
            ))

    def add_employee_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加员工")
        dialog.geometry("400x500")
        
        fields = [
            ('员工工号', ''), ('姓名', ''), ('部门', ''), ('职位', ''),
            ('基本工资', '5000'), ('社保比例 (0-1)', '0.08'), ('公积金比例 (0-1)', '0.12'),
            ('医保比例 (0-1)', '0.02'), ('失业保险比例 (0-1)', '0.005'),
            ('入职日期', datetime.now().strftime('%Y-%m-%d'))
        ]
        
        entries = {}
        for i, (label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(dialog)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            entries[label] = entry

        def save_employee():
            try:
                employee_data = {
                    'employee_id': entries['员工工号'].get().strip(),
                    'name': entries['姓名'].get().strip(),
                    'department': entries['部门'].get().strip(),
                    'position': entries['职位'].get().strip(),
                    'basic_salary': float(entries['基本工资'].get()),
                    'base_social_rate': float(entries['社保比例 (0-1)'].get()),
                    'base_fund_rate': float(entries['公积金比例 (0-1)'].get()),
                    'base_medical_rate': float(entries['医保比例 (0-1)'].get()),
                    'unemployed_rate': float(entries['失业保险比例 (0-1)'].get()),
                    'entry_date': entries['入职日期'].get().strip()
                }
                if not employee_data['employee_id'] or not employee_data['name']:
                    messagebox.showerror("错误", "工号和姓名不能为空")
                    return
                if self.db.add_employee(employee_data):
                    messagebox.showinfo("成功", "员工添加成功")
                    self.load_employee_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "员工添加失败，工号可能已存在")
            except Exception as e:
                messagebox.showerror("错误", f"输入格式错误: {str(e)}")

        ttk.Button(dialog, text="保存", command=save_employee).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def edit_employee_dialog(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个员工")
            return
        
        employee_id = self.employee_tree.item(selected[0])['values'][0]
        employee = self.db.get_employee(employee_id)
        if not employee:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"编辑员工 - {employee['name']}")
        dialog.geometry("400x500")
        
        fields = [
            ('员工工号', employee['employee_id']), ('姓名', employee['name']),
            ('部门', employee['department']), ('职位', employee['position']),
            ('基本工资', str(employee['basic_salary'])),
            ('社保比例 (0-1)', str(employee['base_social_rate'])),
            ('公积金比例 (0-1)', str(employee['base_fund_rate'])),
            ('医保比例 (0-1)', str(employee['base_medical_rate'])),
            ('失业保险比例 (0-1)', str(employee['unemployed_rate'])),
            ('入职日期', employee['entry_date'])
        ]
        
        entries = {}
        for i, (label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            entry = ttk.Entry(dialog)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.EW)
            entries[label] = entry

        def update_employee():
            try:
                update_data = {
                    'name': entries['姓名'].get().strip(),
                    'department': entries['部门'].get().strip(),
                    'position': entries['职位'].get().strip(),
                    'basic_salary': float(entries['基本工资'].get()),
                    'base_social_rate': float(entries['社保比例 (0-1)'].get()),
                    'base_fund_rate': float(entries['公积金比例 (0-1)'].get()),
                    'base_medical_rate': float(entries['医保比例 (0-1)'].get()),
                    'unemployed_rate': float(entries['失业保险比例 (0-1)'].get()),
                    'entry_date': entries['入职日期'].get().strip()
                }
                if not update_data['name']:
                    messagebox.showerror("错误", "姓名不能为空")
                    return
                if self.db.update_employee(employee_id, update_data):
                    messagebox.showinfo("成功", "员工信息更新成功")
                    self.load_employee_data()
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "员工信息更新失败")
            except Exception as e:
                messagebox.showerror("错误", f"输入格式错误: {str(e)}")

        ttk.Button(dialog, text="更新", command=update_employee).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def delete_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个员工")
            return
        
        employee_id = self.employee_tree.item(selected[0])['values'][0]
        employee_name = self.employee_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除员工 {employee_name} (工号: {employee_id}) 吗？"):
            if self.db.delete_employee(employee_id):
                messagebox.showinfo("成功", "员工删除成功")
                self.load_employee_data()
            else:
                messagebox.showerror("错误", "员工删除失败")

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
                    emp['employee_id'], emp['name'], emp['department'], emp['position'],
                    f"{emp['basic_salary']:.2f}", emp['entry_date'], emp['status']
                ))

    def export_employee_list(self):
        result = self.excel_handler.export_employee_list()
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

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
                    record['employee_id'], employee['name'], employee['department'],
                    record['work_days'], record['late_days'], record['leave_days'], record['overtime_hours']
                ))

    def import_attendance(self):
        file_path = filedialog.askopenfilename(
            title="选择考勤 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        result = self.excel_handler.import_attendance_from_excel(file_path, year, month)
        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self.load_attendance_data()
        else:
            messagebox.showerror("错误", result['message'])

    def generate_attendance_template(self):
        result = self.excel_handler.generate_attendance_template()
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

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
                    emp['employee_id'], emp['name'],
                    performance['score'], performance['grade'], performance['bonus_formula']
                ))
            else:
                self.performance_tree.insert('', tk.END, values=(
                    emp['employee_id'], emp['name'], '', '', ''
                ))

    def import_performance(self):
        file_path = filedialog.askopenfilename(
            title="选择绩效 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        result = self.excel_handler.import_performance_from_excel(file_path, year, month)
        if result['success']:
            messagebox.showinfo("成功", result['message'])
            self.load_performance_data()
        else:
            messagebox.showerror("错误", result['message'])

    def generate_performance_template(self):
        result = self.excel_handler.generate_performance_template()
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

    def load_payroll_data(self):
        for item in self.payroll_tree.get_children():
            self.payroll_tree.delete(item)
        
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        payroll_records = self.db.get_payroll(year, month)
        for record in payroll_records:
            self.payroll_tree.insert('', tk.END, values=(
                record['employee_id'], record['name'], record['department'],
                f"{record['basic_salary']:.2f}", f"{record['attendance_salary']:.2f}",
                f"{record['performance_bonus']:.2f}", f"{record['social_deduction']:.2f}",
                f"{record['fund_deduction']:.2f}", f"{record['total_deduction']:.2f}",
                f"{record['gross_salary']:.2f}", f"{record['net_salary']:.2f}"
            ))

    def calculate_all_salaries(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        employees = self.db.get_all_employees()
        if not employees:
            messagebox.showwarning("提示", "没有员工数据，请先添加员工")
            return
        
        if not messagebox.askyesno("确认", f"确定要计算 {year}年{month}月 所有员工的工资吗？"):
            return
        
        success_count = 0
        failed_count = 0
        
        for emp in employees:
            result = self.db.calculate_salary(emp['employee_id'], year, month)
            if result:
                success_count += 1
            else:
                failed_count += 1
        
        messagebox.showinfo("完成", f"工资计算完成\n成功: {success_count} 人\n失败: {failed_count} 人")
        self.load_payroll_data()

    def export_payroll(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        result = self.excel_handler.export_payroll_to_excel(year, month)
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

    def refresh_data(self):
        self.current_year = int(self.year_var.get())
        self.current_month = int(self.month_var.get())
        self.load_employee_data()
        self.load_attendance_data()
        self.load_performance_data()
        self.load_payroll_data()
        messagebox.showinfo("提示", "数据刷新完成")

def main():
    root = tk.Tk()
    app = PayrollSystemGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
