# 宠医助手 · 视觉设计系统规范（方案 B · 暖杏奶油 V2）

> 适用范围：宠物医疗问诊知识问答平台（Web 端优先）
> 设计哲学：Natural Warm Palette —— 自然暖色体系，低饱和、克制用色、温暖可信

---

## 1. 色彩系统 Color System

### 1.1 设计原则

- **Primary 负责品牌识别**：仅用于 Logo、一级按钮、当前选中/激活态、关键图标、重点数字。
- **页面 85~90% 为 Neutral**：背景、文字、边框、卡片。
- **Semantic 色仅用于表达状态**：成功 / 警告 / 危险 / 信息，日常页面露出 ≤ 2%。
- **Danger 是唯一允许高视觉权重的语义色**。
- 所有颜色均来自自然物联想（奶茶、鼠尾草、蜂蜜、陶土、雾蓝、暖灰）。

### 1.2 主色阶 Primary

| Token | 色值 | 使用场景 | 注意事项 |
|------|------|---------|---------|
| `--color-primary-900` | `#6B5045` | Logo、重点标题、Hover、Pressed、强调文字 | 对比度约 7.4:1，可安全用于文字 |
| `--color-primary-700` | `#8C6B5D` | **主按钮**、当前 Tab、当前菜单、当前步骤、关键图标 | 对比度约 4.8:1，白字可用 |
| `--color-primary-500` | `#C7A18E` | 装饰、Tag、辅助强调、Secondary Button 描边、插画 | **不可用于白底白字**，对比度不足 |
| `--color-primary-100` | `#FAF3EC` | 浅色背景、Selected Background、用户消息气泡、hover 底 | 与页面背景过渡自然 |

**Primary 用色禁忌**：
- ❌ 不用于大面积背景
- ❌ 不用于大面积卡片
- ❌ 不用于普通正文
- ❌ 不用于表达语义状态

### 1.3 品牌渐变 Brand Gradient

| Token | 值 | 使用场景 |
|------|-----|---------|
| `--color-gradient-brand` | `linear-gradient(135deg, #FAF3EC 0%, #F4F7F1 100%)` | 品牌插画、登录页装饰、空状态背景、营销卡片 |

- 渐变仅用于装饰性表面，不用于按钮填充或文字背景。
- 渐变上方如有文字，必须使用深色文字并叠加半透明遮罩以保证可读性。

### 1.4 语义色 Semantic

设计原则：**低饱和、自然色系、严格用于语义表达**。

#### Success · 鼠尾草绿

| Token | 色值 | 用途 |
|------|------|------|
| `--color-success-bg` | `#F4F7F1` | 成功提示背景、完成标签背景 |
| `--color-success-border` | `#D6E2CF` | 成功提示边框、完成标签边框 |
| `--color-success-main` | `#6F8A6A` | 图标、进度指示、装饰 |
| `--color-success-dark` | `#53664F` | 成功提示文字、完成标签文字 |

#### Warning · 蜂蜜琥珀

| Token | 色值 | 用途 |
|------|------|------|
| `--color-warning-bg` | `#FFF8EC` | 警告提示背景 |
| `--color-warning-border` | `#F2DFC0` | 警告提示边框 |
| `--color-warning-main` | `#C38A35` | 警告图标 |
| `--color-warning-dark` | `#9A6825` | 警告提示文字 |

#### Danger · 陶土红

| Token | 色值 | 用途 |
|------|------|------|
| `--color-danger-bg` | `#FCF4F1` | 危险提示背景、错误提示背景 |
| `--color-danger-border` | `#E9CEC5` | 危险提示边框 |
| `--color-danger-main` | `#B86B5B` | 危险图标、删除按钮 |
| `--color-danger-dark` | `#8F4E43` | 危险提示文字、删除按钮文字 |

#### Info · 雾灰蓝

| Token | 色值 | 用途 |
|------|------|------|
| `--color-info-bg` | `#F2F6F8` | 信息提示背景 |
| `--color-info-border` | `#D7E2E8` | 信息提示边框 |
| `--color-info-main` | `#6D8795` | 信息图标 |
| `--color-info-dark` | `#536673` | 信息提示文字 |

