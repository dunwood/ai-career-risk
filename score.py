"""
中国职业AI风险评分 Pipeline
使用 Gemini Flash 对职业进行0-10评分
运行方式: python3 score.py --api-key YOUR_GEMINI_API_KEY
"""

import json
import time
import argparse
import os
import sys
from occupations import OCCUPATIONS

try:
    import google.generativeai as genai
except ImportError:
    print("请先安装: pip install google-generativeai")
    sys.exit(1)

# ── 评分提示词 ──────────────────────────────────────────────
SYSTEM_PROMPT = """你是一位分析AI对中国职业市场冲击的专家。

请对给定职业进行AI暴露度评分（0-10），衡量AI将在未来5-10年内多大程度上重塑这个职业。

评分考虑两个维度：
1. 直接自动化：AI直接执行该职业的核心任务
2. 间接影响：AI大幅提升单人产出，导致需要的人数减少

关键判断标准：
- 如果该职业的核心工作能完全在电脑上完成（写作、编程、分析、沟通），AI暴露度天然偏高（7+）
- 如果该职业需要实体存在、手工操作或实时人际互动，天然有保护屏障

评分锚点（中国市场校准）：
- 0-1 极低：建筑工人、清洁工、焊工
- 2-3 低：电工、水管工、厨师、护士
- 4-5 中等：教师、医生（临床）、销售
- 6-7 高：会计、律师、市场经理、教研员
- 8-9 极高：软件工程师、平面设计师、翻译、数据分析师
- 10 最高：数据录入员、电话客服、速记员

特别注意中国市场特殊性：
- 政府/体制内岗位受政策保护，AI冲击节奏慢于市场
- 电商/直播等中国特有职业需结合平台算法化程度判断
- 制造业工人受机器人冲击更大，而非纯AI

请以JSON格式回复，不要有任何多余文字：
{
  "score": 数字（0-10，可以有0.5步进）,
  "tier": "极低/低/中等/高/极高/最高",
  "rationale": "2-3句话解释，说明AI会冲击哪些核心任务、哪些任务有保护屏障（用中文）"
}"""

# ── 主评分函数 ──────────────────────────────────────────────
def score_occupation(model, occupation: str) -> dict:
    prompt = f"请评估这个中国职业的AI暴露度：{occupation}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=300,
            )
        )
        text = response.text.strip()
        # 清理可能的markdown代码块
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        result = json.loads(text)
        result["occupation"] = occupation
        return result
    except Exception as e:
        return {
            "occupation": occupation,
            "score": -1,
            "tier": "错误",
            "rationale": f"评分失败: {str(e)}"
        }

# ── 断点续跑 ──────────────────────────────────────────────
def load_existing(output_file: str) -> dict:
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {item["occupation"]: item for item in data}
    return {}

def save_results(results: list, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# ── 主流程 ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="中国职业AI风险评分")
    parser.add_argument("--api-key", required=True, help="Gemini API Key")
    parser.add_argument("--output", default="occupations_scored.json", help="输出文件路径")
    parser.add_argument("--delay", type=float, default=1.0, help="每次请求间隔（秒），免费版建议1-2秒")
    parser.add_argument("--test", action="store_true", help="测试模式：只跑前5个职业")
    args = parser.parse_args()

    # 初始化 Gemini
    genai.configure(api_key=args.api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    # 加载已有结果（断点续跑）
    existing = load_existing(args.output)
    print(f"✓ 已加载 {len(existing)} 条已有评分")

    occupations = OCCUPATIONS[:5] if args.test else OCCUPATIONS
    total = len(occupations)
    results = list(existing.values())
    errors = []

    print(f"▶ 开始评分，共 {total} 个职业")
    print(f"  预计耗时：{total * args.delay / 60:.1f} 分钟\n")

    for i, occ in enumerate(occupations):
        # 跳过已评分的
        if occ in existing:
            continue

        print(f"[{i+1}/{total}] {occ} ...", end=" ", flush=True)
        result = score_occupation(model, occ)

        if result["score"] == -1:
            print(f"✗ 失败")
            errors.append(occ)
        else:
            print(f"✓ {result['score']}/10 ({result['tier']})")
            results.append(result)
            existing[occ] = result

        # 每10条保存一次
        if len(results) % 10 == 0:
            save_results(results, args.output)

        time.sleep(args.delay)

    # 最终保存
    save_results(results, args.output)

    print(f"\n{'='*50}")
    print(f"✓ 完成！共评分 {len(results)} 个职业")
    print(f"✗ 失败 {len(errors)} 个：{errors}")
    print(f"📄 结果保存至：{args.output}")

    # 统计摘要
    scored = [r for r in results if r["score"] >= 0]
    if scored:
        avg = sum(r["score"] for r in scored) / len(scored)
        print(f"\n📊 平均AI暴露度：{avg:.1f}/10")
        tiers = {}
        for r in scored:
            tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
        print("分布：")
        for tier, count in sorted(tiers.items()):
            print(f"  {tier}: {count} 个职业")

if __name__ == "__main__":
    main()
