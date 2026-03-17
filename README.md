# 职业AI风险查询 - 使用说明

## 项目结构

```
├── occupations.py          # 中国职业列表（~300个，可扩展）
├── score.py                # Gemini评分Pipeline（一次性运行）
├── index.html              # 手机可用的查询网页（PWA）
├── manifest.json           # PWA配置
└── occupations_scored.json # 评分结果（运行score.py后生成）
```

---

## 第一步：安装依赖

在终端运行：
```bash
pip install google-generativeai
```

---

## 第二步：测试运行（先跑5个职业确认API Key正常）

```bash
python3 score.py --api-key 你的GEMINI_KEY --test
```

正常输出示例：
```
✓ 已加载 0 条已有评分
▶ 开始评分，共 5 个职业
[1/5] 总经理/CEO ... ✓ 6.5/10 (高)
[2/5] 副总经理 ... ✓ 6.0/10 (高)
...
```

---

## 第三步：完整运行（评分所有职业）

```bash
python3 score.py --api-key 你的GEMINI_KEY --output occupations_scored.json
```

预计耗时：约 5-8 分钟（300个职业，每个间隔1秒）

**注意：** 脚本支持断点续跑。如果中途失败，重新运行会跳过已评分的职业。

---

## 第四步：本地查看网页

```bash
# 在项目目录下启动本地服务器
python3 -m http.server 8000
```

然后在手机或电脑浏览器打开：`http://localhost:8000`

---

## 第五步：部署到网上（让手机随时可用）

### 方式A：Vercel（推荐，免费）
1. 注册 [vercel.com](https://vercel.com)
2. 把项目文件夹上传到 GitHub
3. 在 Vercel 里 Import 该仓库
4. 自动部署，获得 https://xxx.vercel.app 链接
5. 手机访问该链接，点"添加到主屏幕"即可像App一样使用

### 方式B：GitHub Pages（免费）
1. 上传到 GitHub 仓库
2. Settings → Pages → 选择 main 分支
3. 获得 https://用户名.github.io/仓库名 链接

---

## 使用说明

### 两种查询模式

**模式1：离线查询（有数据库）**
- 运行 score.py 生成 occupations_scored.json 后
- 搜索已收录职业，直接返回，无需API，速度极快

**模式2：实时AI查询（无数据库或职业未收录）**
- 在网页顶部填入 Gemini API Key
- 搜索任意职业，实时调用Gemini评分
- API Key 仅保存在你自己浏览器的本地存储中，不上传服务器

---

## 常见问题

**Q: Gemini免费版有调用限制吗？**
A: 免费版每分钟15次请求，每天1500次。评分300个职业约需5分钟，不会超限。

**Q: 评分准确吗？**
A: 这是基于Karpathy方法论的AI估算，反映大趋势，不是精确预测。具体职业因公司、行业、地区而异。

**Q: 可以添加更多职业吗？**
A: 可以，在 occupations.py 的 OCCUPATIONS 列表末尾添加职业名，然后重新运行 score.py。

---

## 数据来源与致谢

- 评分方法论：[Karpathy/jobs](https://github.com/karpathy/jobs)
- 职业列表：参考人社部职业分类大典（2022版）整理
- 评分模型：Google Gemini Flash