**语义色用色禁忌**：
- ❌ 不用于一级按钮（Danger 删除按钮除外）
- ❌ 不用于 Tab / 导航
- ❌ 不用于 Logo
- ❌ 不作为页面主视觉色大面积使用

### 1.5 中性色 Neutral

| Token | 色值 | 用途 |
|------|------|------|
| `--color-text-main` | `#3E3836` | 正文标题、主要内容 |
| `--color-text-secondary` | `#6F6763` | 辅助说明、时间戳、Placeholder |
| `--color-border` | `#EDE5DD` | 卡片边框、分割线、输入框默认边框 |
| `--color-surface` | `#FDFBF7` | 页面底层背景 |
| `--color-card` | `#FFFFFF` | 卡片、弹窗、浮层背景 |
| `--color-header` | `#FFF9F5` | 顶部标题栏、侧边栏顶部 |

### 1.6 页面色彩使用比例

| 类型 | 占比 | 作用 |
|------|------|------|
| Neutral | 85~90% | 建立页面骨架，保证呼吸感与专业感 |
| Primary | 8~10% | 品牌识别与核心操作引导 |
| Semantic | ≤ 2% | 仅在状态反馈时出现 |

---

## 2. 字体系统 Typography

### 2.1 字体家族

| 类型 | 字体栈 |
|------|--------|
| 中文主字体 | `"PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif` |
| 等宽字体（色值、数字） | `"JetBrains Mono", ui-monospace, monospace` |

### 2.2 字号与行高

| Token | 字号 | 行高 | 字重 | 用途 |
|-------|------|------|------|------|
| `--font-display` | 28px | 1.3 | 700 | 页面大标题 |
| `--font-h1` | 24px | 1.3 | 700 | 页面标题 |
| `--font-h2` | 20px | 1.35 | 600 | 区块标题 |
| `--font-h3` | 16px | 1.4 | 600 | 卡片标题、小标题 |
| `--font-body` | 15px | 1.6 | 400 | 正文、对话内容 |
| `--font-body-sm` | 13px | 1.5 | 400 | 辅助说明、标签文字 |
| `--font-caption` | 12px | 1.4 | 500 | 徽章、时间戳、提示 |

### 2.3 字体规则

- 中文段落行高保持 **1.6~1.7**，避免文字拥挤。
- 标题避免使用超过 600 的字重，保持温和气质。
- 页面最小字号建议 **12px**，不因追求精致而使用过小文字。
- 数字、金额、色值可使用等宽字体，对齐更整齐。

---

## 3. 间距系统 Spacing

### 3.1 基础单位

基础单位为 **4px**，所有间距均为 4 的倍数。

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-1` | 4px | 图标与文字间距、徽章内边距 |
| `--space-2` | 8px | 小间隙、列表项紧凑间距 |
| `--space-3` | 12px | 按钮内边距垂直方向 |
| `--space-4` | 16px | 卡片内边距、组件之间标准间距 |
| `--space-5` | 20px | 表单组间距 |
| `--space-6` | 24px | 区块间距 |
| `--space-8` | 32px | 大区块间距 |
| `--space-10` | 40px | 页面模块间距 |
| `--space-12` | 48px | 页面顶部/底部留白 |
| `--space-16` | 64px | 超大模块间距 |

### 3.2 使用建议

- 卡片内边距默认为 **24px**。
- 卡片之间、区块之间默认间距为 **24px**。
- 同一组件内元素间距优先使用 **8px / 12px**。
- 文字段落的段间距为字号的 0.5~0.75 倍。

---

## 4. 圆角系统 Radius

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 6px | 按钮、输入框、小标签 |
| `--radius-md` | 12px | 卡片、列表项、提示条 |
| `--radius-lg` | 16px | 消息气泡、弹窗、大面板 |
| `--radius-pill` | 999px | 徽章、标签、头像、胶囊按钮 |

### 4.1 组件圆角规范

| 组件 | 圆角 |
|------|------|
| Primary Button | `6px` |
| Secondary Button | `6px` |
| Input | `6px` |
| Card | `12px` |
| Badge / Tag | `999px` |
| Avatar | `50%` |
| User Bubble | `16px 6px 16px 16px` |
| AI Bubble | `6px 16px 16px 16px` |
| Notice | `12px` |
| Modal / Dialog | `16px` |

---

## 5. 阴影与海拔 Shadow & Elevation

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-xs` | `0 1px 2px rgba(62, 56, 54, 0.04)` | 标题栏、静态卡片 |
| `--shadow-sm` | `0 4px 12px rgba(62, 56, 54, 0.06)` | 卡片 hover、下拉菜单 |
| `--shadow-md` | `0 8px 24px rgba(62, 56, 54, 0.10)` | 弹窗、浮层、Toast |

