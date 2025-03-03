import logging
import markdown
import json
from bs4 import BeautifulSoup
import re
import os

# 配置日志记录
logger = logging.getLogger(__name__)

# 分隔符配置
SEPARATORS = ['：']


def load_config(file_name="config.json"):
    """
    加载配置文件（JSON 格式）

    :param file_name: 配置文件名，默认为 config.json
    :return: 解析后的 JSON 数据
    """
    try:
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, file_name)
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"配置文件未找到：{config_path}")
        return None
    except Exception as e:
        logging.error(f"加载配置文件失败：{str(e)}")
        return None


# def read_markdown_file(file_path):
#     """
#     从文件中读取 Markdown 内容
#
#     :param file_path: Markdown 文件路径
#     :return: Markdown 内容字符串
#     """
#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             return file.read()
#     except FileNotFoundError:
#         logging.error(f"文件未找到：{file_path}")
#         return None
#     except Exception as e:
#         logging.error(f"读取 Markdown 文件失败：{str(e)}")
#         return None
#

def parse_markdown_to_json(md_content, config):
    """
    将 Markdown 格式的简历内容解析为 JSON 格式数据

    :param md_content: Markdown 格式的简历内容
    :param config: 配置文件内容（JSON 格式）
    :return: 解析后的 JSON 数据
    """
    # 将 Markdown 转换为 HTML
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, 'html.parser')

    # 初始化 JSON 数据结构，使用 config 作为模板
    data = config

    # 通用解析函数：解析标题下的内容
    def parse_section(header_text, target_key, parser_func):
        """
        解析指定标题下的内容

        :param header_text: 标题文本
        :param target_key: 目标 JSON 键
        :param parser_func: 解析函数
        """
        logging.info(f'解析标题下内容:{header_text}')
        section = soup.find('h1', string=header_text)
        if section:
            parser_func(section, target_key)

    # 解析姓名
    def parse_name(section, target_key):
        """
        解析姓名信息

        :param section: 姓名部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        name_item = section.find_next('p')
        if name_item:
            name_text = name_item.get_text()
            data[target_key] = name_text

    # 解析求职意向
    def parse_job_intention(section, target_key):
        """
        解析求职意向信息

        :param section: 求职意向部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        intention_item = section.find_next('p')
        if intention_item:
            data[target_key] = intention_item.get_text().strip()

    # 解析个人信息
    def parse_personal_info(section, target_key):
        """
        解析个人信息

        :param section: 个人信息部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        # 键名映射表
        key_mapping = {
            "性别": "gender",
            "民族": "ethnicity",
            "年龄": "age",
            "联系方式": "contact",
            "邮箱": "e_mail",
            "政治面貌": "face",
            "国籍": "nationality",
            "住址": "location",
            "Linkedin": "linkedin",
            "Github": "github",
            "个人博客": "personal_website"
        }
        info_items = section.find_next('ul').find_all('li')
        for item in info_items:
            item_text = item.get_text()
            for separator in SEPARATORS:
                if separator in item_text:
                    try:
                        key, value = item_text.split(separator, 1)
                        key = key.strip()
                        value = value.strip()
                        if key in key_mapping:
                            data["personal_info"][key_mapping[key]] = value
                        break
                    except ValueError:
                        logging.error(f"解析个人信息 {item_text} 时出现格式错误")

    # 解析教育背景
    def parse_education(section, target_key):
        """解析教育背景信息"""
        key_edu = {
            "学位": "degree",
            "学校": "school",
            "专业": "major",
            "开始时间": "start_date",
            "结束时间": "end_date",
            "GPA": "gpa",
            "主修课程": "courses",
        }
        edu_items = section.find_next('ul').find_all('li')
        for items in edu_items:
            edu_text = items.get_text()
            for separator in SEPARATORS:
                if separator in edu_text:
                    try:
                        key, value = edu_text.split(separator, 1)
                        key = key.strip()
                        value = value.strip()
                        if key in key_edu:
                            data["education"][key_edu[key]] = value
                    except Exception as e:
                        logging.error(f"解析教育背景失败：{edu_text} - {str(e)}")

    def parse_skills(section, target_key):
        """
        解析技能部分

        :param section: 技能部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        key_skills = {
            "编程语言": "programming_languages",
            "工具": "tools",
            "框架": "frameworks",
            "数据库": "databases",
            "软件": "software",
            "语言": "languages"
        }
        # 找到技能部分的<ul>
        skills_items = section.find_next('ul').find_all('li')
        for items in skills_items:
            skill_text = items.get_text()
            for separator in SEPARATORS:
                if separator in skill_text:
                    try:
                        key, value = skill_text.split(separator, 1)
                        key = key.strip()
                        value = value.strip()
                        if key in key_skills:
                            data["skills"][key_skills[key]] = value
                    except Exception as e:
                        logging.error(f"解析技能失败：{skill_text}－{str(e)}")

    # 证书选择
    def parse_certificates(section, target_key):
        """
        解析证书部分

        :param section: 证书部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        key_certificates = {
            "证书名称": "certificate_name",
            "颁发机构": "issuing_authority",
            "获得日期": "obtained_date"
        }

        # 确保 data["certificates"] 是一个列表
        if "certificates" not in data or not isinstance(data["certificates"], list):
            data["certificates"] = []
        # 清空初始值（覆盖初始值）
        data["certificates"].clear()

        # 初始化一个临时字典来存储当前证书的信息
        current_cert = {}
        certificates_items = section.find_next('ul').find_all('li')  # 找到所有 <li>

        for item in certificates_items:
            cer_text = item.get_text()
            for separator in SEPARATORS:
                if separator in cer_text:
                    try:
                        key, value = cer_text.split(separator, 1)
                        key = key.strip()
                        value = value.strip()
                        if key in key_certificates:
                            # 如果当前字段是“证书名称”，说明是一个新的证书的开始
                            if key == "证书名称" and current_cert:
                                # 保存当前证书
                                data["certificates"].append(current_cert)
                                current_cert = {}
                            # 添加字段到当前证书
                            current_cert[key_certificates[key]] = value
                    except Exception as e:
                        logging.error(f"解析证书失败：{cer_text} - {str(e)}")
                    break  # 匹配到一个分隔符后跳出循环

        # 保存最后一个证书
        if current_cert:
            data["certificates"].append(current_cert)

    # 解析工作经历
    def parse_work_experience(section, target_key):
        """
        解析工作经历部分

        :param section: 工作经历部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        key_experience = {
            "公司名称": "company_name",
            "职务": "position",
            "开始时间": "start_date",
            "结束时间": "end_date",
            "描述": "description"
        }

        # 确保 data["work_experience"] 是一个列表
        if "work_experience" not in data or not isinstance(data["work_experience"], list):
            data["work_experience"] = []

        # 清空初始值（覆盖初始值）
        data["work_experience"].clear()

        work_experience_start = soup.find('h1', string="工作经历")
        if not work_experience_start:
            logging.error("未找到工作经历部分的起始点")
            return

        # 找到所有 <h2> 标签，每个 <h2> 代表一个工作经历
        # 从起始点开始，找到所有 <h2> 标签，每个 <h2> 代表一个工作经历
        next_node = work_experience_start.find_next_sibling()
        while next_node and next_node.name != 'h1':
            if next_node.name == 'h2':
                new_experience = {}  # 初始化一个空字典来存储当前工作经历的信息

                # 找到 <h2> 标签之后的 <ul>
                ul = next_node.find_next_sibling('ul')
                if ul:
                    li_items = ul.find_all('li')
                    description_started = False  # 标记描述部分是否开始

                    for li in li_items:
                        li_text = li.get_text().strip()
                        if not li_text:
                            continue  # 跳过空的 <li>

                        if not description_started:
                            # 尝试解析字段
                            for separator in SEPARATORS:
                                if separator in li_text:
                                    try:
                                        key, value = li_text.split(separator, 1)
                                        key = key.strip()
                                        value = value.strip()
                                        if key in key_experience:
                                            new_experience[key_experience[key]] = value
                                        break  # 匹配到分隔符后跳出循环
                                    except Exception as e:
                                        logging.error(f"解析工作经历失败：{li_text} - {str(e)}")
                            else:
                                # 如果没有匹配到字段，可能是描述部分的开始
                                description_started = True
                                new_experience["description"] = []

                        if description_started:
                            # 将后续的 <li> 添加到描述部分
                            new_experience["description"].append(li_text)

                    # 将解析到的工作经历添加到列表中
                    if any(value is not None for value in new_experience.values()):
                        data["work_experience"].append(new_experience)

            # 移动到下一个节点
            next_node = next_node.find_next_sibling()

    # 解析项目经历
    def parse_Project_experience(section, target_key):
        """
    解析项目经验部分

    :param soup: BeautifulSoup 对象，包含整个 HTML 文档
    """

    key_project = {
        "项目名称": "project_name",
        "项目描述": "project_description",
        "技术栈": "tech_stack",
        "角色": "role",
        "开始时间": "start_date",
        "结束时间": "end_date",
        "成果": "results"
    }

    # 确保 data["project_experience"] 是一个列表
    if "project_experience" not in data or not isinstance(data["project_experience"], list):
        data["project_experience"] = []

    # 清空初始值（覆盖初始值）
    data["project_experience"].clear()

    # 找到项目经验的起始点
    project_experience_start = soup.find('h1', string="项目经历")
    if not project_experience_start:
        logging.error("未找到项目经验部分的起始点")
        return

    # 从起始点开始，找到所有 <h2> 标签，每个 <h2> 代表一个项目
    next_node = project_experience_start.find_next_sibling()
    while next_node and next_node.name != 'h1':
        if next_node.name == 'h2':
            new_project = {}  # 初始化一个空字典来存储当前项目的信息

            # 找到 <h2> 标签之后的 <ul>
            ul = next_node.find_next_sibling('ul')
            if ul:
                li_items = ul.find_all('li')
                tech_stack_started = False  # 标记技术栈部分是否开始
                results_started = False  # 标记成果部分是否开始

                for li in li_items:
                    li_text = li.get_text().strip()
                    if not li_text:
                        continue  # 跳过空的 <li>

                    # 尝试解析字段键和字段值
                    for separator in SEPARATORS:
                        if separator in li_text:
                            try:
                                key, value = li_text.split(separator, 1)
                                key = key.strip()
                                value = value.strip()
                                if key in key_project:
                                    if key == "技术栈":
                                        tech_stack_started = True
                                        new_project[key_project[key]] = []
                                    elif key == "成果":
                                        results_started = True
                                        new_project[key_project[key]] = []
                                    else:
                                        new_project[key_project[key]] = value
                                    break  # 匹配到分隔符后跳出循环
                            except Exception as e:
                                logging.error(f"解析项目经验失败：{li_text} - {str(e)}")
                            break  # 匹配到分隔符后跳出循环

                    # 处理技术栈部分
                    if tech_stack_started and not results_started:
                        if separator not in li_text:
                            new_project["tech_stack"].append(li_text)

                    # 处理成果部分
                    if results_started:
                        if separator not in li_text:
                            new_project["results"].append(li_text)

                # 将解析到的项目经验添加到列表中
                if any(value is not None for value in new_project.values()):
                    data["project_experience"].append(new_project)

        # 移动到下一个节点
        next_node = next_node.find_next_sibling()

        # 解析自我评价
        # 解析自我评价
        def parse_self_evaluation(section, target_key):
            """
            解析自我评价部分

            :param section: 自我评价部分的 HTML 节点
            :param target_key: 目标 JSON 键
            """
            key_evaluation = {
                "职业目标": "career_objective",
                "优势": "strengths",
                "兴趣": "interests",
                "描述": "description"
            }
            SEPARATORS = [': ', ':', '：']  # 定义可能的分隔符

            # 确保 data["self_evaluation"] 是一个字典
            if "self_evaluation" not in data or not isinstance(data["self_evaluation"], dict):
                data["self_evaluation"] = {
                    "career_objective": None,
                    "strengths": [],
                    "description": []
                }

            # 清空初始值（覆盖初始值）
            data["self_evaluation"]["career_objective"] = None
            data["self_evaluation"]["strengths"] = []
            data["self_evaluation"]["description"] = []

            # 找到自我评价的起始点
            self_evaluation_start = soup.find('h1', string="自我评价")
            if not self_evaluation_start:
                logging.error("未找到自我评价部分的起始点")
                return

            # 从起始点开始，找到后续的 <ul>
            ul = self_evaluation_start.find_next_sibling('ul')
            if ul:
                li_items = ul.find_all('li')

                for li in li_items:
                    li_text = li.get_text().strip()
                    if not li_text:
                        continue  # 跳过空的 <li>

                    # 尝试解析字段键和字段值
                    for separator in SEPARATORS:
                        if separator in li_text:
                            try:
                                key, value = li_text.split(separator, 1)
                                key = key.strip()
                                value = value.strip()
                                if key in key_evaluation:
                                    if key == "优势":
                                        # 提取优势列表
                                        strengths = [item.strip() for item in value.split("\n")]
                                        data["self_evaluation"]["strengths"].extend(strengths)
                                    elif key == "描述":
                                        # 提取描述列表
                                        descriptions = [item.strip() for item in value.split("\n")]
                                        data["self_evaluation"]["description"].extend(descriptions)
                                    else:
                                        data["self_evaluation"][key_evaluation[key]] = value
                                    break  # 匹配到分隔符后跳出循环
                            except Exception as e:
                                logging.error(f"解析自我评价失败：{li_text} - {str(e)}")
                            break  # 匹配到分隔符后跳出循环

    # 调用解析函数
    parse_section('姓名', 'name', parse_name)
    parse_section('求职意向', 'job_intention', parse_job_intention)
    parse_section('个人信息', 'personal_info', parse_personal_info)
    parse_section('教育背景', 'education', parse_education)
    parse_section('技能', 'skills', parse_skills)
    parse_section('证书', 'certificates', parse_certificates)
    # parse_section('技能证书', 'SC', parse_list_items)
    parse_section('工作经历', 'work_experience', parse_work_experience)
    parse_section('项目经历', 'Project_experience', parse_Project_experience)
    parse_section('自我评价', 'self_evaluation', parse_self_evaluation)

    return data


