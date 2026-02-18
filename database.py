import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class PayrollDatabase:
    def __init__(self, db_path: str = 'data/payroll.db'):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            basic_salary REAL NOT NULL,
            base_social_rate REAL DEFAULT 0.08,
            base_fund_rate REAL DEFAULT 0.12,
            base_medical_rate REAL DEFAULT 0.02,
            unemployed_rate REAL DEFAULT 0.005,
            entry_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            work_days REAL DEFAULT 22,
            late_days REAL DEFAULT 0,
            leave_days REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            UNIQUE(employee_id, year, month)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            score REAL NOT NULL,
            grade TEXT,
            bonus_formula TEXT DEFAULT 'base_salary * score * 0.01',
            bonus_amount REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            UNIQUE(employee_id, year, month)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            basic_salary REAL NOT NULL,
            attendance_salary REAL DEFAULT 0,
            performance_bonus REAL DEFAULT 0,
            social_deduction REAL DEFAULT 0,
            fund_deduction REAL DEFAULT 0,
            medical_deduction REAL DEFAULT 0,
            unemployed_deduction REAL DEFAULT 0,
            total_deduction REAL DEFAULT 0,
            gross_salary REAL DEFAULT 0,
            net_salary REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            UNIQUE(employee_id, year, month)
        )''')
        
        conn.commit()
        conn.close()

    def add_employee(self, employee_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO employees (
                employee_id, name, department, position, basic_salary,
                base_social_rate, base_fund_rate, base_medical_rate,
                unemployed_rate, entry_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                employee_data['employee_id'],
                employee_data['name'],
                employee_data.get('department', ''),
                employee_data.get('position', ''),
                employee_data['basic_salary'],
                employee_data.get('base_social_rate', 0.08),
                employee_data.get('base_fund_rate', 0.12),
                employee_data.get('base_medical_rate', 0.02),
                employee_data.get('unemployed_rate', 0.005),
                employee_data.get('entry_date', ''),
                employee_data.get('status', 'active')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加员工失败: {e}")
            return False

    def get_all_employees(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE status = "active"')
        employees = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return employees

    def get_employee(self, employee_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def update_employee(self, employee_id: str, update_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [employee_id]
            cursor.execute(f'UPDATE employees SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE employee_id = ?', values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新员工失败: {e}")
            return False

    def delete_employee(self, employee_id: str) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE employees SET status = "inactive" WHERE employee_id = ?', (employee_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除员工失败: {e}")
            return False

    def add_attendance(self, attendance_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO attendance (
                employee_id, year, month, work_days, late_days,
                leave_days, overtime_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                attendance_data['employee_id'],
                attendance_data['year'],
                attendance_data['month'],
                attendance_data.get('work_days', 22),
                attendance_data.get('late_days', 0),
                attendance_data.get('leave_days', 0),
                attendance_data.get('overtime_hours', 0)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加考勤失败: {e}")
            return False

    def get_attendance(self, employee_id: str, year: int, month: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM attendance WHERE employee_id = ? AND year = ? AND month = ?', (employee_id, year, month))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_all_attendance(self, year: int, month: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM attendance WHERE year = ? AND month = ?', (year, month))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def add_performance(self, performance_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO performance (
                employee_id, year, month, score, grade, bonus_formula
            ) VALUES (?, ?, ?, ?, ?, ?)''', (
                performance_data['employee_id'],
                performance_data['year'],
                performance_data['month'],
                performance_data['score'],
                performance_data.get('grade', ''),
                performance_data.get('bonus_formula', 'base_salary * score * 0.01')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加绩效失败: {e}")
            return False

    def get_performance(self, employee_id: str, year: int, month: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM performance WHERE employee_id = ? AND year = ? AND month = ?', (employee_id, year, month))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def calculate_salary(self, employee_id: str, year: int, month: int) -> Optional[Dict]:
        employee = self.get_employee(employee_id)
        if not employee:
            return None

        attendance = self.get_attendance(employee_id, year, month)
        performance = self.get_performance(employee_id, year, month)

        basic_salary = employee['basic_salary']
        work_days = attendance['work_days'] if attendance else 22
        daily_salary = basic_salary / 22
        leave_days = attendance['leave_days'] if attendance else 0
        late_days = attendance['late_days'] if attendance else 0

        attendance_deduction = (leave_days * daily_salary * 0.3) + (late_days * daily_salary * 0.1)
        attendance_salary = basic_salary - attendance_deduction

        overtime_hours = attendance['overtime_hours'] if attendance else 0
        hourly_salary = basic_salary / 22 / 8
        overtime_pay = overtime_hours * hourly_salary * 1.5

        bonus = 0
        if performance:
            try:
                safe_locals = {'base_salary': basic_salary, 'score': performance['score'], 'grade': performance['grade'], 'work_days': work_days, 'overtime_hours': overtime_hours}
                bonus = eval(performance['bonus_formula'], {'__builtins__': {}}, safe_locals)
            except:
                bonus = 0

        social_base = min(basic_salary, 30000)
        social_deduction = social_base * employee['base_social_rate']
        fund_deduction = social_base * employee['base_fund_rate']
        medical_deduction = social_base * employee['base_medical_rate']
        unemployed_deduction = social_base * employee['unemployed_rate']

        total_deduction = social_deduction + fund_deduction + medical_deduction + unemployed_deduction
        gross_salary = attendance_salary + overtime_pay + bonus

        threshold = 5000
        taxable_income = max(0, gross_salary - total_deduction - threshold)
        if taxable_income <= 3000:
            tax_rate = 0.03
        elif taxable_income <= 12000:
            tax_rate = 0.1
        elif taxable_income <= 25000:
            tax_rate = 0.2
        elif taxable_income <= 35000:
            tax_rate = 0.25
        elif taxable_income <= 55000:
            tax_rate = 0.3
        elif taxable_income <= 80000:
            tax_rate = 0.35
        else:
            tax_rate = 0.45

        tax = taxable_income * tax_rate
        net_salary = gross_salary - total_deduction - tax

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO payroll (
            employee_id, year, month, basic_salary, attendance_salary,
            performance_bonus, social_deduction, fund_deduction,
            medical_deduction, unemployed_deduction, total_deduction,
            gross_salary, net_salary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            employee_id, year, month, basic_salary, attendance_salary,
            bonus, social_deduction, fund_deduction, medical_deduction,
            unemployed_deduction, total_deduction, gross_salary, net_salary
        ))
        conn.commit()
        conn.close()

        return {
            'employee_id': employee_id,
            'name': employee['name'],
            'year': year,
            'month': month,
            'basic_salary': basic_salary,
            'attendance_salary': round(attendance_salary, 2),
            'overtime_pay': round(overtime_pay, 2),
            'performance_bonus': round(bonus, 2),
            'social_deduction': round(social_deduction, 2),
            'fund_deduction': round(fund_deduction, 2),
            'medical_deduction': round(medical_deduction, 2),
            'unemployed_deduction': round(unemployed_deduction, 2),
            'total_deduction': round(total_deduction, 2),
            'tax': round(tax, 2),
            'gross_salary': round(gross_salary, 2),
            'net_salary': round(net_salary, 2)
        }

    def get_payroll(self, year: int, month: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT p.*, e.name, e.department FROM payroll p LEFT JOIN employees e ON p.employee_id = e.employee_id WHERE p.year = ? AND p.month = ? ORDER BY e.department, e.name''', (year, month))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records