### 5.1 使用建议

- 白色卡片在浅色背景上默认使用 `--shadow-xs` + `--color-border` 边框。
- 卡片 hover 时阴影加深至 `--shadow-sm`，不使用颜色变化。
- 弹窗、Toast 使用 `--shadow-md` 拉开海拔。
- 阴影色使用暖灰（基于 `--color-text-main`），避免冷黑阴影破坏暖调。

---

## 6. 组件库 Component Library

> 以下所有规格以研发可直接实现的方式描述。

### 6.1 Button 按钮

#### Primary Button

| 属性 | 值 |
|------|-----|
| 背景 | `--color-primary-700` `#8C6B5D` |
| 文字 | `#FFFFFF` |
| Padding | `10px 16px` |
| 圆角 | `--radius-sm` `6px` |
| 字号 | `14px` |
| 字重 | 500 |

状态：
- **Hover**：背景变为 `--color-primary-900` `#6B5045`，轻微上浮 `translateY(-1px)`，阴影 `--shadow-sm`。
- **Active / Pressed**：背景 `--color-primary-900`，无位移。
- **Focus**：外框 `2px solid --color-primary-700`，`outline-offset: 2px`。
- **Disabled**：透明度 `0.4`，cursor `not-allowed`。

#### Secondary Button

| 属性 | 值 |
|------|-----|
| 背景 | `--color-card` `#FFFFFF` |
| 边框 | `1px solid --color-primary-700` |
| 文字 | `--color-primary-700` |
| Padding | `10px 16px` |
| 圆角 | `--radius-sm` |
| 字号 | `14px` |

- **Hover**：背景 `--color-primary-100`。

#### Ghost Button

| 属性 | 值 |
|------|-----|
| 背景 | transparent |
| 文字 | `--color-primary-700` |
| Padding | `10px 12px` |

- **Hover**：背景 `--color-primary-100`。

### 6.2 Input 输入框

| 属性 | 值 |
|------|-----|
| 背景 | `--color-surface` `#FDFBF7` |
| 边框 | `1px solid --color-border` `#EDE5DD` |
| 圆角 | `--radius-sm` `6px` |
| Padding | `10px 14px` |
| 字号 | `14px` |
| 字重 | 400 |
| 文字色 | `--color-text-main` |
| Placeholder | `--color-text-secondary` `70%` 透明度 |

状态：
- **Hover**：边框 `--color-primary-500`。
- **Focus**：边框 `--color-primary-700`，外发光 `0 0 0 3px rgba(144,112,99,0.12)`。
- **Error**：边框 `--color-danger-main`。
- **Disabled**：背景 `#F5F2EF`，文字透明度 `0.5`。

### 6.3 Card 卡片

| 属性 | 值 |
|------|-----|
| 背景 | `--color-card` `#FFFFFF` |
| 边框 | `1px solid --color-border` |
| 圆角 | `--radius-md` `12px` |
| Padding | `24px` |
| 阴影 | `--shadow-xs` |

- **Hover**：阴影 `--shadow-sm`。

### 6.4 Badge / Tag 徽章标签

#### Neutral Tag

| 属性 | 值 |
|------|-----|
| 背景 | `--color-surface` |
| 边框 | `1px solid --color-border` |
| 文字 | `--color-text-secondary` |
| 圆角 | `--radius-pill` |
| Padding | `4px 10px` |
| 字号 | `12px` |

#### Status Tag（Primary）

| 属性 | 值 |
|------|-----|
| 背景 | `--color-primary-100` `#FAF3EC` |
| 文字 | `--color-primary-900` `#6B5045` |

