# Device Atlas · 中国市场设备尺寸库

手机、折叠屏和平板的屏幕规格、物理尺度与设计稿对比工作台。

- 单文件网站：`outputs/device-library/index.html`
- 构建：`python3 work/device-library/build.py`
- 验证：`node work/device-library/test.mjs`
- 推送 `main` 后，GitHub Actions 校验并部署到 GitHub Pages。

规格记录来自公开来源，不保证穷尽中国市场。未知首销日期、单型号发货量、逻辑密度保留为空。屏幕毫米值为规格推算；电脑端 1:1 模式需先用实体尺校准。设计稿图片仅在本地浏览器处理。

## 更新

修改源码或数据后，重新构建并验证，提交源码、数据及生成的 HTML，再推送 `main`。工作流会自动部署。页面内容不会自行抓取或更新。
