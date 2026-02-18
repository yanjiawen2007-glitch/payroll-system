"""
Ollama 集成 - AI 分析工资数据
"""

import requests
import json
from typing import Dict, List
from database import PayrollDatabase


class OllamaAnalyzer:
    def __init__(self, db: PayrollDatabase, base_url: str = 'http://localhost:11434'):
        self.db = db
        self.base_url = base_url
        self.model = 'llama3'

    def _call_ollama(self, prompt: str) -> str:
        """调用 Ollama API"""
        try:
            response = requests.post(
                f'{self.base_url}/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"调用失败: {response.status_code}"
        except Exception as e:
            return f"调用失败: {str(e)}"

    def analyze_salary_data(self, year: int, month: int) -> str:
        """分析工资数据"""
        try:
            payroll_data = self.db.get_payroll(year, month)
            employees = self.db.get_all_employees()

            if not payroll_data:
                return f"{year}年{month}月 暂无工资数据，请先计算工资。"

            # 汇总统计数据
            total_employees = len(payroll_data)
            total_net_salary = sum(p['net_salary'] for p in payroll_data)
            total_gross_salary = sum(p['gross_salary'] for p in payroll_data)
            total_deduction = sum(p['total_deduction'] for p in payroll_data)
            avg_net_salary = total_net_salary / total_employees if total_employees > 0 else 0
            max_salary = max(p['net_salary'] for p in payroll_data)
            min_salary = min(p['net_salary'] for p in payroll_data)

            # 按部门统计
            department_stats = {}
            for p in payroll_data:
                dept = p.get('department', '未知')
                if dept not in department_stats:
                    department_stats[dept] = {'count': 0, 'total_salary': 0, 'avg_salary': 0}
                department_stats[dept]['count'] += 1
                department_stats[dept]['total_salary'] += p['net_salary']

            for dept in department_stats:
                department_stats[dept]['avg_salary'] = department_stats[dept]['total_salary'] / department_stats[dept]['count']

            # 生成分析提示
            prompt = f"""你是一位专业的 HR 数据分析师。请分析以下工资数据：

【基本信息】
- 时间：{year}年{month}月
- 员工总数：{total_employees} 人
- 平均实发工资：{avg_net_salary:.2f} 元
- 最高工资：{max_salary:.2f} 元
- 最低工资：{min_salary:.2f} 元
- 总应发工资：{total_gross_salary:.2f} 元
- 总扣款：{total_deduction:.2f} 元

【部门统计】
"""
            for dept, stats in department_stats.items():
                prompt += f"- {dept}：{stats['count']} 人，平均工资 {stats['avg_salary']:.2f} 元\n"

            prompt += """
【任务】
请根据以上数据，提供以下分析：
1. 整体薪酬水平分析
2. 部门薪酬差异分析
3. 薪酬结构优化建议
4. 预算控制建议
5. 其他有价值的洞察

请用简洁、专业的中文回答，不要超过 500 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"分析失败: {str(e)}"

    def suggest_salary_adjustment(self, employee_id: str, year: int, month: int) -> str:
        """建议工资调整"""
        try:
            employee = self.db.get_employee(employee_id)
            payroll = self.db.get_payroll(year, month)

            current_payroll = next((p for p in payroll if p['employee_id'] == employee_id), None)
            
            if not current_payroll:
                return "该员工没有工资数据。"

            all_employees = self.db.get_all_employees()
            avg_salary = sum(emp['basic_salary'] for emp in all_employees) / len(all_employees)

            prompt = f"""你是一位专业的 HR 顾问。请分析以下员工信息并提出工资调整建议：

【员工信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}
- 基本工资：{employee['basic_salary']:.2f} 元
- 实发工资：{current_payroll['net_salary']:.2f} 元

【市场参考】
- 公司平均基本工资：{avg_salary:.2f} 元
- 员工与平均水平差异：{(current_payroll['net_salary'] - avg_salary):.2f} 元

【任务】
请根据以上信息，提供以下建议：
1. 当前薪酬水平评估（偏高/适中/偏低）
2. 是否建议调整工资
3. 如果建议调整，调整幅度建议
4. 调整理由
5. 其他建议

请用简洁、专业的中文回答，不要超过 300 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"建议失败: {str(e)}"

    def predict_salary_trend(self, employee_id: str, months: int = 3) -> str:
        """预测工资趋势"""
        try:
            history = self.db.get_employee_payroll_history(employee_id)
            
            if len(history) < 2:
                return "该员工工资数据不足，无法预测。"

            prompt = f"""你是一位专业的 HR 数据分析师。请根据以下员工工资历史数据，预测未来 {months} 个月的工资趋势：

【工资历史】（最近几个月，从新到旧）
"""
            for record in history[:6]:
                prompt += f"- {record['year']}年{record['month']}月：实发工资 {record['net_salary']:.2f} 元\n"

            prompt += f"""
【任务】
请根据以上历史数据，提供以下分析：
1. 工资变化趋势分析
2. 未来 {months} 个月的工资预测
3. 可能影响工资变化的因素
4. 建议

请用简洁、专业的中文回答，不要超过 300 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"预测失败: {str(e)}"

    def generate_performance_review(self, employee_id: str, year: int, month: int) -> str:
        """生成绩效评估报告"""
        try:
            from database import PayrollDatabase
            db = PayrollDatabase()
            
            employee = db.get_employee(employee_id)
            attendance = db.get_attendance(employee_id, year, month)
            performance = db.get_performance(employee_id, year, month)
            payroll = next((p for p in db.get_payroll(year, month) if p['employee_id'] == employee_id), None)

            prompt = f"""你是一位专业的 HR 顾问。请根据以下员工数据，生成绩效评估报告：

【员工信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}

【考勤数据】
- 工作天数：{attendance['work_days'] if attendance else 0} 天
- 迟到天数：{attendance['late_days'] if attendance else 0} 天
- 请假天数：{attendance['leave_days'] if attendance else 0} 天
- 加班小时：{attendance['overtime_hours'] if attendance else 0} 小时

【绩效数据】
- 绩效分数：{performance['score'] if performance else 0} 分
- 绩效等级：{performance['grade'] if performance else '无'}

【工资数据】
- 基本工资：{employee['basic_salary']:.2f} 元
- 绩效奖金：{payroll['performance_bonus']:.2f} 元 if payroll else 0 元
- 实发工资：{payroll['net_salary']:.2f} 元 if payroll else 0 元

【任务】
请根据以上数据，提供以下分析：
1. 工作表现评估
2. 绩效分析
3. 薪酬与绩效匹配度分析
4. 改进建议
5. 晋升或发展建议

请用简洁、专业的中文回答，不要超过 500 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"生成失败: {str(e)}"