#### Success / Warning / Danger / Info Tag

| 类型 | 背景 | 边框 | 文字 |
|------|------|------|------|
| Success | `--color-success-bg` | `--color-success-border` | `--color-success-dark` |
| Warning | `--color-warning-bg` | `--color-warning-border` | `--color-warning-dark` |
| Danger | `--color-danger-bg` | `--color-danger-border` | `--color-danger-dark` |
| Info | `--color-info-bg` | `--color-info-border` | `--color-info-dark` |

### 6.5 Notice 提示条

| 类型 | 背景 | 边框 | 文字/图标 |
|------|------|------|----------|
| Success | `--color-success-bg` | `--color-success-border` | `--color-success-dark` |
| Warning | `--color-warning-bg` | `--color-warning-border` | `--color-warning-dark` |
| Danger | `--color-danger-bg` | `--color-danger-border` | `--color-danger-dark` |
| Info | `--color-info-bg` | `--color-info-border` | `--color-info-dark` |

- 圆角：`--radius-md` `12px`
- Padding：`12px 14px`
- 字号：`13px`
- 必须包含图标或前缀文字，不依赖颜色传递语义。

### 6.6 Chat Bubble 对话气泡

#### User Bubble

| 属性 | 值 |
|------|-----|
| 背景 | `--color-primary-100` `#FAF3EC` |
| 文字 | `--color-primary-900` `#6B5045` |
| 圆角 | `16px 6px 16px 16px` |
| Padding | `12px 16px` |
| 最大宽度 | 不超过容器 70% |

#### AI Bubble

| 属性 | 值 |
|------|-----|
| 背景 | `--color-card` `#FFFFFF` |
| 边框 | `1px solid --color-border` |
| 文字 | `--color-text-main` |
| 圆角 | `6px 16px 16px 16px` |
| Padding | `12px 16px` |
| 最大宽度 | 不超过容器 70% |

#### Avatar

| 属性 | 值 |
|------|-----|
| 尺寸 | 36×36px |
| 圆角 | 50% |
| 背景 | `--color-primary-100` |
| 文字 | `--color-primary-900` |
| 字号 | 13px |
| 字重 | 700 |

### 6.7 动物医生插画

- **风格**：可爱扁平、几何化处理、2px 圆角描边。
- **用色**：跟随品牌 Primary/Semantic，耳朵/帽子使用 `--color-primary-500` 或 `--color-gradient-brand`。
- **禁止**：使用写实照片、复杂纹理、高饱和度荧光色。

---

## 7. 可访问性 Accessibility

### 7.1 对比度标准

必须满足 **WCAG 2.1 AA**：
- 普通正文：文字与背景对比度 ≥ 4.5:1
- 大号文字 / 按钮文字：对比度 ≥ 3:1
- 图标/装饰元素：对比度 ≥ 3:1

### 7.2 关键对比度对照表

| 前景 | 背景 | 对比度 | 是否可用 |
|------|------|--------|---------|
| `#8C6B5D` Primary 700 | `#FFFFFF` | ~5.0:1 | ✅ 按钮白字 |
| `#6B5045` Primary 900 | `#FFFFFF` | ~7.4:1 | ✅ 标题/Logo |
| `#3E3836` Text Main | `#FDFBF7` | ~11.8:1 | ✅ 正文 |
| `#6F6763` Text Secondary | `#FFFFFF` | ~5.5:1 | ✅ 辅助文字 |
| `#C7A18E` Primary 500 | `#FFFFFF` | ~2.3:1 | ❌ 不可白字 |
| `#9A6825` Warning Dark | `#FFF8EC` | ~5.0:1 | ✅ 警告文字 |
| `#8F4E43` Danger Dark | `#FCF4F1` | ~5.4:1 | ✅ 危险文字 |
| `#53664F` Success Dark | `#F4F7F1` | ~5.7:1 | ✅ 成功文字 |
| `#536673` Info Dark | `#F2F6F8` | ~5.2:1 | ✅ 信息文字 |

### 7.3 焦点与键盘

- 所有可交互元素必须有可见焦点样式。
- 焦点环：`2px solid --color-primary-700`，`outline-offset: 2px`。
- Tab 顺序遵循视觉阅读顺序。
- 触摸目标最小尺寸 **44×44px**。

