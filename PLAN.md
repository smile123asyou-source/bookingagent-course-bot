# 演出经纪人继续教育刷课助手 — 项目计划书

## 项目概述
文旅部继续教育平台 (zxpx.mr.mct.gov.cn) 自动挂机看课工具，帮阿阳完成每年继续教育学时。

## 技术选型
- **browser-use** (96K⭐) — Python AI浏览器自动化，自然语言操控
- **Playwright** — 浏览器驱动底层
- **DeepSeek API** — 便宜LLM驱动（阿阳缺钱）
- **ddddocr** — 中文验证码OCR（备选，降低手动输入频率）

## 功能清单

### MVP（今晚可交付）
- [x] 打开 token 链接自动登录（或手动填一次）
- [x] 进入「我的课程」，找到未完成课程
- [x] 自动播放视频 → 监听弹窗 → 点确认
- [x] 一节播完自动切下一节
- [x] 全部完成后通知

### 后续迭代
- [ ] 验证码自动识别（ddddocr）
- [ ] Cookie持久化（免二次登录）
- [ ] 多门课排队自动刷
- [ ] 托盘小图标显示进度

## 平台关键信息
- 登录页：https://zxpx.mr.mct.gov.cn/login.html
- Token: 从上级平台(jgpt.mr.mct.gov.cn)跳转，URL携带
- 登录方式：`RM.login` API，密码MD5，验证码必填
- 登录后跳转：powerLV=1 → /system/index.html
- API前缀：commonUrl（需运行时抓取）

## 开发阶段

### 阶段1：环境搭建 (10分钟)
- pip install browser-use playwright
- playwright install chromium
- 配置 DeepSeek API key

### 阶段2：登录脚本 (15分钟)
- 用 browser-use 导航到 token 链接
- 检测是否自动登录成功
- 如需手动输入，暂停等待阿阳操作

### 阶段3：课程自动播放 (20分钟)
- 进入课程列表 → 找到未完成课程
- 进入播放页 → 监听视频状态
- 处理弹窗 → 自动下一节

### 阶段4：测试验收 (10分钟)
- 阿阳本地跑一遍完整流程
- 确认弹窗处理、课程切换正常

## 验收标准
- [ ] 登录流程跑通（token或手动）
- [ ] 至少完成一门课的自动播放+切换
- [ ] 弹窗（如"继续学习"确认）自动处理
- [ ] 脚本不崩溃跑完所有未完成课程

## 参考项目
- browser-use/browser-use (96K⭐) — 核心引擎
- 无需fork其他项目，直接基于 browser-use 开发

## 成本估算
- DeepSeek API：每节课约消耗 5-10万 token → 约 ¥0.1-0.2/课
- 一学期按20门课算 → ¥2-4，几乎忽略不计