def parse_markdown_file_to_json(md_file_path, save_to_file=False, output_file_name="output.json"):
    """
    解析 Markdown 文件并返回 JSON 数据

    :param md_file_path: Markdown 文件路径
    :return: 解析后的 JSON 数据
    """
    # 加载配置文件
    config = load_config()
    if not config:
        logging.error("配置文件加载失败，无法继续解析")
        return None

    # 调用解析函数，传入 Markdown 内容和配置数据
    json_data = parse_markdown_to_json(md_file_path, config)

    # 如果需要保存到文件，则调用保存函数
    if save_to_file and json_data:
        save_json_to_file(json_data, output_file_name)

    return json_data

def save_json_to_file(data, file_name="output.json"):
    """
    将 JSON 数据保存到文件中

    :param data: JSON 数据
    :param file_name: 输出文件名，默认为 output.json
    """
    try:
        # 获取当前脚本所在的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(current_dir, file_name)

        # 将 JSON 数据写入文件
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info(f"JSON 数据已成功保存到文件：{output_path}")
    except Exception as e:
        logging.error(f"保存 JSON 数据到文件失败：{str(e)}")

# def main():
#      # 从文件中读取 Markdown 内容
#     md_file_path = os.path.join(os.path.dirname(__file__), '测试.md')
#     md_content = read_markdown_file(md_file_path)
#     if not md_content:
#         logging.error("Markdown 文件加载失败，程序退出")
#         return
#
#     # 解析 Markdown 内容
#     data = parse_markdown_file_to_json(md_file_path)
#
#     # 将解析后的数据以 JSON 格式输出
#     json_output = json.dumps(data, ensure_ascii=False, indent=4)
#     print(json_output)
#
#     # 可选：将 JSON 数据保存到文件
#     with open('output.json', 'w', encoding='utf-8') as json_file:
#         json_file.write(json_output)
#
# if __name__ == "__main__":
#     main()
