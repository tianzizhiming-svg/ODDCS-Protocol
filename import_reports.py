# -*- coding: utf-8 -*-
"""
AgentBridge 批量导入脚本
功能：
1. 将待导入的 PDF 文件移动到正确的目录结构
2. 更新 schools.json 和 colleges.json
3. 生成前端 index.html 需要的 JS 代码片段
"""
import os, json, shutil, re
from collections import defaultdict

BASE = r"F:\edu_reports"
PENDING = os.path.join(BASE, "待导入")
EMP_DIR = os.path.join(BASE, "2025届毕业生就业质量年度报告及深度解读")
TEACH_DIR = os.path.join(BASE, "2024-2025本科教学质量报告及深度解读")

# ========== 配置：省份映射 ==========
SCHOOL_PROVINCE = {
    "北方工业大学": "北京市高校",
    "宁波大学": "浙江省高校",
    "安徽三联学院": "安徽省高校",
    "芜湖学院": "安徽省高校",
    "郑州升达经贸管理学院": "河南省高校",
}

COLLEGE_PROVINCE = {
    "吉林大学": "吉林省高校",
    "华北水利水电大学": "河南省高校",
    "河南工程学院": "河南省高校",
    "兰州工业学院": "甘肃省高校",
    "吉林工程技术师范学院": "吉林省高校",
    "吉林建筑大学": "吉林省高校",
    "吉林铁道职业技术大学": "吉林省高校",
    "广东轻工职业技术大学": "广东省高校",
    "延安大学": "陕西省高校",
    "西安明德理工学院": "陕西省高校",
    "鄂尔多斯应用技术学院": "内蒙古自治区高校",
    "内蒙古师范大学": "内蒙古自治区高校",
    "包头医学院": "内蒙古自治区高校",
    "内蒙古财经大学": "内蒙古自治区高校",
}

# ========== 配置：英文名映射 ==========
SCHOOL_EN = {
    "北方工业大学": "North China University of Technology",
    "宁波大学": "Ningbo University",
    "安徽三联学院": "Anhui Sanlian University",
    "芜湖学院": "Wuhu University",
    "郑州升达经贸管理学院": "Zhengzhou Shengda University of Economics, Business and Management",
    "吉林大学": "Jilin University",
    "华北水利水电大学": "North China University of Water Resources and Electric Power",
    "河南工程学院": "Henan University of Engineering",
    "兰州工业学院": "Lanzhou Institute of Technology",
    "吉林工程技术师范学院": "Jilin Normal University of Engineering and Technology",
    "吉林建筑大学": "Jilin Jianzhu University",
    "吉林铁道职业技术大学": "Jilin Railway Vocational and Technical University",
    "广东轻工职业技术大学": "Guangdong Industry Polytechnic",
    "延安大学": "Yan'an University",
    "西安明德理工学院": "Xi'an Mingde Institute of Technology",
    "鄂尔多斯应用技术学院": "Ordos Institute of Technology",
    "内蒙古师范大学": "Inner Mongolia Normal University",
    "包头医学院": "Baotou Medical College",
    "内蒙古财经大学": "Inner Mongolia University of Finance and Economics",
}

COLLEGE_EN = {
    "历史文化学院": "School of History and Culture",
    "哲学社会学院": "School of Philosophy and Sociology",
    "外国语言文化学院": "School of Foreign Languages and Cultures",
    "护理学院": "School of Nursing",
    "机械与航空航天工程学院": "School of Mechanical and Aerospace Engineering",
    "汽车工程学院": "School of Automotive Engineering",
    "法学院": "School of Law",
    "物理学院": "School of Physics",
    "生命科学学院": "School of Life Sciences",
    "经济学院": "School of Economics",
    "软件学院": "School of Software",
    "信息工程学院": "School of Information Engineering",
    "电气工程学院": "School of Electrical Engineering",
    "电气信息工程学院": "School of Electrical and Information Engineering",
    "纺织工程学院": "School of Textile Engineering",
    "医学院": "School of Medicine",
}

