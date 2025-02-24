import logging
import markdown
from bs4 import BeautifulSoup

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 分隔符配置
SEPARATORS = [': ', ':', '：']

def parse_markdown_to_json(md_content):
    """
    将 Markdown 格式的简历内容解析为 JSON 格式数据

    :param md_content: Markdown 格式的简历内容
    :return: 解析后的 JSON 数据
    """
    # 将 Markdown 转换为 HTML
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, 'html.parser')

    # 初始化 JSON 数据结构
    data = {
        "name": "",
        "job_intention": "",
        "personal_info": {
            "gender": "",
            "ethnicity": "",
            "age": "",
            "contact": "",
            "email": ""
        },
        "education": [],
        "skills": [],
        "certificates": [],
        "work_experience": [],
        "self_evaluation": ""
    }

    # 键名映射表
    key_mapping = {
        "性别": "gender",
        "民族": "ethnicity",
        "年龄": "age",
        "联系方式": "contact",
        "邮箱": "email"
    }

    # 通用解析函数：解析标题下的内容
    def parse_section(header_text, target_key, parser_func):
        """
        解析指定标题下的内容

        :param header_text: 标题文本
        :param target_key: 目标 JSON 键
        :param parser_func: 解析函数
        """
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
        name_item = section.find_next('li')
        if name_item:
            name_text = name_item.get_text()
            try:
                parts = name_text.split(': ', 1)
                if len(parts) == 2:
                    data[target_key] = parts[1].strip()
            except ValueError:
                logging.error(f"解析姓名 {name_text} 时出现格式错误")

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
        """
        解析教育背景信息

        :param section: 教育背景部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        # 找到教育背景标题下的所有 h2 标签
        edu_items = []
        next_element = section.find_next()
        while next_element and next_element.name != 'h1':
            if next_element.name == 'h2':
                edu_items.append(next_element)
            next_element = next_element.find_next()

        for edu in edu_items:
            try:
                degree, school_info = edu.get_text().split(' @ ')
                school, dates = school_info.rsplit(' (', 1)
                dates = dates.rstrip(')')
                major = edu.find_next('p').get_text().strip()
                data[target_key].append({
                    "degree": degree.strip(),
                    "school": school.strip(),
                    "dates": dates.strip(),
                    "major": major
                })
            except ValueError:
                logging.error(f"解析教育背景 {edu.get_text()} 时出现格式错误")

    # 解析技能和证书（通用函数）
    def parse_list_items(section, target_key):
        """
        解析列表项信息（如技能、证书）

        :param section: 列表项部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        items = section.find_next('ul').find_all('li')
        for item in items:
            data[target_key].append(item.get_text().strip())

    # 解析工作经历
    def parse_work_experience(section, target_key):
        """
        解析工作经历信息

        :param section: 工作经历部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        job_items = section.find_all_next('h2')
        for job in job_items:
            try:
                position, company_info = job.get_text().split(' @ ')
                company, dates = company_info.rsplit(' (', 1)
                dates = dates.rstrip(')')
                details = [detail.get_text().strip() for detail in job.find_next('ul').find_all('li')]
                data[target_key].append({
                    "position": position.strip(),
                    "company": company.strip(),
                    "dates": dates.strip(),
                    "details": details
                })
            except ValueError:
                logging.error(f"解析工作经历 {job.get_text()} 时出现格式错误")

    # 解析自我评价
    def parse_self_evaluation(section, target_key):
        """
        解析自我评价信息

        :param section: 自我评价部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        evaluation_item = section.find_next('p')
        if evaluation_item:
            data[target_key] = evaluation_item.get_text().strip()

    # 调用解析函数
    parse_section('姓名', 'name', parse_name)
    parse_section('求职意向', 'job_intention', parse_job_intention)
    parse_section('个人信息', 'personal_info', parse_personal_info)
    parse_section('教育背景', 'education', parse_education)
    parse_section('职业技能', 'skills', parse_list_items)
    parse_section('证书', 'certificates', parse_list_items)
    parse_section('工作经历', 'work_experience', parse_work_experience)
    parse_section('自我评价', 'self_evaluation', parse_self_evaluation)

    return data