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
        self.model = 'qwen3:4b'  # 使用 qwen3:4b 模型

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
                        'num_predict': 1500
                    }
                },
                timeout=60  # 增加超时时间到 60 秒
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
            
            # 计算工资分布
            salary_ranges = {
                '5千以下': 0,
                '5千-1万': 0,
                '1万-1.5万': 0,
                '1.5万-2万': 0,
                '2万-3万': 0,
                '3万以上': 0
            }
            
            for p in payroll_data:
                salary = p['net_salary']
                if salary < 5000:
                    salary_ranges['5千以下'] += 1
                elif salary < 10000:
                    salary_ranges['5千-1万'] += 1
                elif salary < 15000:
                    salary_ranges['1万-1.5万'] += 1
                elif salary < 20000:
                    salary_ranges['1.5万-2万'] += 1
                elif salary < 30000:
                    salary_ranges['2万-3万'] += 1
                else:
                    salary_ranges['3万以上'] += 1

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

            # 按部门排序
            sorted_departments = sorted(department_stats.items(), key=lambda x: x[1]['avg_salary'], reverse=True)

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

【工资分布】
"""
            for range_name, count in salary_ranges.items():
                prompt += f"- {range_name}: {count} 人\n"

            prompt += """
【部门薪酬分析】
"""
            for dept, stats in sorted_departments[:5]:  # 只显示前 5 个部门
                prompt += f"- {dept}: {stats['count']} 人，平均工资 {stats['avg_salary']:.2f} 元\n"

            if len(sorted_departments) > 5:
                prompt += f"- 其他部门: {len(sorted_departments) - 5} 个\n"

            prompt += """
【任务】
请根据以上数据，提供以下分析：
1. 整体薪酬水平评估（偏低/适中/偏高）
2. 部门薪酬差异分析
3. 工资分布特征分析
4. 薪酬结构优化建议
5. 成本控制建议
6. 其他有价值的洞察