# ========== 维度名称标准化 ==========
DIMENSION_MAP = {
    "师资队伍与教学投入": "01-师资队伍与教学投入",
    "师资力量与教学投入": "01-师资队伍与教学投入",
    "生源质量与培养规模": "02-生源质量与培养规模",
    "生源质量与入学机会": "02-生源质量与培养规模",
    "教学经费与硬件资源": "03-教学经费与硬件资源",
    "办学投入与硬件设施": "03-教学经费与硬件资源",
    "课程设置与教学实施": "04-课程设置与教学实施",
    "课程体系与教学体验": "04-课程设置与教学实施",
    "专业实力与品牌特色": "04-课程设置与教学实施",
    "学生发展与学业支持": "05-学生发展与学业支持",
    "在校支持与成长环境": "05-学生发展与学业支持",
    "毕业要求与学习成果": "06-毕业要求与学习成果",
    "毕业门槛与学业成果": "06-毕业要求与学习成果",
    "就业质量与发展前景": "07-就业质量与发展前景",
    "毕业出路与发展前景": "07-就业质量与发展前景",
    "专业建设质量": "08-专业建设质量",
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_id(data, prefix):
    max_num = 0
    for key in data:
        if key.startswith(prefix):
            num = int(key[1:])
            if num > max_num:
                max_num = num
    return f"{prefix}{max_num + 1:03d}"

def main():
    # 加载现有数据
    schools = load_json(os.path.join(BASE, "schools.json"))
    colleges = load_json(os.path.join(BASE, "colleges.json"))

    # 扫描待导入文件
    files = [f for f in os.listdir(PENDING) if f.endswith('.pdf')]
    print(f"找到 {len(files)} 个待导入文件")

    # ===== 分类 =====
    emp_files = []  # 就业报告
    teach_files = defaultdict(list)  # 教学报告: {学院key: [files]}

    for f in files:
        if f.startswith("七大维度深度解读"):
            emp_files.append(f)
        elif re.match(r'^\d{2}-', f):
            # 教学报告维度文件
            teach_files[f].append(f)  # 先用文件名做key，后面解析
        else:
            print(f"  ⚠️ 未知文件类型: {f}")

    # ===== 解析教学报告 =====
    # 从文件名提取 学校+学院 信息
    college_entries = {}  # {(school_cn, college_cn): [file_tuples]}

    for f in files:
        if not re.match(r'^\d{2}-', f):
            continue
        # 去掉编号前缀
        name_part = re.sub(r'^\d{2}-', '', f)
        # 去掉 .pdf 后缀
        name_part = name_part.replace('.pdf', '').replace(' (1)', '')
        # 去掉 "：xxx解读" 后缀，提取学校+学院
        # 格式: "维度名：学校名学院名2024-2025年度本科教学质量报告解读"
        # 或: "维度名：学校名2024-2025本科教学质量报告深度解读"

        # 找到 "：" 后面的部分
        if '：' in name_part:
            after_colon = name_part.split('：', 1)[1]
        elif ':' in name_part:
            after_colon = name_part.split(':', 1)[1]
        else:
            print(f"  ⚠️ 无法解析: {f}")
            continue

        # 提取维度名
        dim_name = name_part.split('：')[0].split(':')[0] if '：' in name_part else name_part.split(':')[0]
        std_dim = DIMENSION_MAP.get(dim_name, dim_name)

        # 从 after_colon 提取学校+学院
        # 去掉年份后缀
        clean = re.sub(r'2024-2025.*$', '', after_colon).strip()
        # 去掉"质量报告解读"等后缀
        clean = re.sub(r'质量报告.*$', '', clean).strip()
        clean = re.sub(r'年度本科教学.*$', '', clean).strip()
        clean = re.sub(r'本科教学质量报告.*$', '', clean).strip()
        clean = re.sub(r'高等职业教育质量报告.*$', '', clean).strip()

        # 尝试匹配学校+学院
        school_cn = None
        college_cn = None
        for s in COLLEGE_PROVINCE:
            if clean.startswith(s):
                school_cn = s
                college_cn = clean[len(s):].strip()
                break

        if not school_cn:
            print(f"  ⚠️ 无法识别学校: {f} -> {clean}")
            continue

        if not college_cn:
            college_cn = "全校"  # 整个学校的报告

        key = (school_cn, college_cn)
        if key not in college_entries:
            college_entries[key] = []
        college_entries[key].append((std_dim, f))

    # ===== 处理就业报告 =====
    print(f"\n===== 就业报告 ({len(emp_files)} 份) =====")
    new_schools_js = []
    for f in emp_files:
        # 提取学校名: "七大维度深度解读北方工业大学2025届毕业生就业质量报告.pdf"
        name = f.replace("七大维度深度解读", "").replace(".pdf", "")
        name = re.sub(r'2025届.*$', '', name).strip()
        name = re.sub(r'2025年.*$', '', name).strip()

        school_cn = name
        province = SCHOOL_PROVINCE.get(school_cn, "其他")
        school_en = SCHOOL_EN.get(school_cn, school_cn)

        sid = get_next_id(schools, 'S')
        file_name = f"{school_cn}2025毕业生就业质量报告.pdf"

        # 创建目录
        school_dir = os.path.join(EMP_DIR, province, f"{school_cn}2025届毕业生就业质量年度报告及解读")
        os.makedirs(school_dir, exist_ok=True)

        # 移动文件
        src = os.path.join(PENDING, f)
        dst = os.path.join(school_dir, file_name)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  ✅ {school_cn} -> {province}")
        else:
            print(f"  ❌ 文件不存在: {src}")

        # 更新 schools.json
        schools[sid] = {
            "name_cn": school_cn,
            "file": file_name,
            "province": province,
            "type": "employment"
        }

        new_schools_js.append({
            "id": sid,
            "cn": school_cn,
            "en": school_en
        })

    # ===== 处理教学报告 =====
    print(f"\n===== 教学报告 ({len(college_entries)} 个学院) =====")
    new_colleges_js = []

    for (school_cn, college_cn), dim_files in sorted(college_entries.items()):
        province = COLLEGE_PROVINCE.get(school_cn, "其他")
        school_en = SCHOOL_EN.get(school_cn, school_cn)
        college_en = COLLEGE_EN.get(college_cn, college_cn)

        cid = get_next_id(colleges, 'C')

        # 创建目录
        if college_cn == "全校":
            folder_name = f"{school_cn}2024-2025本科教学质量报告及解读"
        else:
            folder_name = f"{school_cn}{college_cn}2024-2025本科教学质量报告及解读"

        # 确定父目录名
        parent_dir_name = f"{school_cn}本科教学质量报告"
        if "解读" in folder_name or "深度" in folder_name:
            parent_dir_name += "及解读"

        college_dir = os.path.join(TEACH_DIR, province, parent_dir_name, folder_name)
        os.makedirs(college_dir, exist_ok=True)

        # 移动文件并重命名
        files_list = []
        for std_dim, orig_name in dim_files:
            # 标准化文件名
            new_name = f"{std_dim}.pdf"
            src = os.path.join(PENDING, orig_name)
            dst = os.path.join(college_dir, new_name)
            if os.path.exists(src):
                shutil.copy2(src, dst)
            # 处理 (1) 副本
            src_copy = os.path.join(PENDING, orig_name.replace('.pdf', ' (1).pdf'))
            if os.path.exists(src_copy):
                shutil.copy2(src_copy, dst)

            dim_num = std_dim.split('-')[0]
            files_list.append({
                "dimension": dim_num,
                "filename": new_name
            })

        # 更新 colleges.json
        colleges[cid] = {
            "school": school_cn,
            "college": f"{school_cn}{college_cn}" if college_cn != "全校" else school_cn,
            "province": province,
            "files": files_list
        }

        new_colleges_js.append({
            "id": cid,
            "schoolCn": school_cn,
            "collegeCn": college_cn if college_cn != "全校" else "",
            "schoolEn": school_en,
            "collegeEn": college_en
        })

        print(f"  ✅ {school_cn} - {college_cn} ({len(files_list)} 个维度)")

    # ===== 保存 JSON =====
    save_json(os.path.join(BASE, "schools.json"), schools)
    save_json(os.path.join(BASE, "colleges.json"), colleges)
    print(f"\n✅ schools.json 已更新 (共 {len(schools)} 条)")
    print(f"✅ colleges.json 已更新 (共 {len(colleges)} 条)")

    # ===== 生成前端代码片段 =====
    print("\n===== 前端代码片段 =====")
    print("\n// 新增就业报告（添加到 employmentSchools 数组）：")
    for s in new_schools_js:
        print(f"    {{ id: '{s['id']}', cn: '{s['cn']}', en: '{s['en']}' }},")

    print("\n// 新增教学报告（添加到 teachingColleges 数组）：")
    for c in new_colleges_js:
        if c['collegeCn']:
            print(f"    {{ id: '{c['id']}', schoolCn: '{c['schoolCn']}', collegeCn: '{c['collegeCn']}', schoolEn: '{c['schoolEn']}', collegeEn: '{c['collegeEn']}' }},")
        else:
            print(f"    // TODO: {c['schoolCn']} (全校报告，需要手动确认学院名)")

    print("\n===== 完成！=====")
    print("下一步：")
    print("1. 检查待导入文件夹中是否还有未处理的文件")
    print("2. 将上面的前端代码片段添加到 index.html")
    print("3. 重启后端: nssm restart AgentBridge-API")
    print("4. 验证新 API 端点返回 402")

if __name__ == "__main__":
    main()
