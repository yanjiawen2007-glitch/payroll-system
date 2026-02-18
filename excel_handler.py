import pandas as pd
import os
from typing import List, Dict, Optional
from database import PayrollDatabase

class ExcelHandler:
    def __init__(self, db: PayrollDatabase):
        self.db = db
        self.export_dir = 'exports'
        os.makedirs(self.export_dir, exist_ok=True)

    def import_attendance_from_excel(self, file_path: str, year: int, month: int) -> Dict:
        try:
            df = pd.read_excel(file_path)
            required_columns = ['员工工号', '工作天数', '迟到天数', '请假天数', '加班小时']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {'success': False, 'message': f'Excel 缺少必需列: {", ".join(missing_columns)}'}
            
            success_count = 0
            failed_count = 0
            
            for _, row in df.iterrows():
                employee_id = str(row['员工工号']).strip()
                employee = self.db.get_employee(employee_id)
                if not employee:
                    failed_count += 1
                    continue
                
                attendance_data = {
                    'employee_id': employee_id,
                    'year': year,
                    'month': month,
                    'work_days': float(row['工作天数']) if pd.notna(row['工作天数']) else 22,
                    'late_days': float(row['迟到天数']) if pd.notna(row['迟到天数']) else 0,
                    'leave_days': float(row['请假天数']) if pd.notna(row['请假天数']) else 0,
                    'overtime_hours': float(row['加班小时']) if pd.notna(row['加班小时']) else 0
                }
                
                if self.db.add_attendance(attendance_data):
                    success_count += 1
                else:
                    failed_count += 1
            
            return {'success': True, 'message': f'导入完成：成功 {success_count} 条，失败 {failed_count} 条'}
        except Exception as e:
            return {'success': False, 'message': f'导入失败: {str(e)}'}

    def import_performance_from_excel(self, file_path: str, year: int, month: int) -> Dict:
        try:
            df = pd.read_excel(file_path)
            required_columns = ['员工工号', '绩效分数']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {'success': False, 'message': f'Excel 缺少必需列: {", ".join(missing_columns)}'}
            
            success_count = 0
            failed_count = 0
            
            for _, row in df.iterrows():
                employee_id = str(row['员工工号']).strip()
                employee = self.db.get_employee(employee_id)
                if not employee:
                    failed_count += 1
                    continue
                
                performance_data = {
                    'employee_id': employee_id,
                    'year': year,
                    'month': month,
                    'score': float(row['绩效分数']),
                    'grade': str(row['绩效等级']) if '绩效等级' in df.columns and pd.notna(row['绩效等级']) else '',
                    'bonus_formula': str(row['奖金公式']) if '奖金公式' in df.columns and pd.notna(row['奖金公式']) else 'base_salary * score * 0.01'
                }
                
                if self.db.add_performance(performance_data):
                    success_count += 1
                else:
                    failed_count += 1
            
            return {'success': True, 'message': f'导入完成：成功 {success_count} 条，失败 {failed_count} 条'}
        except Exception as e:
            return {'success': False, 'message': f'导入失败: {str(e)}'}

    def export_payroll_to_excel(self, year: int, month: int) -> Dict:
        try:
            payroll_data = self.db.get_payroll(year, month)
            if not payroll_data:
                return {'success': False, 'message': '该月份暂无工资数据'}
            
            df = pd.DataFrame(payroll_data)
            export_columns = [
                'employee_id', 'name', 'department',
                'basic_salary', 'attendance_salary', 'performance_bonus',
                'social_deduction', 'fund_deduction', 'medical_deduction',
                'unemployed_deduction', 'total_deduction',
                'gross_salary', 'net_salary'
            ]
            df_export = df[export_columns]
            df_export.columns = [
                '工号', '姓名', '部门',
                '基本工资', '出勤工资', '绩效奖金',
                '社保扣款', '公积金扣款', '医保扣款',
                '失业保险扣款', '总扣款',
                '应发工资', '实发工资'
            ]
            
            total_row = df_export.sum(numeric_only=True)
            total_row['工号'] = '合计'
            total_row['姓名'] = ''
            total_row['部门'] = ''
            df_export = pd.concat([df_export, total_row.to_frame().T], ignore_index=True)
            
            filename = f'工资表_{year}年{month:02d}月.xlsx'
            file_path = os.path.join(self.export_dir, filename)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='工资表', index=False)
                worksheet = writer.sheets['工资表']
                for idx, col in enumerate(df_export.columns, 1):
                    max_length = max(df_export[col].astype(str).apply(len).max(), len(str(col)))
                    worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 30)
            
            return {'success': True, 'message': f'导出成功：{filename}', 'file_path': file_path}
        except Exception as e:
            return {'success': False, 'message': f'导出失败: {str(e)}'}

    def export_employee_list(self) -> Dict:
        try:
            employees = self.db.get_all_employees()
            if not employees:
                return {'success': False, 'message': '暂无员工数据'}
            
            df = pd.DataFrame(employees)
            export_columns = [
                'employee_id', 'name', 'department', 'position',
                'basic_salary', 'base_social_rate', 'base_fund_rate',
                'base_medical_rate', 'unemployed_rate', 'entry_date', 'status'
            ]
            df_export = df[export_columns]
            df_export.columns = [
                '工号', '姓名', '部门', '职位',
                '基本工资', '社保比例', '公积金比例',
                '医保比例', '失业保险比例', '入职日期', '状态'
            ]
            
            filename = f'员工列表_{pd.Timestamp.now().strftime("%Y%m%d")}.xlsx'
            file_path = os.path.join(self.export_dir, filename)
            df_export.to_excel(file_path, index=False)
            
            return {'success': True, 'message': f'导出成功：{filename}', 'file_path': file_path}
        except Exception as e:
            return {'success': False, 'message': f'导出失败: {str(e)}'}

    def generate_attendance_template(self) -> Dict:
        try:
            employees = self.db.get_all_employees()
            df = pd.DataFrame({
                '员工工号': [emp['employee_id'] for emp in employees],
                '姓名': [emp['name'] for emp in employees],
                '工作天数': [22] * len(employees),
                '迟到天数': [0] * len(employees),
                '请假天数': [0] * len(employees),
                '加班小时': [0] * len(employees)
            })
            filename = '考勤导入模板.xlsx'
            file_path = os.path.join(self.export_dir, filename)
            df.to_excel(file_path, index=False)
            return {'success': True, 'message': f'模板生成成功：{filename}', 'file_path': file_path}
        except Exception as e:
            return {'success': False, 'message': f'模板生成失败: {str(e)}'}

    def generate_performance_template(self) -> Dict:
        try:
            employees = self.db.get_all_employees()
            df = pd.DataFrame({
                '员工工号': [emp['employee_id'] for emp in employees],
                '姓名': [emp['name'] for emp in employees],
                '绩效分数': [100] * len(employees),
                '绩效等级': ['A'] * len(employees),
                '奖金公式': ['base_salary * score * 0.01'] * len(employees)
            })
            filename = '绩效导入模板.xlsx'
            file_path = os.path.join(self.export_dir, filename)
            df.to_excel(file_path, index=False)
            return {'success': True, 'message': f'模板生成成功：{filename}', 'file_path': file_path}
        except Exception as e:
            return {'success': False, 'message': f'模板生成失败: {str(e)}'}