请用简洁、专业的中文回答，分点列出，不要超过 800 字。
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

            # 获取公司平均数据
            all_employees = self.db.get_all_employees()
            avg_salary = sum(emp['basic_salary'] for emp in all_employees) / len(all_employees)
            
            # 获取部门平均数据
            department_employees = [emp for emp in all_employees if emp['department'] == employee['department']]
            dept_avg_salary = sum(emp['basic_salary'] for emp in department_employees) / len(department_employees)
            
            # 获取职位平均数据
            position_employees = [emp for emp in all_employees if emp['position'] == employee['position']]
            position_avg_salary = sum(emp['basic_salary'] for emp in position_employees) / len(position_employees)

            # 获取绩效数据
            attendance = self.db.get_attendance(employee_id, year, month)
            performance = self.db.get_performance(employee_id, year, month)

            prompt = f"""你是一位专业的 HR 顾问。请根据以下员工信息，提供薪酬调整建议：

【员工信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}
- 基本工资：{employee['basic_salary']:.2f} 元

【当前薪酬】
- 实发工资：{current_payroll['net_salary']:.2f} 元
- 出勤工资：{current_payroll['attendance_salary']:.2f} 元
- 绩效奖金：{current_payroll['performance_bonus']:.2f} 元

【市场参考】
- 公司平均基本工资：{avg_salary:.2f} 元
- {employee['department']}部门平均基本工资：{dept_avg_salary:.2f} 元
- {employee['position']}职位平均基本工资：{position_avg_salary:.2f} 元

【考勤数据】
"""
            if attendance:
                prompt += f"- 工作天数：{attendance['work_days']} 天\n"
                prompt += f"- 迟到天数：{attendance['late_days']} 天\n"
                prompt += f"- 请假天数：{attendance['leave_days']} 天\n"
                prompt += f"- 加班小时：{attendance['overtime_hours']} 小时\n"

            prompt += """
【绩效数据】
"""
            if performance:
                prompt += f"- 绩效分数：{performance['score']} 分\n"
                prompt += f"- 绩效等级：{performance['grade']}\n"
                prompt += f"- 奖金公式：{performance['bonus_formula']}\n"
                prompt += f"- 绩效奖金：{current_payroll['performance_bonus']:.2f} 元\n"

            prompt += f"""
【薪酬差异分析】
- 与公司平均水平差异：{current_payroll['net_salary'] - avg_salary:.2f} 元
- 与{employee['department']}部门平均水平差异：{current_payroll['net_salary'] - dept_avg_salary:.2f} 元
- 与{employee['position']}职位平均水平差异：{current_payroll['net_salary'] - position_avg_salary:.2f} 元

【任务】
请根据以上信息，提供以下建议：
1. 当前薪酬水平评估（偏低/适中/偏高）
2. 是否建议调整基本工资
3. 如果建议调整，具体调整幅度建议
4. 调整理由（如：绩效突出/岗位价值提升等）
5. 其他建议（如：内部公平性、外部竞争力等）

请用简洁、专业的中文回答，分点列出，不要超过 600 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"建议失败: {str(e)}"

    def predict_salary_trend(self, employee_id: str, months: int = 3) -> str:
        """预测工资趋势"""
        try:
            history = self.db.get_employee_payroll_history(employee_id)

            if len(history) < 2:
                return "该员工工资数据不足，无法预测。至少需要 2 个月的数据。"

            # 只取最近的几个月用于预测
            recent_history = history[:6]

            # 分析历史数据
            salary_changes = []
            for i in range(1, len(recent_history)):
                prev_salary = recent_history[i-1]['net_salary']
                curr_salary = recent_history[i]['net_salary']
                change = curr_salary - prev_salary
                change_pct = (change / prev_salary) * 100 if prev_salary > 0 else 0
                salary_changes.append({
                    'period': f"{recent_history[i]['year']}年{recent_history[i]['month']}月",
                    'salary': curr_salary,
                    'change': change,
                    'change_pct': change_pct
                })

            # 计算平均增长率
            if len(salary_changes) >= 2:
                avg_growth = sum(sc['change_pct'] for sc in salary_changes) / len(salary_changes)
            else:
                avg_growth = 0

            prompt = f"""你是一位专业的 HR 数据分析师。请根据以下员工工资历史数据，预测未来 {months} 个月的工资趋势：

【员工基本信息】
- 工号：{employee_id}
- 数据期间：{recent_history[0]['year']}年{recent_history[0]['month']}月 到 {recent_history[-1]['year']}年{recent_history[-1]['month']}月
- 数据点数：{len(recent_history)} 个月

【工资历史数据】（从最新到最旧）
"""
            for record in recent_history:
                prompt += f"- {record['year']}年{record['month']}月：实发工资 {record['net_salary']:.2f} 元"
                if record['attendance_salary'] != record['basic_salary']:
                    prompt += f"（含出勤调整）"
                if record['performance_bonus'] > 0:
                    prompt += f"（含绩效奖金 {record['performance_bonus']:.2f} 元）"
                prompt += "\n"

            prompt += f"""
【趋势分析】
- 平均增长率：{avg_growth:.2f}%
- 最近的工资变化趋势：{'上升' if salary_changes[-1]['change'] > 0 else '下降' if salary_changes[-1]['change'] < 0 else '稳定'} ({salary_changes[-1]['change']:.2f} 元)

【预测任务】
请根据以上历史数据，提供以下分析和预测：
1. 工资变化趋势分析（上升/下降/稳定）
2. 影响工资变化的主要因素（如：出勤、绩效、奖金等）
3. 未来 {months} 个月的工资预测（具体金额）
4. 预测的准确度评估
5. 影响未来工资的风险提示

请用简洁、专业的中文回答，分点列出，不要超过 700 字。
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

【员工基本信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}
- 基本工资：{employee['basic_salary']:.2f} 元

