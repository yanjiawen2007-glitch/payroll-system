import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from database import PayrollDatabase
from excel_handler import ExcelHandler
from ollama_analyzer import OllamaAnalyzer
import platform


class ModernStyle:
    """Apple风格样式配置"""
    
    # 配色方案
    COLORS = {
        'bg_primary': '#FFFFFF',      # 主背景
        'bg_secondary': '#F5F5F7',    # 次要背景
        'bg_accent': '#E8E8ED',      # 强调背景
        'text_primary': '#1D1D1F',   # 主文本
        'text_secondary': '#86868B',  # 次要文本
        'accent_blue': '#007AFF',      # 苹果蓝
        'accent_green': '#34C759',    # 苹果绿
        'accent_red': '#FF3B30',      # 苹果红
        'border': '#E5E5EA',          # 边框
        'shadow': 'rgba(0,0,0,0.1)',    # 阴影
    }
    
    # 字体配置
    FONTS = {
        'title': ('SF Pro Display', -size, 'bold') if platform.system() == 'Darwin' else ('Segoe UI', 14, 'bold'),
        'header': ('SF Pro Text', -size, 'semibold') if platform.system() == 'Darwin' else ('Segoe UI Semibold', 11, 'normal'),
        'body': ('SF Pro Text', -size) if platform.system() == 'Darwin' else ('Segoe UI', 10, 'normal'),
        'small': ('SF Pro Text', -size-1) if platform.system() == 'Darwin' else ('Segoe UI', 9, 'normal'),
    }


class PayrollSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll Anytime")
        self.root.geometry("1400x800")
        self.root.configure(bg=ModernStyle.COLORS['bg_primary'])
        
        # 设置窗口图标（如果有）
        try:
            if platform.system() == 'Windows':
                self.root.iconbitmap('icon.ico') if False else None
        except:
            pass
        
        self.db = PayrollDatabase()
        self.excel_handler = ExcelHandler(self.db)
        self.ollama_analyzer = OllamaAnalyzer(self.db)
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        self.setup_styles()
        self.create_main_interface()

    def setup_styles(self):
        """配置Ttk样式"""
        style = ttk.Style()
        
        # 配置Notebook标签
        style.configure('TNotebook', 
                      background=ModernStyle.COLORS['bg_primary'],
                      borderwidth=0)
        
        style.configure('TNotebook.Tab',
                      background=ModernStyle.COLORS['bg_secondary'],
                      foreground=ModernStyle.COLORS['text_secondary'],
                      padding=[24, 12],
                      font=ModernStyle.FONTS['body'])
        
        style.map('TNotebook.Tab',
                  background=[('selected', ModernStyle.COLORS['bg_primary'])],
                  foreground=[('selected', ModernStyle.COLORS['accent_blue'])])
        
        # 配置Treeview
        style.configure('Treeview',
                      background=ModernStyle.COLORS['bg_primary'],
                      foreground=ModernStyle.COLORS['text_primary'],
                      font=ModernStyle.FONTS['body'],
                      rowheight=30,
                      borderwidth=0)
        
        style.configure('Treeview.Heading',
                      background=ModernStyle.COLORS['bg_secondary'],
                      foreground=ModernStyle.COLORS['text_primary'],
                      font=ModernStyle.FONTS['header'])
        
        # 配置Button
        style.configure('Modern.TButton',
                      background=ModernStyle.COLORS['accent_blue'],
                      foreground='white',
                      borderwidth=0,
                      padding=[20, 10],
                      font=ModernStyle.FONTS['body'])
        
        style.map('Modern.TButton',
                  background=[('active', '#0063D1')])
        
        # 配置Secondary.TButton
        style.configure('Secondary.TButton',
                      background=ModernStyle.COLORS['bg_secondary'],
                      foreground=ModernStyle.COLORS['text_primary'],
                      borderwidth=0,
                      padding=[20, 10],
                      font=ModernStyle.FONTS['body'])
        
        style.map('Secondary.TButton',
                  background=[('active', ModernStyle.COLORS['bg_accent'])])
        
        # 配置Frame
        style.configure('Card.TFrame',
                      background=ModernStyle.COLORS['bg_primary'],
                      relief='flat')

    def create_main_interface(self):
        """创建主界面 - Apple风格"""
        # 顶部导航栏
        self.create_navbar()
        
        # 主内容区域
        main_container = ttk.Frame(self.root, style='Card.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 创建标签
        self.create_notebook(main_container)

    def create_navbar(self):
        """创建导航栏"""
        navbar = tk.Frame(self.root, bg=ModernStyle.COLORS['bg_primary'], height=60)
        navbar.pack(fill=tk.X)
        navbar.pack_propagate(False)
        
        # Logo/标题
        title_frame = tk.Frame(navbar, bg=ModernStyle.COLORS['bg_primary'])
        title_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        title_label = tk.Label(title_frame, 
                              text="Payroll Anytime",
                              font=ModernStyle.FONTS['title'],
                              bg=ModernStyle.COLORS['bg_primary'],
                              fg=ModernStyle.COLORS['text_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                text="Simple • Intuitive • Powerful",
                                font=ModernStyle.FONTS['small'],
                                bg=ModernStyle.COLORS['bg_primary'],
                                fg=ModernStyle.COLORS['text_secondary'])
        subtitle_label.pack()

        # 年月选择器
        date_selector = tk.Frame(navbar, bg=ModernStyle.COLORS['bg_primary'])
        date_selector.pack(side=tk.LEFT, padx=40, pady=15)
        
        tk.Label(date_selector, text="Year", 
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['bg_primary'],
                fg=ModernStyle.COLORS['text_secondary']).pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_spinbox = ttk.Spinbox(date_selector, 
                                    from_=2020, 
                                    to=2030, 
                                    textvariable=self.year_var,
                                    width=10,
                                    font=ModernStyle.FONTS['body'])
        year_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_selector, text="Month",
                font=ModernStyle.FONTS['body'],
                bg=ModernStyle.COLORS['bg_primary'],
                fg=ModernStyle.COLORS['text_secondary']).pack(side=tk.LEFT, padx=5)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_spinbox = ttk.Spinbox(date_selector,
                                     from_=1,
                                     to=12,
                                     textvariable=self.month_var,
                                     width=8,
                                     font=ModernStyle.FONTS['body'])
        month_spinbox.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = tk.Button(navbar,
                              text="↻ Refresh",
                              command=self.refresh_data,
                              bg=ModernStyle.COLORS['bg_secondary'],
                              fg=ModernStyle.COLORS['text_primary'],
                              borderwidth=0,
                              padx=20,
                              pady=8,
                              font=ModernStyle.FONTS['body'],
                              cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=30, pady=15)

    def create_notebook(self, parent):
        """创建标签页"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页
        self.employee_tab = ttk.Frame(notebook)
        self.attendance_tab = ttk.Frame(notebook)
        self.performance_tab = ttk.Frame(notebook)
        self.payroll_tab = ttk.Frame(notebook)
        self.ai_tab = ttk.Frame(notebook)
        
        notebook.add(self.employee_tab, text="  👥 员工  ")
        notebook.add(self.attendance_tab, text="  📅 考勤  ")
        notebook.add(self.performance_tab, text="  ⭐ 绩效  ")
        notebook.add(self.payroll_tab, text="  💰 工资  ")
        notebook.add(self.ai_tab, text="  🤖 AI  ")
        
        self.create_employee_tab()
        self.create_attendance_tab()
        self.create_performance_tab()
        self.create_payroll_tab()
        self.create_ai_tab()

    def create_employee_tab(self):
        """员工管理标签页 - 简洁风格"""
        # 工具栏
        toolbar = tk.Frame(self.employee_tab, bg=ModernStyle.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=15)
        
        # 主要按钮组
        btn_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        btn_frame.pack(side=tk.LEFT)
        
        self.create_modern_button(btn_frame, "+ Add", "modern", self.add_employee_dialog)
        self.create_modern_button(btn_frame, "✏️ Edit", "secondary", self.edit_employee_dialog)
        self.create_modern_button(btn_frame, "🗑️ Delete", "secondary", self.delete_employee)
        self.create_modern_button(btn_frame, "📤 Export", "secondary", self.export_employee_list)
        
        # 搜索框
        search_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        search_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(search_frame, text="🔍",
                bg=ModernStyle.COLORS['bg_primary'],
                fg=ModernStyle.COLORS['text_secondary'],
                font=ModernStyle.FONTS['body']).pack(side=tk.LEFT, padx=5)
        
        self.employee_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                             textvariable=self.employee_search_var,
                             font=ModernStyle.FONTS['body'],
                             relief='flat',
                             bg=ModernStyle.COLORS['bg_secondary'],
                             fg=ModernStyle.COLORS['text_primary'],
                             width=25,
                             padx=12,
                             pady=8)
        search_entry.pack(side=tk.LEFT)
        
        # 数据表格
        self.create_employee_table()

    def create_attendance_tab(self):
        """考勤管理标签页"""
        toolbar = tk.Frame(self.attendance_tab, bg=ModernStyle.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        btn_frame.pack(side=tk.LEFT)
        
        self.create_modern_button(btn_frame, "📥 Import", "modern", self.import_attendance)
        self.create_modern_button(btn_frame, "📋 Template", "secondary", self.generate_attendance_template)
        
        self.create_attendance_table()

    def create_performance_tab(self):
        """绩效管理标签页"""
        toolbar = tk.Frame(self.performance_tab, bg=ModernStyle.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        btn_frame.pack(side=tk.LEFT)
        
        self.create_modern_button(btn_frame, "📥 Import", "modern", self.import_performance)
        self.create_modern_button(btn_frame, "📋 Template", "secondary", self.generate_performance_template)
        
        self.create_performance_table()

    def create_payroll_tab(self):
        """工资核算标签页"""
        toolbar = tk.Frame(self.payroll_tab, bg=ModernStyle.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        btn_frame.pack(side=tk.LEFT)
        
        self.create_modern_button(btn_frame, "🧮 Calculate", "modern", self.calculate_all_salaries)
        self.create_modern_button(btn_frame, "📤 Export", "secondary", self.export_payroll)
        
        self.create_payroll_table()

    def create_ai_tab(self):
        """AI分析标签页"""
        toolbar = tk.Frame(self.ai_tab, bg=ModernStyle.COLORS['bg_primary'])
        toolbar.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(toolbar, bg=ModernStyle.COLORS['bg_primary'])
        btn_frame.pack(side=tk.LEFT)
        
        self.create_modern_button(btn_frame, "📊 Analysis", "modern", self.analyze_overall)
        self.create_modern_button(btn_frame, "💬 Employee", "secondary", self.analyze_employee)
        self.create_modern_button(btn_frame, "📈 Trend", "secondary", self.predict_trend)
        self.create_modern_button(btn_frame, "✍️ Review", "secondary", self.generate_performance_review)
        
        # AI输出区域
        output_frame = tk.Frame(self.ai_tab, bg=ModernStyle.COLORS['bg_secondary'])
        output_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        self.ai_output = tk.Text(output_frame,
                               wrap=tk.WORD,
                               padx=20,
                               pady=20,
                               font=ModernStyle.FONTS['body'],
                               bg=ModernStyle.COLORS['bg_primary'],
                               fg=ModernStyle.COLORS['text_primary'],
                               relief='flat',
                               borderwidth=0)
        self.ai_output.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.ai_output.yview)
        self.ai_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_modern_button(self, parent, text, style_type, command):
        """创建现代风格按钮"""
        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       bg=ModernStyle.COLORS['accent_blue'] if style_type == "modern" else ModernStyle.COLORS['bg_secondary'],
                       fg='white' if style_type == "modern" else ModernStyle.COLORS['text_primary'],
                       borderwidth=0,
                       padx=20,
                       pady=10,
                       font=ModernStyle.FONTS['body'],
                       cursor='hand2',
                       relief='flat')
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def create_employee_table(self):
        """创建员工数据表格"""
        columns = ('工号', '姓名', '部门', '职位', '基本工资', '入职日期', '状态')
        self.employee_tree = ttk.Treeview(self.employee_tab, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=120, anchor='w')
        
        self.employee_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_employee_data()

    def create_attendance_table(self):
        """创建考勤数据表格"""
        columns = ('工号', '姓名', '部门', '工作天数', '迟到天数', '请假天数', '加班小时')
        self.attendance_tree = ttk.Treeview(self.attendance_tab, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
            self.attendance_tree.column(col, width=100, anchor='w')
        
        self.attendance_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_attendance_data()

    def create_performance_table(self):
        """创建绩效数据表格"""
        columns = ('工号', '姓名', '绩效分数', '绩效等级', '奖金公式')
        self.performance_tree = ttk.Treeview(self.performance_tab, columns=columns, show='headings', style='Treeview')
        
        for col in columns:
            self.performance_tree.heading(col, text=col)
            self.performance_tree.column(col, width=140, anchor='w')
        
        self.performance_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.load_performance_data()

    def create_payroll_table(self):
        """创建工资数据表格"""
        columns = ('工号', '姓名', '部门', '基本工资', '出勤工资', '绩效奖金',
                  '社保扣款', '公积金扣款', '总扣款', '应发工资', '实发工资')
        self.payroll_tree = ttk.Treeview(self.payroll_tab, columns=columns, show='headings', style='Treeview')
        
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
        dialog.title("Add Employee - Payroll Anytime")
        dialog.geometry("450x550")
        dialog.configure(bg=ModernStyle.COLORS['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg=ModernStyle.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(main_frame, text="Add New Employee",
                font=ModernStyle.FONTS['header'],
                bg=ModernStyle.COLORS['bg_primary'],
                fg=ModernStyle.COLORS['text_primary']).pack(pady=(0, 20))

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
            tk.Label(main_frame, text=label,
                   font=ModernStyle.FONTS['body'],
                   bg=ModernStyle.COLORS['bg_primary'],
                   fg=ModernStyle.COLORS['text_secondary']).grid(
                       row=i, column=0, padx=(0, 15), pady=10, sticky='w')
            
            entry = tk.Entry(main_frame,
                         font=ModernStyle.FONTS['body'],
                         bg=ModernStyle.COLORS['bg_secondary'],
                         fg=ModernStyle.COLORS['text_primary'],
                         relief='flat',
                         borderwidth=0,
                         padx=15,
                         pady=8)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=(0, 0), pady=10, sticky='ew')
            entries[label] = entry

        button_frame = tk.Frame(main_frame, bg=ModernStyle.COLORS['bg_primary'])
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=30, sticky='ew')

        save_btn = tk.Button(button_frame, text="Save Employee", command=dialog.destroy,
                          bg=ModernStyle.COLORS['accent_blue'],
                          fg='white',
                          borderwidth=0,
                          padx=30,
                          pady=12,
                          font=ModernStyle.FONTS['body'],
                          cursor='hand2',
                          relief='flat')
        save_btn.pack(side=tk.RIGHT, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                           bg=ModernStyle.COLORS['bg_secondary'],
                           fg=ModernStyle.COLORS['text_primary'],
                           borderwidth=0,
                           padx=30,
                           py=12,
                           font=ModernStyle.FONTS['body'],
                           cursor='hand2',
                           relief='flat')
        cancel_btn.pack(side=tk.RIGHT)

    def edit_employee_dialog(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an employee")
            return

        messagebox.showinfo("Info", "Edit feature coming soon")

    def delete_employee(self):
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an employee")
            return

        employee_id = self.employee_tree.item(selected[0])['values'][0]
        employee_name = self.employee_tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Confirm", f"Delete {employee_name}?"):
            if self.db.delete_employee(employee_id):
                messagebox.showinfo("Success", "Employee deleted")
                self.load_employee_data()

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
        messagebox.showinfo("Info", "Import feature coming soon")

    def generate_attendance_template(self):
        result = self.excel_handler.generate_attendance_template()
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

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
        messagebox.showinfo("Info", "Import feature coming soon")

    def generate_performance_template(self):
        result = self.excel_handler.generate_performance_template()
        if result['success']:
            messagebox.showinfo("Success", f"{result['message']}\n{result['file_path']}")
        else:
            messagebox.showerror("Error", result['message'])

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
            messagebox.showinfo("Info", "No employees found")
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
        messagebox.showinfo("Done", "Data refreshed")

    # ==================== AI 分析 ====================

    def analyze_overall(self):
        year = int(self.year_var.get())
        month = int(self.month_var.get())

        self.ai_output.delete(1.0, tk.END)
        self.ai_output.insert(tk.END, "Analyzing...\n")
        self.ai_output.insert(tk.END, f"Year: {year}, Month: {month}\n\n")
        self.root.update()

        result = self.ollama_analyzer.analyze_salary_data(year, month)
        
        self.ai_output.insert(tk.END, "\n" + "─" * 50 + "\n")
        if not result:
            self.ai_output.insert(tk.END, "No data received\n")
        elif "failed" in result.lower():
            self.ai_output.insert(tk.END, f"Error: {result}\n")
        else:
            self.ai_output.insert(tk.END, result + "\n")
        
        self.ai_output.insert(tk.END, "─" * 50 + "\n")
        self.ai_output.insert(tk.END, "✓ Done\n")
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
