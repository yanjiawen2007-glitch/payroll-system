import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from database import PayrollDatabase
from excel_handler import ExcelHandler
from ollama_analyzer import OllamaAnalyzer


class PayrollSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("工资核算系统 - Payroll Anytime")
        self.root.geometry("1400x850")
        self.root.configure(bg='#FFFFFF')
        
        self.db = PayrollDatabase()
        self.excel_handler = ExcelHandler(self.db)
        self.ollama_analyzer = OllamaAnalyzer(self.db)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        self.create_main_interface()

    def create_main_interface(self):
        navbar = tk.Frame(self.root, bg='#FFFFFF', height=60)
        navbar.pack(fill=tk.X)
        navbar.pack_propagate(False)
        
        title_frame = tk.Frame(navbar, bg='#FFFFFF')
        title_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        title_label = tk.Label(title_frame, 
                              text="工资核算系统",
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
        
        tk.Label(date_selector, text="年", 
                font=('Segoe UI', 10),
                bg='#FFFFFF',
                fg='#86868B').pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spinbox = ttk.Spinbox(date_selector, from_=2020, to=2030, textvariable=self.year_var, width=10)
        year_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_selector, text="月",
                font=('Segoe UI', 10),
                bg='#FFFFFF',
                fg='#86868B').pack(side=tk.LEFT, padx=5)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_spinbox = ttk.Spinbox(date_selector, from_=1, to=12, textvariable=self.month_var, width=8)
        month_spinbox.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = tk.Button(navbar,
                              text="刷新",
                              command=self.refresh_data,
                              bg='#F5F5F7',
                              fg='#1D1D1F',
                              borderwidth=0,
                              padx=20,
                              pady=8,
                              font=('Segoe UI', 10))
        refresh_btn.pack(side=tk.RIGHT, padx=30, pady=15)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.employee_tab = ttk.Frame(notebook)
        self.attendance_tab = ttk.Frame(notebook)
        self.performance_tab = ttk.Frame(notebook)
        self.payroll_tab = ttk.Frame(notebook)
        self.ai_tab = ttk.Frame(notebook)
        
        notebook.add(self.employee_tab, text="  👥 员工管理  ")
        notebook.add(self.attendance_tab, text="  📅 考勤管理  ")
        notebook.add(self.performance_tab, text="  ⭐ 绩效管理  ")
        notebook.add(self.payroll_tab, text="  💰 工资核算  ")
        notebook.add(self.ai_tab, text="  🤖 AI 分析  ")
        
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_performance_tab()
        self.create_payroll_tab()
        self.create_ai_tab()

    def create_employee_tab(self):
        toolbar = tk.Frame(self.employee_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, "+ 添加员工", "#007AFF", self.add_employee_dialog)
        self.create_button(btn_frame, "✏️ 编辑员工", "#F5F5F7", self.edit_employee_dialog)
        self.create_button(btn_frame, "🗑️ 删除员工", "#F5F5F7", self.delete_employee)
        self.create_button(btn_frame, "📤 导出员工列表", "#F5F5F7", self.export_employee_list)
        
        search_frame = tk.Frame(toolbar, bg='#FFFFFF')
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(search_frame, text="🔍",
                bg='#FFFFFF',
                fg='#86868B',
                font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)
        
        self.employee_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                             textvariable=self.employee_search_var,
                             width=20,
                             font=('Segoe UI', 10),
                             bg='#F5F5F7',
                             fg='#1D1D1F',
                             relief='flat')
        search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="搜索", command=self.search_employee, bg='#007AFF', fg='white', borderwidth=0, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=5)

        self.create_employee_table()

    def create_attendance_tab(self):
        toolbar = tk.Frame(self.attendance_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, "📥 导入考勤", "#007AFF", self.import_attendance)
        self.create_button(btn_frame, "📋 生成模板", "#F5F5F7", self.generate_attendance_template)
        
        self.create_attendance_table()

    def create_performance_tab(self):
        toolbar = tk.Frame(self.performance_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, "📥 导入绩效", "#007AFF", self.import_performance)
        self.create_button(btn_frame, "📋 生成模板", "#F5F5F7", self.generate_performance_template)
        
        self.create_performance_table()

    def create_payroll_tab(self):
        toolbar = tk.Frame(self.payroll_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg='#FFFFFF')
        btn_frame.pack(side=tk.LEFT)
        
        self.create_button(btn_frame, "🧮 计算工资", "#007AFF", self.calculate_all_salaries)
        self.create_button(btn_frame, "📤 导出工资表", "#F5F5F7", self.export_payroll)
        
        self.create_payroll_table()

    def create_ai_tab(self):
        toolbar = tk.Frame(self.ai_tab, bg='#FFFFFF')
        toolbar.pack(fill=tk.X, pady=15)
        
        tk.Label(toolbar, text="选择功能：", font=('Segoe UI', 10, 'bold'), bg='#FFFFFF', fg='#1D1D1F').pack(side=tk.LEFT, padx=10)
        
        functions = [
            ("📊 分析整体工资数据", self.analyze_overall),
            ("💬 分析单个员工工资", self.analyze_employee),
            ("📈 预测工资趋势", self.predict_trend),
            ("✍️ 生成绩效评估报告", self.generate_performance_review)
        ]
        
        for text, command in functions:
            self.create_button(toolbar, text, "#007AFF", command)
        
        ttk.Separator(self.ai_tab, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.ai_output = tk.Text(self.ai_tab, height=20, width=100, wrap=tk.WORD, padx=10, pady=10, font=('Segoe UI', 10), bg='#FFFFFF', fg='#1D1D1F')
        self.ai_output.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.ai_tab, orient=tk.VERTICAL, command=self.ai_output.yview)
        self.ai_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_button(self, parent, text, bg_color, command):
        """创建按钮 - 标准参数"""
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=bg_color,
                       fg='white' if bg_color == '#007AFF' else '#1D1D1F',
                       borderwidth=0,
                       padx=20,
                       pady=10,
                       font=('Segoe UI', 10))
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def create_employee_table(self):
        columns = ('工号', '姓名', '部门', '职位', '基本工资', '入职日期', '状态')
        self.employee_tree = ttk.Treeview(self.employee_tab, columns=columns, show='headings')
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120, anchor='w')
        
        self.employee_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_employee_data()

    def create_attendance_table(self):
        columns = ('工号', '姓名', '部门', '工作天数', '迟到天数', '请假天数', '加班小时')
        self.attendance_tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings')
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=100, anchor='w')
        
        self.attendance_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_attendance_data()

    def create_performance_table(self):
        columns = ('工号', '姓名', '绩效分数', '绩效等级', '奖金公式')
        self.performance_tree = ttk.Treeview(self.performance_tab, columns=columns, show='headings')
        
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=140, anchor='w')
        
        self.performance_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_performance_data()

    def create_payroll_table(self):
        columns = ('工号', '姓名', '部门', '基本工资', '出勤工资', '绩效奖金',
                  '社保扣款', '公积金扣款', '总扣款', '应发工资', '实发工资')
        self.payroll_tree = ttk.Treeview(self.payroll_tab, columns=columns, show='headings')
        
        for col in columns:
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=100, anchor='w')
        
        self.payroll_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_payroll_data()

    # ==================== 员工管理 ====================

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

    def add_employee_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加员工 - 工资核算系统")
        dialog.geometry("450x500")
        dialog.configure(bg='#FFFFFF')
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg='#FFFFFF')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(main_frame, text="添加新员工",
                font=('Segoe UI', 12, 'bold'),
                bg='#FFFFFF',
                fg='#1D1D1F').pack(pady=(0, 20))

        fields = [
            ('员工工号', ''),
            ('姓名', ''),
            ('部门', ''),
            ('职位', ''),
            ('基本工资', '5000'),
            ('社保比例 (0-1)', '0.08'),
            ('公积金比例 (0-1)', '0.12'),
            ('医保比例 (0-1)', '0.02'),
            ('失业保险比例 (0-1)', '0.005'),
            ('入职日期', datetime.now().strftime('%Y-%m-%d'))
        ]

        entries = {}
        for i, (label, default) in enumerate(fields):
            tk.Label(main_frame, text=label,
                   font=('Segoe UI', 10),
                   bg='#FFFFFF',
                   fg='#86868B').grid(row=i, column=0, padx=(0, 15), pady=10, sticky='w')
            entry = tk.Entry(main_frame,
                         font=('Segoe UI', 10),
                         bg='#F5F5F7',
                         fg='#1D1D1F')
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=(0, 0), pady=10, sticky='ew')
            entries[label] = entry

        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=30)

        save_btn = tk.Button(button_frame, text="保存", command=self.save_employee, dialog=dialog, entries=entries, bg='#007AFF', fg='white', borderwidth=0, font=('Segoe UI', 10))
        save_btn.pack(side=tk.RIGHT)

    def save_employee(self, dialog, entries):
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

    def edit_employee_dialog(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个员工")
            return

        employee_id = self.employee_tree.item(selected[0])['values'][0]
        employee = self.db.get_employee(employee_id)

        if not employee:
            return

        messagebox.showinfo("提示", "编辑功能即将推出")

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
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

    # ==================== 考勤管理 ====================

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

    def import_attendance(self):
        messagebox.showinfo("提示", "导入功能即将推出")

    def generate_attendance_template(self):
        result = self.excel_handler.generate_attendance_template()
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

    # ==================== 绩效管理 ====================

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

    def import_performance(self):
        messagebox.showinfo("提示", "导入功能即将推出")

    def generate_performance_template(self):
        result = self.excel_handler.generate_performance_template()
        if result['success']:
            messagebox.showinfo("成功", f"{result['message']}\n文件路径: {result['file_path']}")
        else:
            messagebox.showerror("错误", result['message'])

    # ==================== 工资核算 ====================

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

    def calculate_all_salaries(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        employees = self.db.get_all_employees()

        if not employees:
            messagebox.showwarning("提示", "没有员工数据，请先添加员工")
            return

        if messagebox.askyesno("确认", f"确定要计算 {year}年{month}月 所有员工的工资吗？"):
            success = 0
            failed = 0
            
            for emp in employees:
                if self.db.calculate_salary(emp['employee_id'], year, month):
                    success += 1
                else:
                    failed += 1
            
            messagebox.showinfo("完成", f"工资计算完成\n成功: {success} 人\n失败: {failed} 人")

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

    # ==================== AI 分析 ====================

    def analyze_overall(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        self.ai_output.delete(1.0, tk.END)
        self.ai_output.insert(tk.END, "正在分析工资数据...\n")
        self.ai_output.insert(tk.END, f"年份: {year}年，月份: {month}月\n")
        self.ai_output.insert(tk.END, "-" * 50 + "\n")
        self.root.update()

        result = self.ollama_analyzer.analyze_salary_data(year, month)

        self.ai_output.insert(tk.END, "\n" + "-" * 50 + "\n")
        if not result:
            self.ai_output.insert(tk.END, "未获取到分析结果\n")
        elif "调用失败" in result:
            self.ai_output.insert(tk.END, f"错误: {result}\n")
        else:
            self.ai_output.insert(tk.END, result)

        self.ai_output.insert(tk.END, "\n" + "-" * 50 + "\n")
        self.ai_output.insert(tk.END, "✅ 分析完毕！\n")
        self.ai_output.see(tk.END)

    def analyze_employee(self):
        messagebox.showinfo("提示", "单个员工分析功能即将推出")

    def predict_trend(self):
        messagebox.showinfo("提示", "趋势预测功能即将推出")

    def generate_performance_review(self):
        messagebox.showinfo("提示", "绩效评估报告生成功能即将推出")


def main():
    root = tk.Tk()
    app = PayrollSystemGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
