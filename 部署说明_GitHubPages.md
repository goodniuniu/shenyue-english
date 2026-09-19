# 部署到 GitHub Pages 的说明

网站成品已生成在 `docs/` 目录（含 `.nojekyll`，无需额外配置）。按以下步骤发布：

## 第一步：在 GitHub 创建仓库

1. 打开 https://github.com/new ，新建一个仓库，例如命名为 `shenyue-english`
2. 设为 Public（GitHub Pages 免费版要求公开仓库；如用 Private 需 GitHub Pro）

## 第二步：推送项目到 GitHub

在项目文件夹中执行（已装 Git 的情况下）：

```bash
cd "E:\MyOutput\AI_Project\申悦学习-AI指导英语学习"
git remote add origin https://github.com/<你的用户名>/shenyue-english.git
git branch -M main
git push -u origin main
```

> 项目已 `git init` 并完成首次提交，直接加 remote 推送即可。
> 提示：`node_modules/` 体积大且不需要上传，项目中的 `.gitignore` 已排除它。
> 如沿用物理项目的网络环境：SSH 走 443 端口 + 本地代理 7897，首次大推送慢属正常。

## 第三步：开启 GitHub Pages

1. 打开仓库页面 → 顶部 **Settings** → 左侧 **Pages**
2. **Source** 选择 `Deploy from a branch`
3. Branch 选择 `main`，目录选择 `/docs`，点 **Save**
4. 等待 1~3 分钟，刷新该页面，上方会显示访问地址，形如：
   `https://<你的用户名>.github.io/shenyue-english/`

## 日常更新流程

1. 修改 `知识库/`、`家长支持/` 或辅导计划 Markdown 文件（或让 AI 入库新错题）
2. 运行 `python build_site.py` 重新生成 `docs/`（卡片改动再跑 `python build_print_pack.py` 更新打印包）
3. `git add . && git commit -m "更新内容" && git push`
4. 网站约 1 分钟后自动更新

## 备注

- 数学公式由本地 KaTeX（`assets/katex/` 随构建拷入 `docs/`）在浏览器端渲染，离线也可用；英语卡基本无公式，骨架保留以兼容姊妹项目。
- 若以后想绑定自己的域名（如 english.example.com），在 Pages 设置里填域名，
  并在 DNS 添加 CNAME 记录指向 `<你的用户名>.github.io` 即可。
