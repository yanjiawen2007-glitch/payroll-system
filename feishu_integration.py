"""
飞书多维表格集成模块（简化版）
专用于工资表格：Base ID NbGTbqBPXasagWsfGpHcklrTnnd, Table ID tblHc3G5OyJGjpx2
"""

import requests
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeishuImporter:
    """飞书工资表格导入器（简化版）"""

    # 固定的多维表格信息
    BASE_ID = "NbGTbqBPXasagWsfGpHcklrTnnd"
    TABLE_ID = "tblHc3G5OyJGjpx2"

    def __init__(self, access_token: str):
        """
        初始化导入器

        参数:
            access_token: 飞书个人访问令牌（格式：cli_xxxxxxxxx）
        """
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def _extract_field_value(self, record: Dict, field_name: str) -> Any:
        """从记录中提取字段值"""
        fields = record.get("fields", {})

        if field_name not in fields:
            return None

        value = fields[field_name]

        # 处理列表类型（多选、人员等）
        if isinstance(value, list):
            if len(value) == 0:
                return None
            if all(isinstance(item, str) for item in value):
                return ", ".join(value)
            if all(isinstance(item, dict) for item in value):
                return ", ".join([item.get("text", item.get("name", "")) for item in value])
            return str(value)

        return value

    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        获取工资表格中的所有记录

        返回:
            记录列表
        """
        records = []
        page_token = ""

        while True:
            url = f"{self.base_url}/bitable/v1/apps/{self.BASE_ID}/tables/{self.TABLE_ID}/records"
            params = {"page_size": 100}

            if page_token:
                params["page_token"] = page_token

            try:
                response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
                result = response.json()

                if result.get("code") != 0:
                    raise Exception(f"获取数据失败: {result.get('msg')}")

                data = result.get("data", {})
                items = data.get("items", [])
                records.extend(items)

                has_more = data.get("has_more", False)
                if not has_more:
                    break

                page_token = data.get("page_token", "")

                logger.info(f"已获取 {len(records)} 条记录...")

            except requests.exceptions.Timeout:
                logger.error("请求超时，请检查网络连接")
                break
            except Exception as e:
                logger.error(f"获取数据出错: {str(e)}")
                break

        logger.info(f"✅ 成功获取 {len(records)} 条记录")
        return records

    def parse_records(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """
        解析记录，按类型分类

        返回:
            {
                "employees": 员工数据列表,
                "attendance": 考勤数据列表,
                "performance": 绩效数据列表
            }
        """
        employees = []
        attendance = []
        performance = []

        for record in records:
            # 提取基本字段
            employee_id = self._extract_field_value(record, "工号")
            name = self._extract_field_value(record, "姓名")
            department = self._extract_field_value(record, "部门")
            position = self._extract_field_value(record, "职位")
            basic_salary = self._extract_field_value(record, "基本工资")
            year = self._extract_field_value(record, "年份")
            month = self._extract_field_value(record, "月份")

            # 员工数据
            if employee_id and name:
                employee = {
                    "employee_id": employee_id,
                    "name": name,
                    "department": department,
                    "position": position,
                    "basic_salary": basic_salary,
                    "status": "active"
                }
                employees.append(employee)

            # 考勤数据
            if employee_id and year and month:
                att = {
                    "employee_id": employee_id,
                    "year": year,
                    "month": month,
                    "work_days": self._extract_field_value(record, "工作天数") or 22,
                    "late_days": self._extract_field_value(record, "迟到天数") or 0,
                    "leave_days": self._extract_field_value(record, "请假天数") or 0,
                    "overtime_hours": self._extract_field_value(record, "加班小时") or 0
                }
                attendance.append(att)

            # 绩效数据
            if employee_id and year and month:
                perf = {
                    "employee_id": employee_id,
                    "year": year,
                    "month": month,
                    "score": self._extract_field_value(record, "绩效分数") or 0,
                    "grade": self._extract_field_value(record, "绩效等级"),
                    "bonus_formula": self._extract_field_value(record, "奖金公式"),
                    "bonus_amount": self._extract_field_value(record, "奖金金额")
                }
                performance.append(perf)

        logger.info(f"✅ 解析完成：{len(employees)} 名员工，{len(attendance)} 条考勤，{len(performance)} 条绩效")

        return {
            "employees": employees,
            "attendance": attendance,
            "performance": performance
        }

    def import_all(self) -> Dict[str, List[Dict]]:
        """
        一键导入所有数据

        返回:
            {
                "employees": 员工数据列表,
                "attendance": 考勤数据列表,
                "performance": 绩效数据列表
            }
        """
        logger.info("=" * 50)
        logger.info("📥 开始从飞书导入数据...")

        # 获取记录
        records = self.get_all_records()

        if not records:
            logger.warning("⚠️ 飞书表格中没有数据")
            return {"employees": [], "attendance": [], "performance": []}

        # 解析记录
        data = self.parse_records(records)

        logger.info("=" * 50)
        logger.info("✅ 数据导入完成！")

        return data


# 简化的测试函数
def test_import(access_token: str) -> bool:
    """
    测试飞书导入

    参数:
        access_token: 飞书个人访问令牌

    返回:
        是否成功
    """
    try:
        importer = FeishuImporter(access_token)
        data = importer.import_all()

        if data["employees"]:
            print(f"✅ 成功导入 {len(data['employees'])} 名员工")
            print(f"✅ 成功导入 {len(data['attendance'])} 条考勤记录")
            print(f"✅ 成功导入 {len(data['performance'])} 条绩效记录")
            return True
        else:
            print("⚠️ 飞书表格中没有数据")
            return False

    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 测试代码
    print("飞书工资表格导入器（简化版）")
    print("=" * 50)
    print()
    print("使用方法:")
    print()
    print("  from feishu_integration import FeishuImporter")
    print()
    print("  # 创建导入器（需要飞书个人访问令牌）")
    print("  importer = FeishuImporter('cli_xxxxxxxxx')")
    print()
    print("  # 一键导入所有数据")
    print("  data = importer.import_all()")
    print()
    print("  # data 包含三个列表：")
    print("  # - data['employees']: 员工数据")
    print("  # - data['attendance']: 考勤数据")
    print("  # - data['performance']: 绩效数据")
    print()
    print("=" * 50)
