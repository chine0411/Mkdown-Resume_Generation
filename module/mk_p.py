import logging
import markdown
import re
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
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')

    # 初始化 JSON 数据结构
    data = {
        "name": None,
        "job_intention": None,
        "personal_info": {
            "gender": None,
            "ethnicity": None,
            "age": None,
            "contact": None,
            "e_mail": None,
            "face": None,
        },
        "education": [],
        "skills": [],
        "certificates": [],
        "SC": [],
        "work_experience": [],
        "Project_experience": [],
        "self_evaluation": None,
    }

    # 键名映射表
    key_mapping = {
        "性别": "gender",
        "民族": "ethnicity",
        "年龄": "age",
        "联系方式": "contact",
        "邮箱": "e_mail"
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
        """解析教育背景信息"""
        edu_items = []
        next_element = section.find_next()
        while next_element and next_element.name != 'h1':
            if next_element.name == 'h2':
                edu_items.append(next_element)
            next_element = next_element.find_next()

        for edu in edu_items:
            try:
                # 使用正则表达式匹配教育信息
                edu_text = edu.get_text().strip()
                degree_match = re.match(r'^([^|]+)\s*\|\s*(.+?)\s*\（(.+?)\）$', edu_text)
                if not degree_match:
                    raise ValueError("教育信息格式错误")
                degree = degree_match.group(1).strip()
                school = degree_match.group(2).strip()
                dates_str = degree_match.group(3).strip()  # 已包含括号

                # 解析日期范围
                dates = re.findall(r'\d{4}\.\d{2} - \d{4}\.\d{2}', dates_str)
                if not dates:
                    raise ValueError("日期格式错误")
                start_date, end_date = dates[0].split(' - ')

                # 处理主修课程
                major_p = edu.find_next('ul')
                major = major_p.get_text().strip() if major_p else ""

                data[target_key].append({
                    "degree": degree,
                    "school": school,
                    "start_date": start_date,
                    "end_date": end_date,
                    "major": major
                })
            except Exception as e:
                logging.error(f"解析教育背景失败：{edu.get_text()} - {str(e)}")

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
        """解析工作经历信息"""
        work_items = []
        # 找到当前h1之后的所有h2，直到下一个h1
        current_node = section.find_next()
        while current_node and current_node.name != 'h1':
            if current_node.name == 'h2':
                work_items.append(current_node)
            current_node = current_node.find_next()

        for job in work_items:
            try:
                # 使用竖线分割职位和公司信息
                job_parts = job.get_text().strip().split(' | ')
                if len(job_parts) < 2:
                    raise ValueError("工作经历格式错误")

                position = job_parts[0].strip()
                company_info = ' '.join(job_parts[1:]).strip()

                # 分割公司和日期
                company_dates = company_info.rsplit('（', 1)
                if len(company_dates) != 2:
                    raise ValueError("公司日期格式错误")
                company = company_dates[0].strip()
                dates = company_dates[1][:-1].strip()  # 移除右括号

                # 解析详细信息
                details_ul = None
                node = job.find_next()
                while node and node.name != 'ul':
                    node = node.find_next()
                if node and node.name == 'ul':
                    details_ul = node

                details = []
                if details_ul:
                    for li in details_ul.find_all('li'):
                        stripped_text = li.get_text().strip()
                        if stripped_text:
                            details.append(stripped_text)

                data[target_key].append({
                    "position": position,
                    "company": company,
                    "dates": dates,
                    "details": details
                })
            except Exception as e:
                logging.error(f"解析工作经历失败：{job.get_text()} - {str(e)}")

    # 解析项目经历
    def parse_Project_experience(section, target_key):
        """解析项目经历信息"""
        Pro_items = section.find_all_next('h2')
        for Pro in Pro_items:
            try:
                project_name = Pro.get_text().strip().lstrip('## ').rstrip('\n')

                # 直接解析后续内容块而非特定容器
                content_blocks = []
                current_block = None
                next_node = Pro.find_next()

                while next_node and (next_node.name == 'p' or next_node.name == 'ul'):
                    if next_node.name == 'p' and not current_block:
                        content_blocks.append(('description', next_node.get_text().strip()))
                    elif next_node.name == 'ul':
                        items = [li.get_text().strip() for li in next_node.find_all('li')]
                        content_blocks.append(('modules', items))
                    next_node = next_node.find_next()

                description = ""
                tech_stack = []
                achievement = ""

                for block_type, content in content_blocks:
                    if block_type == 'description':
                        description = content, print('描述', description)
                    elif block_type == 'modules':
                        tech_stack = [item for item in content if item.startswith('技术栈')], print('技术栈', tech_stack)
                        achievement = [item for item in content if item.startswith('个人成果')][0] if any(
                            item.startswith('个人成果') for item in content) else ""
                        print('个人成果')

                data[target_key].append({
                    "project_name": project_name,
                    "description": description,
                    "tech_stack": tech_stack,
                    "achievement": achievement
                })
            except Exception as e:
                logging.error(f"解析项目经历失败：{Pro.get_text()} - {str(e)}")

    # 解析自我评价
    def parse_self_evaluation(section, target_key):
        """
        解析自我评价信息

        :param section: 自我评价部分的 HTML 节点
        :param target_key: 目标 JSON 键
        """
        evaluation_item = section.find_next()
        if evaluation_item:
            data[target_key] = evaluation_item.get_text().strip()

    # 调用解析函数
    parse_section('姓名', 'name', parse_name)
    parse_section('求职意向', 'job_intention', parse_job_intention)
    parse_section('个人信息', 'personal_info', parse_personal_info)
    parse_section('教育背景', 'education', parse_education)
    parse_section('职业技能', 'skills', parse_list_items)
    parse_section('证书', 'certificates', parse_list_items)
    parse_section('技能证书', 'SC', parse_list_items)
    parse_section('工作经历', 'work_experience', parse_work_experience)
    parse_section('项目经历', 'Project_experience', parse_Project_experience)
    parse_section('自我评价', 'self_evaluation', parse_self_evaluation)

    return data

# def main():
#
#     md_content="""
#    # 张三的简历
#
# # 求职意向
# 算法工程师
#
# # 个人信息
# - 性别：男
# - 民族：汉族
# - 年龄：28
# - 联系方式：138-0013-8000
# - 邮箱：zhangsan@email.com
#
#
#
# # 教育背景
# ## 上海交通大学 | 计算机科学与技术硕士（2018.09 - 2021.06）
# - GPA：3.8/4.0
# - 主修课程：数据结构、机器学习、操作系统
#
# # 工作经历
# ## 腾讯科技 | 算法工程师（实习）（2020.07 - 2020.12）
# - **项目经验**：
#   - 开发基于深度学习的用户行为分析系统，提升点击率15%
#   - 使用Python/TensorFlow构建推荐模型，日均处理100万级数据
# - **技术栈**：
#   - Python、TensorFlow、PyTorch
#   - SQL、MySQL、Redis
#
# ## 百度研究院 | 研究助理（2019.09 - 2019.12）
# - **研究成果**：
#   - 参与自然语言处理论文《BERT在少样本学习中的应用》撰写
#   - 实现基于Transformer的文本摘要模型，ROUGE-LUKE得分提升8%
#
#
# # 项目经历
# ## 智能简历生成系统（个人项目）
# - **目标**：通过AI生成个性化简历
# - **技术实现**：
#   - 使用GPT-4 API解析用户输入
#   - 基于HTML/CSS生成响应式简历模板
#   - 集成GitHub/LinkedIn数据自动填充
# - **成果**：开源项目地址 [https://github.com/zhangsan/resume-generator](https://github.com/zhangsan/resume-generator)
#
# ## 在线教育平台（团队项目）
# - **角色**：前端开发工程师
# - **技术栈**：
#   - React.js、Vue.js
#   - Redux、Axios
#   - WebSocket实时通信
# - **亮点**：
#   - 重构用户中心页面，首屏加载速度提升40%
#   - 实现课程直播实时弹幕功能
#
# # 技能证书
# - **编程语言**：Python（熟练）、Java（中级）、Go（了解）
# - **证书**：
#   - AWS Certified Solutions Architect
#   - PADI Open Water Diver执照
#
# # 自我评价
# - 5年算法研发经验，主导过3个百万级用户项目
# - 擅长数据建模与机器学习算法优化
# - 英语CET-6，可流利阅读技术文档
#
# # 其他信息
# - GitHub：https://github.com/zhangsan
# - 技术博客：https://zhangsan.tech"""
#     data = parse_markdown_to_json(md_content)
#     print(data,end=" \n")
#
#
# if __name__ == "__main__":
#     main()