【考勤数据】
"""
            if attendance:
                prompt += f"- 工作天数：{attendance['work_days']} 天"
                if attendance['work_days'] >= 22:
                    prompt += "（满勤）"
                else:
                    prompt += f"（缺勤 {22 - attendance['work_days']} 天）"
                prompt += "\n"
                prompt += f"- 迟到天数：{attendance['late_days']} 天"
                if attendance['late_days'] > 0:
                    prompt += "（有迟到记录）"
                else:
                    prompt += "（无迟到）"
                prompt += "\n"
                prompt += f"- 请假天数：{attendance['leave_days']} 天"
                if attendance['leave_days'] > 0:
                    prompt += f"（请假 {attendance['leave_days']} 天）"
                else:
                    prompt += "（无请假）"
                prompt += "\n"
                prompt += f"- 加班小时：{attendance['overtime_hours']} 小时"
                if attendance['overtime_hours'] > 0:
                    prompt += f"（加班 {attendance['overtime_hours']} 小时）"
                else:
                    prompt += "（无加班）"
                prompt += "\n"
            else:
                prompt += "- 暂无考勤数据\n"

            prompt += """
【绩效数据】
"""
            if performance:
                prompt += f"- 绩效分数：{performance['score']} 分\n"
                if performance['score'] >= 90:
                    prompt += "评价：优秀（90分以上）\n"
                elif performance['score'] >= 80:
                    prompt += "评价：良好（80-89分）\n"
                elif performance['score'] >= 70:
                    prompt += "评价：合格（70-79分）\n"
                elif performance['score'] >= 60:
                    prompt += "评价：待改进（60-69分）\n"
                else:
                    prompt += "评价：需提升（60分以下）\n"
                prompt += f"- 绩效等级：{performance['grade']}\n"
                prompt += f"- 奖金公式：{performance['bonus_formula']}\n"
                if performance['bonus_formula']:
                    prompt += f"说明：此公式用于计算绩效奖金\n"
                else:
                    prompt += "说明：使用默认奖金公式\n"
            else:
                prompt += "- 暂无绩效数据\n"

            prompt += f"""
【薪酬数据】
"""
            if payroll:
                prompt += f"- 基本工资：{employee['basic_salary']:.2f} 元\n"
                prompt += f"- 出勤工资：{payroll['attendance_salary']:.2f} 元"
                if payroll['attendance_salary'] != employee['basic_salary']:
                    diff = payroll['attendance_salary'] - employee['basic_salary']
                    if diff < 0:
                        prompt += f"（因考勤扣款 {abs(diff):.2f} 元）"
                    else:
                        prompt += f"（因加班费 {abs(diff):.2f} 元）"
                else:
                    prompt += "（与基本工资一致）"
                prompt += "\n"
                prompt += f"- 绩效奖金：{payroll['performance_bonus']:.2f} 元"
                if payroll['performance_bonus'] > 0:
                    prompt += "（含绩效奖金）"
                else:
                    prompt += "（无绩效奖金）"
                prompt += "\n"
                prompt += f"- 实发工资：{payroll['net_salary']:.2f} 元\n"
            else:
                prompt += "- 暂无工资数据\n"

            prompt += f"""
【综合评估任务】
请根据以上数据，提供以下综合评估：

1. 工作表现评估（出勤、加班、工作态度等）
2. 绩效水平评估（分数、等级、与标准对比）
3. 薪酬与绩效匹配度分析（是否体现了多劳多得）
4. 基本工资是否合理（与市场、部门、职位对比）
5. 综合薪酬建议（保持/调整/调整幅度）
6. 提升建议（技能、能力、资历等方面）
7. 其他有价值的建议

请用简洁、专业的中文回答，结构清晰，分点列出，不要超过 1000 字。
"""

            return self._call_ollama(prompt)

        except Exception as e:
            return f"生成失败: {str(e)}"