### 7.4 动效

- 微动画时长控制在 **150~300ms**。
- 支持 `prefers-reduced-motion` 媒体查询，必要时关闭位移动画。

---

## 8. 颜色使用比例与禁忌

### 8.1 推荐页面占比

| 类别 | 占比 | 关键词 |
|------|------|--------|
| Neutral | 85~90% | 背景、文字、边框 |
| Primary | 8~10% | 品牌、CTA、当前选中 |
| Semantic | ≤ 2% | 状态反馈 |

### 8.2 Primary 建议使用位置

✅ Logo  
✅ 一级按钮（Primary Button）  
✅ 当前 Tab  
✅ 当前菜单  
✅ 当前步骤  
✅ 关键数字  
✅ 重要图标  
✅ 用户消息气泡背景  

### 8.3 Primary 避免使用位置

❌ 大面积背景  
❌ 大面积卡片  
❌ 大面积标签  
❌ 普通正文  
❌ 表达成功/失败/警告  

### 8.4 Semantic 使用位置

✅ Toast  
✅ Alert / Notice  
✅ Status Badge  
✅ 风险提示  
✅ 图表状态  

### 8.5 Semantic 避免使用位置

❌ 一级按钮（Danger 删除按钮除外）  
❌ Tab / 导航  
❌ Logo  
❌ 普通交互  

---

## 9. 研发落地 CSS 变量速查

```css
:root {
  /* Primary */
  --color-primary-900: #6B5045;
  --color-primary-700: #8C6B5D;
  --color-primary-500: #C7A18E;
  --color-primary-100: #FAF3EC;

  /* Semantic */
  --color-success-bg: #F4F7F1;
  --color-success-border: #D6E2CF;
  --color-success-main: #6F8A6A;
  --color-success-dark: #53664F;

  --color-warning-bg: #FFF8EC;
  --color-warning-border: #F2DFC0;
  --color-warning-main: #C38A35;
  --color-warning-dark: #9A6825;

  --color-danger-bg: #FCF4F1;
  --color-danger-border: #E9CEC5;
  --color-danger-main: #B86B5B;
  --color-danger-dark: #8F4E43;

  --color-info-bg: #F2F6F8;
  --color-info-border: #D7E2E8;
  --color-info-main: #6D8795;
  --color-info-dark: #536673;

  /* Gradient */
  --color-gradient-brand: linear-gradient(135deg, #FAF3EC 0%, #F4F7F1 100%);

  /* Neutral */
  --color-text-main: #3E3836;
  --color-text-secondary: #6F6763;
  --color-border: #EDE5DD;
  --color-surface: #FDFBF7;
  --color-card: #FFFFFF;
  --color-header: #FFF9F5;

  /* Shadow */
  --shadow-xs: 0 1px 2px rgba(62, 56, 54, 0.04);
  --shadow-sm: 0 4px 12px rgba(62, 56, 54, 0.06);
  --shadow-md: 0 8px 24px rgba(62, 56, 54, 0.10);

  /* Typography */
  --font-sans: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 999px;
}
```

---

## 10. 设计 QA 检查清单

交付开发前，按以下清单复核：

- [ ] 所有 Primary 700 / Primary 900 在目标背景上的对比度 ≥ 4.5:1。
- [ ] 所有 Semantic Dark 文字在对应背景上对比度 ≥ 4.5:1。
- [ ] Primary 500 未用于白底白字。
- [ ] 页面中 Primary 颜色占比未超过 10%。
- [ ] 页面中 Semantic 颜色占比未超过 2%。
- [ ] 所有可交互元素有 Hover / Active / Focus / Disabled 状态。
- [ ] 所有语义状态（成功/警告/危险/信息）同时使用了图标或文字说明。
- [ ] 圆角体系在整个产品中保持一致。
- [ ] 阴影使用暖灰，不冷不跳。
- [ ] 中文正文行高 ≥ 1.6。

---

**文档版本**：V1.0  
**适用范围**：方案 B · 暖杏奶油 V2 设计系统  
**状态**：可直接用于开发落地
