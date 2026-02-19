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
            print(f"[DEBUG] 正在调用Ollama API...")
            print(f"[DEBUG] Prompt长度: {len(prompt)}")
            print(f"[DEBUG] 模型: {self.model}")
            
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
                timeout=300  # 增加超时时间到 5 分钟
            )

            print(f"[DEBUG] 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[DEBUG] 响应JSON: {result}")
                
                result_text = result.get('response', '').strip()
                print(f"[DEBUG] 提取的文本: {repr(result_text[:100] if result_text else '空')}")
                
                return result_text if result_text else "未获取到AI响应，请稍后重试"
            else:
                error_msg = f"调用失败: HTTP {response.status_code} - {response.text[:200]}"
                print(f"[DEBUG] {error_msg}")
                return error_msg
        except requests.exceptions.Timeout:
            error_msg = "调用失败: 请求超时（300秒），请检查Ollama服务是否正常运行"
            print(f"[DEBUG] {error_msg}")
            return error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"调用失败: 无法连接到Ollama服务 - {str(e)}"
            print(f"[DEBUG] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"调用失败: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            return error_msg

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
            prompt = f"""你是一位专业的 HR 顾问。请根据以下工资数据进行分析和提供建议：

【工资数据概况】
- 月份：{year}年{month}月
- 员工总数：{total_employees}人
- 总实发工资：{total_net_salary:.2f}元
- 平均实发工资：{avg_net_salary:.2f}元
- 最高工资：{max_salary:.2f}元
- 最低工资：{min_salary:.2f}元

【工资分布】
"""
            for range_name, count in salary_ranges.items():
                if count > 0:
                    prompt += f"- {range_name}：{count}人（{count/total_employees*100:.1f}%）\n"

            prompt += "\n【部门工资】\n"
            for dept_name, stats in sorted_departments:
                prompt += f"- {dept_name}：{stats['count']}人，平均工资{stats['avg_salary']:.2f}元\n"

            prompt += """
请提供以下分析：
1. 整体薪酬水平评估（对比市场平均）
2. 工资分布特征分析
3. 薪酬结构优化建议
4. 成本控制建议

请用简洁、专业的语言回答。"""

            print(f"[DEBUG] 生成Prompt长度: {len(prompt)}")

            # 调用Ollama
            result = self._call_ollama(prompt)

            return result

        except Exception as e:
            error_msg = f"分析失败: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            return error_msg

    def analyze_employee(self, employee_id: str, year: int, month: int) -> str:
        """分析单个员工工资"""
        try:
            employee = self.db.get_employee(employee_id)
            if not employee:
                return f"未找到工号为 {employee_id} 的员工。"

            current_payroll = self.db.get_payroll(year, month)
            employee_payroll = next((p for p in current_payroll if p['employee_id'] == employee_id), None)

            if not employee_payroll:
                return f"该员工没有工资数据。"

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
- 实发工资：{employee_payroll['net_salary']:.2f} 元
- 出勤工资：{employee_payroll['attendance_salary']:.2f} 元
- 绩效奖金：{employee_payroll['performance_bonus']:.2f} 元

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
                prompt += f"- 绩效分数：{performance['score']}\n"
                prompt += f"- 绩效等级：{performance['grade']}\n"

            prompt += """
请提供以下建议：
1. 薪酬合理性评估（对比市场）
2. 是否需要薪酬调整
3. 具体的调整建议（金额或比例）

请用简洁、专业的语言回答。"""

            # 调用Ollama
            result = self._call_ollama(prompt)

            return result

        except Exception as e:
            return f"分析失败: {str(e)}"

    def predict_salary_trend(self, employee_id: str) -> str:
        """预测工资趋势"""
        try:
            employee = self.db.get_employee(employee_id)
            if not employee:
                return f"未找到工号为 {employee_id} 的员工。"

            # 获取历史工资数据
            payroll_history = self.db.get_employee_payroll_history(employee_id)

            if not payroll_history:
                return f"该员工没有历史工资数据，无法预测趋势。"

            prompt = f"""你是一位专业的 HR 数据分析师。请根据以下员工的历史工资数据，预测未来工资趋势：

【员工信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}

【历史工资数据】（最近6个月）
"""
            for record in payroll_history[:6]:
                prompt += f"{record['year']}年{record['month']}月：实发{record['net_salary']:.2f}元，应发{record['gross_salary']:.2f}元\n"

            prompt += """
请提供以下分析：
1. 工资增长趋势（上升/下降/稳定）
2. 预测未来3个月的工资水平
3. 影响工资变化的主要因素

请用简洁、专业的语言回答。"""

            # 调用Ollama
            result = self._call_ollama(prompt)

            return result

        except Exception as e:
            return f"预测失败: {str(e)}"

    def generate_performance_review(self, employee_id: str, year: int, month: int) -> str:
        """生成绩效评估报告"""
        try:
            employee = self.db.get_employee(employee_id)
            if not employee:
                return f"未找到工号为 {employee_id} 的员工。"

            # 获取绩效数据
            performance = self.db.get_performance(employee_id, year, month)
            attendance = self.db.get_attendance(employee_id, year, month)

            if not performance:
                return f"该员工没有绩效数据。"

            prompt = f"""你是一位专业的 HR 绩效主管。请根据以下数据，为员工生成绩效评估报告：

【员工信息】
- 工号：{employee['employee_id']}
- 姓名：{employee['name']}
- 部门：{employee['department']}
- 职位：{employee['position']}

【当前绩效】
- 绩效分数：{performance['score']}
- 绩效等级：{performance['grade']}

【考勤数据】
"""
            if attendance:
                prompt += f"- 工作天数：{attendance['work_days']} 天\n"
                prompt += f"- 迟到天数：{attendance['late_days']} 天\n"
                prompt += f"- 请假天数：{attendance['leave_days']} 天\n"
                prompt += f"- 加班小时：{attendance['overtime_hours']} 小时\n"

            prompt += """
请生成以下内容：
1. 绩效评估（优秀/良好/合格/需改进）
2. 工作表现亮点
3. 改进建议
4. 后续发展建议

请用专业、鼓励性的语言回答。"""

            # 调用Ollama
            result = self._call_ollama(prompt)

            return result

        except Exception as e:
            return f"生成失败: {str(e)}"
