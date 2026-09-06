"""
宠医助手 —— FIP 知识推理系统首页（静态呈现版）。

基于 Gradio + 自定义 CSS/JS 实现：
- 左 / 中 / 右三栏响应式布局
- 右侧面板：默认隐藏、滑入、全屏覆盖、收起
- 左侧边栏：展开 / 缩略（hover logo 变为展开按钮）
- 小屏默认左侧缩略，优先保证常规 PC 端效果
- 静态文案与配色严格参考 design-system-spec.md 方案 B

Hugging Face Spaces 默认入口：本文件 app.py
"""

from __future__ import annotations

import base64
import os
import threading
from datetime import datetime
from pathlib import Path

import gradio as gr

from core.logging import FeishuLogger
from core.pipeline import Pipeline

# 飞书日志（访问行为 / 用户反馈）。配置缺失时内部自动 no-op，不阻塞主流程。
logger = FeishuLogger()


# ---------------------------------------------------------------------------
# 静态首页 HTML（包含结构与样式/脚本）
# ---------------------------------------------------------------------------
HOMEPAGE_HTML = """
<div class="app-shell" id="appShell">
  <!-- 左侧边栏 -->
  <aside class="left-sidebar" id="leftSidebar">
    <div class="sidebar-content">
      <!-- 顶部 Header -->
      <div class="left-header">
        <div class="brand">
          <img src="file=asset/logo.jpg" class="brand-logo" alt="宠医助手" />
          <div class="brand-text">
            <div class="brand-title">宠医助手</div>
            <div class="brand-subtitle">让爱宠更健康</div>
          </div>
        </div>
        <button class="icon-btn collapse-btn" id="collapseLeftBtn" data-tooltip="收起侧边栏" aria-label="收起侧边栏">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#6F6763" stroke-width="2">
            <rect x="3" y="5" width="18" height="14" rx="2" />
            <line x1="9" y1="5" x2="9" y2="19" />
          </svg>
        </button>
      </div>

      <!-- 新建任务 -->
      <button class="primary-btn new-task-btn">
        <span class="plus-icon">+</span>
        <span>新建任务</span>
      </button>

      <!-- 导航 -->
      <nav class="nav-menu">
        <a class="nav-item" href="#">
          <span class="nav-icon nav-icon-db">
<svg viewBox="0 0 1024 1024" width="18" height="18" aria-hidden="true"><path d="M245.077333 375.466667a34.133333 34.133333 0 0 1-30.72-49.066667 401.066667 401.066667 0 0 1 363.093334-228.181333 34.133333 34.133333 0 0 1 0 68.266666 333.397333 333.397333 0 0 0-301.653334 189.781334 34.133333 34.133333 0 0 1-30.72 19.2zM577.450667 911.189333A401.066667 401.066667 0 0 1 214.442667 682.666667a34.133333 34.133333 0 1 1 61.44-29.866667 333.312 333.312 0 0 0 301.568 190.122667 34.133333 34.133333 0 0 1 0 68.266666zM898.218667 724.224a33.450667 33.450667 0 0 1-17.066667-4.522667 34.133333 34.133333 0 0 1-12.714667-46.592 340.906667 340.906667 0 0 0-10.24-353.536 34.133333 34.133333 0 0 1 57.258667-37.205333 409.088 409.088 0 0 1 12.202667 424.618667 34.133333 34.133333 0 0 1-29.44 17.237333zM765.525333 283.306667a114.517333 114.517333 0 1 1 113.834667-114.517334A114.346667 114.346667 0 0 1 765.525333 283.306667z m0-160.682667a46.250667 46.250667 0 1 0 45.568 46.165333 45.994667 45.994667 0 0 0-45.568-46.165333zM156.501333 619.178667a114.517333 114.517333 0 1 1 113.92-114.517334 114.346667 114.346667 0 0 1-113.92 114.517334z m0-160.682667a46.250667 46.250667 0 1 0 45.653334 46.165333 45.994667 45.994667 0 0 0-45.653334-46.165333zM802.133333 969.642667a114.517333 114.517333 0 1 1 113.92-114.432A114.346667 114.346667 0 0 1 802.133333 969.642667z m0-160.682667a46.250667 46.250667 0 1 0 45.653334 46.250667A45.994667 45.994667 0 0 0 802.133333 808.96zM577.450667 655.701333a151.04 151.04 0 1 1 150.186666-150.954666 150.698667 150.698667 0 0 1-150.186666 150.954666z m0-233.728a82.773333 82.773333 0 1 0 81.92 82.773334 82.346667 82.346667 0 0 0-81.92-82.773334z" fill="#3E3836"/><path d="M649.472 443.733333a33.621333 33.621333 0 0 1-15.701333-3.84 34.133333 34.133333 0 0 1-14.592-45.994666l85.333333-165.290667a34.133333 34.133333 0 0 1 60.586667 31.402667l-85.333334 165.290666A34.133333 34.133333 0 0 1 649.472 443.733333zM273.664 541.952a34.133333 34.133333 0 0 1-1.962667-68.266667l184.832-10.837333a34.133333 34.133333 0 0 1 4.010667 68.266667L275.712 541.866667zM745.472 807.338667a34.133333 34.133333 0 0 1-29.781333-17.066667l-91.648-162.133333a34.133333 34.133333 0 0 1 59.733333-33.621334l91.648 162.133334a34.133333 34.133333 0 0 1-12.970667 46.506666 33.024 33.024 0 0 1-16.981333 4.181334z" fill="#3E3836"/></svg>
          </span>
          <span>图数据库</span>
        </a>
        <a class="nav-item" href="#">
          <span class="nav-icon nav-icon-doc">
<svg viewBox="0 0 1024 1024" width="18" height="18" aria-hidden="true"><path d="M708.096 980.992H163.584c-58.624 0-106.24-47.616-106.24-106.24V161.536c0-58.624 47.616-106.24 106.24-106.24h544.512c55.552 0 106.24 44.544 106.24 93.44v713.216c0 68.864-44.8 119.04-106.24 119.04zM163.584 116.736c-24.576 0-44.8 20.224-44.8 44.8v713.216c0 24.576 20.224 44.8 44.8 44.8h544.512c26.88 0 44.8-23.04 44.8-57.6V148.736c0-10.752-19.456-32-44.8-32H163.584z" fill="#3E3836"/><path d="M518.912 620.544H227.584c-16.896 0-30.72-13.824-30.72-30.72s13.824-30.72 30.72-30.72h291.328c16.896 0 30.72 13.824 30.72 30.72s-13.824 30.72-30.72 30.72zM431.872 772.864H227.584c-16.896 0-30.72-13.824-30.72-30.72s13.824-30.72 30.72-30.72h204.288c16.896 0 30.72 13.824 30.72 30.72s-13.824 30.72-30.72 30.72zM606.976 442.624H259.84c-35.072 0-63.744-28.672-63.744-63.744v-106.24c0-35.072 28.672-63.744 63.744-63.744h347.136c35.072 0 63.744 28.672 63.744 63.744V378.88c0 35.072-28.672 63.744-63.744 63.744z m-347.136-172.288c-1.28 0-2.304 1.024-2.304 2.304V378.88c0 1.28 1.024 2.304 2.304 2.304h347.136c1.28 0 2.304-1.024 2.304-2.304v-106.24c0-1.28-1.024-2.304-2.304-2.304H259.84zM897.024 980.48h-248.32c-16.896 0-30.72-13.824-30.72-30.72s13.824-30.72 30.72-30.72h248.32c8.704 0 15.616-7.168 15.616-15.616V435.968c0-8.704-7.168-15.616-15.616-15.616h-111.36c-16.896 0-30.72-13.824-30.72-30.72s13.824-30.72 30.72-30.72h111.36c42.496 0 77.056 34.56 77.056 77.056v467.2c0.256 42.752-34.56 77.312-77.056 77.312z" fill="#3E3836"/></svg>
          </span>
          <span>文献库</span>
        </a>
        <a class="nav-item" href="#">
          <span class="nav-icon">
<svg viewBox="0 0 1024 1024" width="18" height="18" aria-hidden="true"><path d="M191.4 765.1c0 22.6 18.3 41 41 41h158.1c22.6 0 41-18.3 41-41 0-22.6-18.3-41-41-41H232.3c-22.6 0-40.9 18.3-40.9 41zM889.3 855.1h-40.9 16.2c13.8-0.8 24.7-12.2 24.7-26.2v26.2zM141.3 855.2h40.9H166c-13.8-0.8-24.7-12.2-24.7-26.2v26.2zM889.3 549.6h-40.9 16.2c13.8 0.8 24.7 12.2 24.7 26.2v-26.2zM809.6 346.9h-40.9 16.2c13.8 0.8 24.7 12.2 24.7 26.2v-26.2zM141.6 244h40.9-16.2c-13.8 0.8-24.7 12.2-24.7 26.2V244z" fill="#3E3836"/><path d="M906.1 468.1H232.3c-22.6 0-41 18.3-41 41 0 22.6 18.3 41 41 41h657v305.1h-748V244.1h287.3l52.7 81.4a40.98 40.98 0 0 0 36.1 21.5h291.9v63.4c0 22.6 18.3 41 41 41s41-18.3 41-41v-83.2c-3.2-34.7-32.3-61.8-67.8-61.8H769v-0.2H539.9L486 181.9l-0.6-0.9c-7.3-11.3-20-18.9-34.5-18.9H182.3v0.1h-54.5c-37.6 0-68.1 30.5-68.1 68.1v0.5h-0.1v643.6c2.4 32.8 28 59.1 60.5 62.6h787c33.1-1.5 60-26.6 64.3-58.9V529.7c-3.3-33.7-31.1-60.3-65.3-61.6z" fill="#3E3836"/></svg>
          </span>
          <span>产品设计说明</span>
        </a>
      </nav>

      <!-- 最近对话 -->
      <div class="section">
        <div class="section-header">
          <span class="section-title">最近对话</span>
          <span class="section-count">(3)</span>
        </div>
        <ul class="chat-list"></ul>
      </div>

      <!-- 底部装饰：静止态 left_bottom.jpg；hover 时由 JS 用 canvas 播放 APNG 队列（start→progress→end） -->
      <div class="left-footer" data-tooltip="点击打开【设置】菜单" data-tooltip-delay="0">
        <img class="lf-img" src="file=asset/left_bottom.jpg" alt="装饰" />
        <canvas class="lf-canvas" width="204" height="108"></canvas>
      </div>
    </div>

    <!-- 缩略态（窄条） -->
    <div class="collapsed-bar">
      <div class="collapsed-logo-wrap" id="expandLeftBtn" data-tooltip="展开侧边栏">
        <img src="file=asset/logo.jpg" class="collapsed-logo" alt="宠医助手" />
        <div class="expand-icon" aria-label="展开">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#6B5045" stroke-width="2">
            <polyline points="13 17 18 12 13 7" />
            <polyline points="6 17 11 12 6 7" />
          </svg>
        </div>
      </div>
      <button class="collapsed-tool" data-tooltip="新建任务">
        <span class="collapsed-plus">+</span>
      </button>
      <button class="collapsed-tool" data-tooltip="搜索">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#6F6763" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </button>
      <button class="collapsed-tool" id="collapsedSettingsBtn" data-tooltip="设置" aria-label="设置">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#6F6763" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </button>
    </div>
  </aside>

  <!-- 中间主区域 -->
  <main class="main-area" id="mainArea">
    <!-- 打开右侧按钮 -->
    <button class="icon-btn open-right-btn" id="openRightBtn" data-tooltip="打开右侧栏">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#6F6763" stroke-width="2">
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <line x1="15" y1="5" x2="15" y2="19" />
      </svg>
    </button>

    <div class="main-scroll">
      <div class="main-inner">

      <!-- Hero -->
      <section class="hero">
        <div class="hero-text">
          <h1 class="hero-title">
            你好，我是宠医助手
            <span class="paw-emoji">🐾</span>
          </h1>
          <p class="hero-subtitle">专注于猫传腹（FIP）的 AI 咨询与知识问答</p>
        </div>
        <div class="hero-image">
          <img class="hero-img" src="file=asset/middle.jpg" alt="宠医助手" />
          <video class="hero-video" muted loop playsinline preload="auto" src="/gradio_api/file=asset/middle_hello.mp4"></video>
          <!-- APNG 备选：如需切回，取消下一行注释并注释掉上面的 <video> 即可：<canvas class="hero-canvas"></canvas> -->
        </div>
      </section>

      <!-- 聊天交互区域（空态隐藏，发送后显示；置于 hero 之后：其长高只会把下方的输入区/卡片往下推，hero 保持顶部，向上移出） -->
      <section class="chat-area" id="chatArea"></section>

      <!-- 输入区 -->
      <div class="input-area">
        <div class="input-box">
          <div class="input-text-wrap">
            <div class="input-textarea" contenteditable="true" aria-label="输入问题"></div>
          </div>
          <div class="input-toolbar">
            <div class="model-select-wrap">
              <button class="input-tool model-btn" data-tooltip="选择模型">
                <span class="model-paw"><svg viewBox="0 0 1304 1024" width="14" height="14" aria-hidden="true"><path d="M82.59529938 450.3801144a150.60833431 128.0248712 90 1 0 256.0497433 4e-8 150.60833431 128.0248712 90 1 0-256.0497433-4e-8Z" fill="#B47B68"/><path d="M1074.58733465 734.21008403a123.50817892 150.6083343 12.07 1 0 62.98638385-294.55762892 123.50817892 150.6083343 12.07 1 0-62.98638385 294.55762892Z" fill="#B47B68"/><path d="M393.39047088 225.47997485a168.1299859 131.60707559 90 1 0 263.21415207 2e-8 168.1299859 131.60707559 90 1 0-263.21415207-2e-8Z" fill="#B47B68"/><path d="M864.14609382 436.84087636a131.60707559 168.1299859 6.71 1 0 39.28998639-333.95668374 131.60707559 168.1299859 6.71 1 0-39.28998639 333.95668373Z" fill="#B47B68"/><path d="M929.47515147 749.26056245c-9.42275492 142.66518562-147.18187788 219.21533615-310.17217958 208.39084944s-289.53556667-104.6626682-280.34643328-247.40572826 152.55518447-233.23265776 312.19690332-238.91746033c165.09289985 33.1743283 287.74446448 135.18927998 278.32170954 277.93233915z" fill="#B47B68"/></svg></span>
                <span class="model-label">宠医助手 · Pro</span>
                <svg class="caret" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#A99A90" stroke-width="2"><polyline points="6 9 12 15 18 9" /></svg>
              </button>
              <div class="model-popover hidden">
                <div class="model-option active" data-value="pro">宠医助手 · Pro</div>
                <div class="model-option disabled" data-value="max">宠医助手 · Max（暂未开发）</div>
              </div>
            </div>
            <div class="toolbar-spacer"></div>
            <button class="input-tool mic-btn" data-tooltip="语音输入" hidden>
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#6B5045" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="23" /><line x1="8" y1="23" x2="16" y2="23" /></svg>
            </button>
            <button class="send-btn" data-tooltip="发送">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#FFFFFF" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 快速开始 -->
      <section class="quick-start">
        <div class="quick-title">你可以从这里开始</div>

      <!-- 功能卡片 -->
      <section class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">
<svg viewBox="0 0 1024 1024" width="22" height="22" aria-hidden="true"><path d="M298.709333 298.666667c0-23.594667 19.072-42.666667 42.666667-42.666667h298.666667a42.666667 42.666667 0 0 1 0 85.333333H341.333333a42.666667 42.666667 0 0 1-42.666666-42.666666z m42.666667 128a42.666667 42.666667 0 1 0 0 85.333333h128a42.666667 42.666667 0 1 0 0-85.333333H341.333333z" fill="#8C6B5D" p-id="14580"></path><path d="M706.730667 57.728c-41.941333-4.394667-94.464-4.394667-160.298667-4.394667h-37.290667c-80.768 0-145.408 0-196.096 6.4-52.224 6.741333-96 20.821333-130.858666 53.76-35.328 33.408-50.773333 75.690667-57.941334 126.208-6.912 48.384-6.912 109.824-6.912 185.728v262.4c0 34.048 0 61.696 1.450667 84.309334 1.578667 23.210667 4.821333 43.861333 12.629333 63.701333a213.546667 213.546667 0 0 0 128.64 122.026667c36.608 12.842667 99.413333 12.842667 165.76 12.8 121.173333 0 193.066667 0.042667 252.117334-20.736 94.72-33.365333 170.325333-104.32 206.293333-195.456 12.032-30.378667 17.365333-63.018667 19.925333-102.101334 2.56-38.4 2.56-85.930667 2.56-146.432V395.733333c0-61.824 0-111.872-4.736-151.808-4.864-41.6-15.232-77.312-39.552-107.946666a213.589333 213.589333 0 0 0-44.16-41.728c-31.744-22.485333-68.48-32-111.530666-36.522667zM239.061333 174.208c16.768-15.786667 40.533333-26.112 84.48-31.658667 44.8-5.76 104.106667-5.76 188.501334-5.76h32.128c68.565333 0 116.864 0 153.984 3.84 36.394667 3.84 57.088 11.008 72.32 21.76 10.282667 7.296 19.370667 15.872 26.922666 25.472 10.88 13.781333 18.176 32.213333 22.058667 65.792 4.053333 34.56 4.096 79.658667 4.096 144.64v123.776c0 11.392 0 38.570667-11.946667 58.752-7.338667 12.416-16.810667 22.784-26.496 28.117334a109.781333 109.781333 0 0 1-52.693333 13.312l-44.330667-1.578667a191.829333 191.829333 0 0 0-53.418666 5.12 102.869333 102.869333 0 0 0-72.917334 72.874667c-4.181333 17.493333-5.930667 35.413333-5.12 53.418666l1.621334 44.416c0 19.882667-5.333333 37.333333-14.592 53.461334-5.418667 9.386667-14.805333 18.005333-27.818667 25.6-19.754667 11.52-43.306667 11.52-57.770667 11.648l-42.368 0.128c-78.293333 0-106.666667-0.64-128.213333-8.192A130.346667 130.346667 0 0 1 208.64 805.12c-3.285333-8.362667-5.674667-19.456-6.869333-38.485333-1.28-19.541333-1.28-44.373333-1.28-80.213334v-257.792c0-79.872 0.042667-135.296 5.973333-177.066666 5.76-40.362667 16.213333-61.781333 32.64-77.269334l-0.042667-0.085333z" fill="#8C6B5D" p-id="14581"></path></svg>
          </div>
          <div class="feature-text">
            <div class="feature-name">什么是猫传腹？</div>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
<svg viewBox="0 0 1024 1024" width="22" height="22" aria-hidden="true"><path d="M386.304 217.728C457.002667 95.274667 613.546667 53.333333 736 124.010667c122.453333 70.698667 164.394667 227.264 93.696 349.717333l-192 332.544C567.04 928.725333 410.453333 970.666667 288 899.989333c-122.453333-70.698667-164.394667-227.264-93.696-349.717333l192-332.544zM693.333333 197.930667a170.666667 170.666667 0 0 0-233.130666 62.464l-192 332.544a170.666667 170.666667 0 0 0 295.594666 170.666666l192-332.544A170.666667 170.666667 0 0 0 693.333333 197.930667z" fill="#8C6B5D" p-id="15695"></path><path d="M693.909333 666.282667l-406.464-234.666667 42.666667-73.898667 406.464 234.666667-42.666667 73.898667zM653.525333 224.213333l18.474667 10.666667a128 128 0 0 1 46.869333 174.848l-32 55.424-73.92-42.666667 32-55.424a42.666667 42.666667 0 0 0-15.616-58.282666l-18.474666-10.666667 42.666666-73.898667z" fill="#8C6B5D" p-id="15696"></path></svg>
          </div>
          <div class="feature-text">
            <div class="feature-name">传腹的治疗方法</div>
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
<svg viewBox="0 0 1024 1024" width="22" height="22" aria-hidden="true"><path d="M704 128C833.621333 128 938.666667 234.666667 938.666667 384c0 298.666667-320 469.333333-426.666667 533.333333-84.352-50.602667-302.208-167.978667-389.589333-362.624L42.666667 554.666667v-85.333334h51.626666A407.552 407.552 0 0 1 85.333333 384c0-149.333333 106.666667-256 234.666667-256C399.36 128 469.333333 170.666667 512 213.333333c42.666667-42.666667 112.64-85.333333 192-85.333333z m0 85.333333c-45.909333 0-95.573333 24.32-131.669333 60.330667L512 333.994667l-60.330667-60.330667C415.573333 237.653333 365.909333 213.333333 320 213.333333 237.226667 213.333333 170.666667 283.989333 170.666667 384c0 29.226667 3.84 57.685333 11.392 85.333333h92.458666L362.666667 322.389333l128 213.333134L530.517333 469.333333H725.333333v85.333334h-146.517333L490.666667 701.610667l-128-213.333134L322.816 554.666667H217.941333c33.706667 58.624 84.693333 113.834667 150.912 166.528 31.786667 25.301333 65.706667 48.896 103.296 72.533333 12.757333 8.064 25.386667 15.786667 39.850667 24.405333 14.464-8.618667 27.093333-16.341333 39.850667-24.362666a1141.418667 1141.418667 0 0 0 103.253333-72.576C782.293333 620.074667 853.333333 509.568 853.333333 384c0-100.693333-65.578667-170.666667-149.333333-170.666667z" fill="#8C6B5D" p-id="23497"></path></svg>
          </div>
          <div class="feature-text">
            <div class="feature-name">441安全吗？能治好吗？</div>
          </div>
          <div class="feature-tag">常问</div>
        </div>
      </section>

      </section>
      </div>

      <!-- 聊天态底部遮罩：置于 main-scroll 内部、main-inner 之后。
           sticky bottom:0 相对滚动容器可视区固定 → 不随内容滚动；
           滚动条属于 main-scroll、绘制在其内容之上 → 遮罩永远不会盖住滚动条 -->
      <div class="chat-mask" id="chatMask"></div>
    </div>

    <!-- 免责声明：始终固定在屏幕底部 -->
    <div class="disclaimer">内容由 AI 生成，仅供参考，不能代替兽医诊断&nbsp;&nbsp;|&nbsp;&nbsp;联系我&nbsp;潘页冰&nbsp;&nbsp;TEL/微信：13564037937</div>

  </main>

  <!-- 右侧边栏（默认隐藏；点击开始对话后自动打开） -->
  <aside class="right-sidebar hidden" id="rightSidebar">
    <div class="sidebar-resizer" id="sidebarResizer"></div>
    <div class="right-inner" data-sidebar-version="v2-timeline">
      <!-- 顶部 Header：标题 + 状态 + 输入摘要 -->
      <div class="right-header">
        <div class="right-header-row">
          <div class="right-title">
            <span class="title-star" aria-hidden="true">✦</span>
            <span>AI 分析过程</span>
          </div>
          <div class="right-actions">
            <button class="icon-btn fullscreen-btn" id="fullscreenRightBtn" data-tooltip="全屏">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#6F6763" stroke-width="2">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
              </svg>
            </button>
            <button class="icon-btn close-right-btn" id="closeRightBtn" data-tooltip="收起">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#6F6763" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>
        <div class="analysis-status" id="analysisStatus"></div>
        <div class="analysis-input" id="analysisInput"></div>
      </div>

      <!-- Timeline：固定步骤纵向列表 -->
      <div class="right-timeline" id="traceTimeline">
        <div class="trace-empty">发送问题后，这里会展示 AI 分析 Timeline</div>
      </div>

      <!-- Detail Panel：当前选中步骤详情（独立滚动） -->
      <div class="right-detail" id="traceDetail">
        <div class="detail-resizer" id="detailResizer"></div>
        <div class="detail-body" id="traceDetailBody">
          <div class="detail-empty">点击步骤查看详细内容</div>
        </div>
      </div>
    </div>
  </aside>
  <!-- 图数据库页面（iframe 隔离，懒加载） -->
  <iframe id="pageGraph" class="page-graph" hidden title="图数据库"></iframe>
  <!-- 文献库页面（空页面占位） -->
  <iframe id="pageDocs" class="page-docs" hidden title="文献库"></iframe>
  <!-- 产品设计说明页面（空页面占位） -->
  <iframe id="pageDesign" class="page-design" hidden title="产品设计说明"></iframe>
</div>
<!-- 设置功能：设置面板 / 通用 Modal / Toast 栈（顶层浮层，位于 app-shell 外部） -->
<div id="stSettings" class="st-settings" role="dialog" aria-label="设置" aria-hidden="true">
  <div class="st-settings__head">
    <div class="st-settings__title-group">
      <span class="st-settings__gear" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </span>
      <span class="st-settings__title">设置</span>
      <span class="st-settings__subtitle">SETTINGS</span>
    </div>
    <div class="st-settings__close" data-st-settings-close role="button" tabindex="0" aria-label="关闭">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </div>
  </div>
  <div class="st-divider st-divider--head"></div>
  <div class="st-settings__body">
    <div class="st-feedback-card" data-st-action="feedback" role="button" tabindex="0" aria-label="给我反馈">
      <video class="st-feedback-card__video" src="/gradio_api/file=asset/questionnaire.mp4" autoplay muted loop playsinline aria-hidden="true"></video>
      <div class="st-feedback-card__body">
        <div class="st-feedback-card__desc">期待您的意见与建议</div>
        <div class="st-feedback-card__cta">给"我"反馈 →</div>
      </div>
      <div class="st-feedback-card__art" aria-hidden="true">
        <svg viewBox="0 0 44 44" fill="none">
          <circle cx="22" cy="21" r="13" stroke="#C7A18E" stroke-width="1.6"/>
          <circle cx="22" cy="21" r="5.5" fill="#E7C9B8"/>
          <path d="M16.5 21.5l3.5 3.5 7.5-8" stroke="#C7A18E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <div class="st-divider"></div>
    <div class="st-group">
      <div class="st-group__label">系统配置</div>
      <div class="st-setting">
        <div class="st-setting__label">服务端桥接方案</div>
        <div class="st-bridge" id="stBridge">
          <button class="st-bridge__seg" data-st-bridge="networkx" type="button">NetworkX · 本地</button>
          <button class="st-bridge__seg" data-st-bridge="neo4j" type="button">Neo4j · 联网</button>
        </div>
      </div>
    </div>
    <div class="st-divider"></div>
    <div class="st-group">
      <div class="st-group__label">系统操作</div>
      <button class="st-item" data-st-action="clear">
        <span class="st-item__label">删除全部对话</span>
        <span class="st-item__arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg></span>
      </button>
      <button class="st-item" data-st-action="unwatermark">
        <span class="st-item__label">去水印</span>
        <span class="st-item__arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg></span>
      </button>
      <button class="st-item" data-st-action="logs">
        <span class="st-item__label">运行日志</span>
        <span class="st-item__arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg></span>
      </button>
    </div>
  </div>
</div>
<div id="stModal" class="st-modal" role="dialog" aria-modal="true" aria-hidden="true">
  <div class="st-modal__overlay" data-st-overlay></div>
  <div class="st-modal__box" id="stModalBox">
    <div class="st-modal__content" id="stModalContent"></div>
  </div>
</div>
<div id="stToastStack" class="st-toast-stack" aria-live="polite"></div>
<div id="styleDemoModal" class="style-demo-modal" aria-hidden="true">
  <div class="style-demo-modal__overlay" data-close></div>
  <div class="style-demo-modal__content">
    <div class="style-demo-modal__head">
      <span class="style-demo-modal__title">视觉设计 demo</span>
      <div role="button" tabindex="0" class="style-demo-modal__close" data-close aria-label="关闭">&times;</div>
    </div>
    <iframe class="style-demo-modal__frame" id="styleDemoFrame" sandbox="allow-scripts allow-same-origin"></iframe>
  </div>
</div>
<!-- 展开弹窗（顶层覆盖层，与 styleDemoModal 同构）：详情内容通过 iframe srcdoc 加载 -->
<div id="designExpandModal" class="design-expand-modal" aria-hidden="true">
  <div class="design-expand-modal__overlay" data-close></div>
  <div class="design-expand-modal__content">
    <div class="design-expand-modal__head">
      <span class="design-expand-modal__title"></span>
      <div role="button" tabindex="0" class="design-expand-modal__close" data-close aria-label="关闭">&times;</div>
    </div>
    <iframe class="design-expand-modal__frame" id="designExpandFrame" sandbox="allow-scripts allow-same-origin"></iframe>
  </div>
</div>
<!-- 图片放大灯箱（顶层覆盖层，z-index 高于弹窗，支持主文档与展开 iframe 图片） -->
<div id="imgLightbox" class="img-lightbox" aria-hidden="true">
  <div class="img-lightbox__overlay" data-close></div>
  <button type="button" class="img-lightbox__close" data-close aria-label="关闭">&times;</button>
  <img class="img-lightbox__img" alt="图片放大预览" />
</div>
"""

# Gradio 的 gr.HTML 中插入的 <script> 不会被执行，因此交互逻辑通过 Blocks 的 js 参数注入。
# 说明：页面标题由 gr.Blocks(title=...) 设置；favicon 由 launch(favicon_path=...) 提供
# （Gradio 6.x 的 favicon_path 是 launch() 的参数，不是 Blocks() 的），
# 因此 JS_CODE 不再需要手写 title/favicon 注入。
JS_CODE = """
window.__GRAPH_HTML__=__GRAPH_HTML_JSON__;
window.__DOCS_HTML__=__DOCS_HTML_JSON__;
window.__DESIGN_HTML__=__DESIGN_HTML_JSON__;
window.__STYLE_DEMO_HTML__=__STYLE_DEMO_HTML_JSON__;

/* ====== 访客标识与飞书行为日志 ====== */
/* 访客标识：每次页面加载生成，刷新后重建（会话级，非持久化） */
function genVisitorId() {
  var d = new Date();
  function p(n) { return (n < 10 ? '0' : '') + n; }
  var date = '' + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate());
  var time = '' + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
  var rand = '';
  for (var i = 0; i < 4; i++) { rand += Math.floor(Math.random() * 10); }
  return 'visitor_' + date + '_' + time + '_' + rand;
}
var VISITOR_ID = genVisitorId();
/* 行为类型常量（与 core.logging.feishu_logger 的 BEHAVIOR_* 对齐） */
var BEHAVIOR_PAGE_VIEW = 'page_view';
var BEHAVIOR_QUESTION = 'question';
var BEHAVIOR_FEEDBACK = 'feedback';

/* 行为日志：统一经 server.log_behavior / log_feedback 异步写入飞书，失败静默 */
function logBehavior(type, value) {
  try {
    if (server && server.log_behavior) {
      server.log_behavior({
        user_id: VISITOR_ID,
        behavior_type: type,
        behavior_value: value || '',
        user_agent: navigator.userAgent || ''
      }).catch(function () {});
    }
  } catch (e) {}
}
function logFeedback(fb) {
  try {
    if (server && server.log_feedback) {
      fb.user_id = VISITOR_ID;
      return server.log_feedback(fb).catch(function () {});
    }
  } catch (e) {}
  return Promise.resolve();
}
/* 页面访问日志：server 就绪前重试，确保 page_view 不丢 */
function logPageView() {
  var tries = 0;
  function attempt() {
    if (server && server.log_behavior) {
      logBehavior(BEHAVIOR_PAGE_VIEW, '主页面');
      return;
    }
    if (tries++ < 20) setTimeout(attempt, 300);
  }
  attempt();
}

/* ====== 全局自定义 tooltip（替代原生 title 黑底白字） ====== */
(function(){
  var tip = document.createElement('div');
  tip.id = 'app-tooltip';
  tip.className = 'app-tooltip';
  document.body.appendChild(tip);
  var timer = null;
  var currentTarget = null;
  function hide() {
    currentTarget = null;
    clearTimeout(timer);
    tip.classList.remove('app-tooltip--show');
    tip.classList.remove('app-tooltip--bubble');
  }
  function position(el) {
    var rect = el.getBoundingClientRect();
    var tipRect = tip.getBoundingClientRect();
    var pad = 6;
    var top = rect.top - tipRect.height - pad;
    var left = rect.left + rect.width/2 - tipRect.width/2;
    if (left < 4) left = 4;
    if (left + tipRect.width > window.innerWidth - 4) left = window.innerWidth - tipRect.width - 4;
    if (top < 4) top = rect.bottom + pad;
    tip.style.top = top + 'px';
    tip.style.left = left + 'px';
  }
  function show(el) {
    if (window.__fipGuideActive) return; /* 反馈引导显示时，压掉左下角 hover 气泡避免重叠 */
    var text = el.getAttribute('data-tooltip');
    if (!text) return;
    currentTarget = el;
    tip.textContent = text;
    tip.classList.toggle('app-tooltip--bubble', !!el.closest('.left-footer'));
    tip.classList.add('app-tooltip--show');
    position(el);
  }
  document.addEventListener('mouseover', function(e){
    var el = e.target.closest && e.target.closest('[data-tooltip]');
    if (!el) return;
    clearTimeout(timer);
    var d = parseInt(el.getAttribute('data-tooltip-delay'), 10);
    if (isNaN(d)) d = 400;
    timer = setTimeout(function(){ show(el); }, d);
  });
  document.addEventListener('mouseout', function(e){
    var el = e.target.closest && e.target.closest('[data-tooltip]');
    if (!el) return;
    hide();
  });
  window.addEventListener('scroll', function(){ if(currentTarget) position(currentTarget); }, true);
  window.addEventListener('resize', function(){ if(currentTarget) position(currentTarget); });
})();

(() => {
  /* ====== 导航路由：页面切换（图数据库 / 文献库 / 产品设计说明） ====== */
  (function(){
    var appShell=document.getElementById('appShell');
    var pageGraph=document.getElementById('pageGraph');
    var pageDocs=document.getElementById('pageDocs');
    var pageDesign=document.getElementById('pageDesign');
    if(!appShell)return;
    /* 事件委托到 document：避免 Gradio 重渲染或 iframe srcdoc 加载导致
       nav-item 监听丢失（一次性 forEach 绑定的脆弱性） */
    document.addEventListener('click',function(e){
      var item=e.target&&e.target.closest&&e.target.closest('.nav-menu .nav-item');
      if(!item)return;
      e.preventDefault();
      var pageDesign=document.getElementById('pageDesign');
      if(pageDesign){ pageDesign.classList.remove('is-modal'); }
      document.body.style.overflow = '';
      var text=item.textContent;
      /* 记录侧边栏页面访问行为（最小方案：点击即记，复用已验证的 fire-and-forget 日志；
         子页面为纯前端 iframe 切换，无 Python 调用，故在此直接记 page_view） */
      logBehavior(BEHAVIOR_PAGE_VIEW, text.trim());
      /* 每次重新查询 nav-items，防止 DOM 变化导致引用过期 */
      var navItems=document.querySelectorAll('.nav-menu .nav-item');
      navItems.forEach(function(n){n.classList.remove('active');});
      item.classList.add('active');
      /* 切换页面导航时，取消左侧最近对话的高亮 */
      document.querySelectorAll('.chat-item.active').forEach(function(c){c.classList.remove('active');});
      if(text.indexOf('图数据库')>=0){
        appShell.classList.add('mode-graph');
        appShell.classList.remove('mode-docs','mode-design');
        if(!pageGraph.dataset.loaded){
          pageGraph.srcdoc=window.__GRAPH_HTML__;
          pageGraph.dataset.loaded='1';
        }
      }else if(text.indexOf('文献库')>=0){
        appShell.classList.add('mode-docs');
        appShell.classList.remove('mode-graph','mode-design');
        if(!pageDocs.dataset.loaded){
          pageDocs.srcdoc=window.__DOCS_HTML__;
          pageDocs.dataset.loaded='1';
        }
      }else if(text.indexOf('产品设计说明')>=0){
        appShell.classList.add('mode-design');
        appShell.classList.remove('mode-graph','mode-docs');
        if(!pageDesign.dataset.loaded){
          pageDesign.srcdoc=window.__DESIGN_HTML__;
          pageDesign.dataset.loaded='1';
        }
      }else{
        /* 其他导航项：回到首页 */
        appShell.classList.remove('mode-graph','mode-docs','mode-design');
      }
      /* 切换到非图数据库页面时，无动画重置图谱页内的搜索栏
         （iframe 仍存活，状态需清；设置面板不改 mode 类，不受影响） */
      if(text.indexOf('图数据库')<0){
        try{ if(pageGraph.contentWindow && pageGraph.contentWindow.resetNodeSearch) pageGraph.contentWindow.resetNodeSearch(); }catch(e){}
      }
    });
  })();

  /* ====== 产品设计说明 展开弹窗（顶层覆盖层，与 demo 同构；监听 design.html 内详情消息） ====== */
  (function(){
    var modal = document.getElementById('designExpandModal');
    if(!modal) return;
    var frame = document.getElementById('designExpandFrame');
    var contentEl = modal.querySelector('.design-expand-modal__content');
    var titleEl = modal.querySelector('.design-expand-modal__title');
    var overlay = modal.querySelector('.design-expand-modal__overlay');
    var closeBtn = modal.querySelector('.design-expand-modal__close');
    function openExpand(data){
      modal.classList.remove('is-closing');
      if(titleEl && data.title != null) titleEl.textContent = data.title;
      if(frame && data.srcdoc) frame.srcdoc = data.srcdoc;
      if(contentEl && data.width) contentEl.style.width = data.width + 'px';
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden','false');
      document.body.classList.add('design-expand-open');
      document.body.style.overflow = 'hidden';
    }
    function closeExpand(){
      if(!modal.classList.contains('is-open')) return;
      modal.classList.remove('is-open');
      modal.classList.add('is-closing');
      modal.setAttribute('aria-hidden','true');
      document.body.classList.remove('design-expand-open');
      document.body.style.overflow = '';
      setTimeout(function(){
        modal.classList.remove('is-closing');
        if(frame){ frame.srcdoc = ''; }
      }, 320);
    }
    window.addEventListener('message', function(e){
      if(!e.data || e.data.type !== 'design-expand') return;
      if(e.data.open){ openExpand(e.data); } else { closeExpand(); }
    });
    if(overlay) overlay.addEventListener('click', closeExpand);
    if(closeBtn) closeBtn.addEventListener('click', closeExpand);
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape'){ var lb=document.getElementById('imgLightbox'); if(lb && lb.classList.contains('is-open')) return; if(modal.classList.contains('is-open')) closeExpand(); } });
  })();
  /* ====== 图片放大灯箱（顶层覆盖层，支持主文档与展开 iframe 图片；z-index 高于弹窗） ====== */
  (function(){
    var lb = document.getElementById('imgLightbox');
    if(!lb) return;
    var imgEl = lb.querySelector('.img-lightbox__img');
    var overlay = lb.querySelector('.img-lightbox__overlay');
    var closeBtn = lb.querySelector('.img-lightbox__close');
    function isExpandOpen(){
      var em = document.getElementById('designExpandModal');
      return !!(em && em.classList.contains('is-open'));
    }
    function openZoom(src){
      if(!src) return;
      imgEl.src = src;
      lb.classList.add('is-open');
      lb.setAttribute('aria-hidden','false');
      if(!isExpandOpen()) document.body.style.overflow = 'hidden';
    }
    function closeZoom(){
      if(!lb.classList.contains('is-open')) return;
      lb.classList.remove('is-open');
      lb.setAttribute('aria-hidden','true');
      imgEl.src = '';
      if(!isExpandOpen()) document.body.style.overflow = '';
    }
    window.addEventListener('message', function(e){
      if(!e.data || e.data.type !== 'img-zoom') return;
      openZoom(e.data.src);
    });
    if(overlay) overlay.addEventListener('click', closeZoom);
    if(closeBtn) closeBtn.addEventListener('click', closeZoom);
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && lb.classList.contains('is-open')) closeZoom();
    });
  })();

  /* ====== Module 04 视觉设计 demo 弹窗（顶层模态框，监听 design.html 内按钮消息） ====== */
  (function(){
    var modal = document.getElementById('styleDemoModal');
    if(!modal) return;
    var frame = document.getElementById('styleDemoFrame');
    var overlay = modal.querySelector('.style-demo-modal__overlay');
    var closeBtn = modal.querySelector('.style-demo-modal__close');
    function injectScrollbar(){
      try{
        var fd = frame.contentWindow.document;
        if(!fd.getElementById('demoScrollbarStyle')){
          var st = fd.createElement('style');
          st.id = 'demoScrollbarStyle';
          st.textContent = '::-webkit-scrollbar{width:8px;height:8px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:rgba(111,103,99,.2);border-radius:4px;}::-webkit-scrollbar-thumb:hover{background:#6F6763;}*{scrollbar-width:thin;scrollbar-color:rgba(111,103,99,.2) transparent;}';
          fd.head.appendChild(st);
        }
      }catch(err){}
    }
    function openDemo(){
      modal.classList.remove('is-closing');
      if(frame && window.__STYLE_DEMO_HTML__){
        frame.onload = injectScrollbar;
        frame.srcdoc = window.__STYLE_DEMO_HTML__;
      }
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden','false');
      document.body.classList.add('style-demo-open');
      document.body.style.overflow = 'hidden';
    }
    function closeDemo(){
      if(!modal.classList.contains('is-open')) return;
      modal.classList.remove('is-open');
      modal.classList.add('is-closing');
      modal.setAttribute('aria-hidden','true');
      document.body.classList.remove('style-demo-open');
      document.body.style.overflow = '';
      if(frame){ frame.onload = null; }
      setTimeout(function(){
        modal.classList.remove('is-closing');
        if(frame){ frame.srcdoc = ''; }
      }, 320);
    }
    window.addEventListener('message', function(e){
      if(!e.data || e.data.type !== 'style-demo-modal') return;
      if(e.data.open){ openDemo(); } else { closeDemo(); }
    });
    if(overlay) overlay.addEventListener('click', closeDemo);
    if(closeBtn) closeBtn.addEventListener('click', closeDemo);
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape' && modal.classList.contains('is-open')) closeDemo(); });
  })();

  function bindShell() {
    const left = document.getElementById('leftSidebar');
    const right = document.getElementById('rightSidebar');
    const openRight = document.getElementById('openRightBtn');
    const closeRight = document.getElementById('closeRightBtn');
    const fsRight = document.getElementById('fullscreenRightBtn');
    const collapseLeft = document.getElementById('collapseLeftBtn');
    const expandLeft = document.getElementById('expandLeftBtn');
    if (!left || !right) return;

    function openRightPanel() {
      right.classList.remove('hidden');
      right.classList.remove('fullscreen');
      if (openRight) openRight.style.display = 'none';
    }
    function closeRightPanel() {
      right.classList.add('hidden');
      right.classList.remove('fullscreen');
      if (openRight) openRight.style.display = 'flex';
    }
    function toggleRightFullscreen() {
      right.classList.toggle('fullscreen');
      right.classList.remove('hidden');
    }
    function collapseLeftPanel() {
      left.classList.add('collapsed');
    }
    function expandLeftPanel() {
      left.classList.remove('collapsed');
    }

    if (openRight) openRight.addEventListener('click', openRightPanel);
    if (closeRight) closeRight.addEventListener('click', closeRightPanel);
    if (fsRight) fsRight.addEventListener('click', toggleRightFullscreen);
    if (collapseLeft) collapseLeft.addEventListener('click', collapseLeftPanel);
    if (expandLeft) expandLeft.addEventListener('click', expandLeftPanel);

    document.addEventListener('click', function (e) {
      if (window.innerWidth > 1100) return;
      if (!left.contains(e.target)) {
        left.classList.add('collapsed');
      }
    });

    bindChat();
    logPageView();
  }

  /* 详情区向上展开 / 向下收起：展开时隐藏 Timeline，让详情填满 Header 以下区域 */
  function setDetailExpanded(expanded) {
    const sidebar = document.getElementById('rightSidebar');
    const detail = document.getElementById('traceDetail');
    if (!sidebar) return;
    sidebar.classList.toggle('detail-expanded', expanded);
    if (detail) {
      if (expanded) {
        detail.dataset.flexBackup = detail.style.flex || '';
        detail.style.flex = '';
      } else if (detail.dataset.flexBackup) {
        detail.style.flex = detail.dataset.flexBackup;
      }
    }
    document.querySelectorAll('.detail-expand-btn').forEach(function (b) {
      b.dataset.tooltip = expanded ? '向下收起' : '向上展开';
    });
  }

  /* 展开/收起按钮（纯 SVG，图标由 CSS 按 sidebar 状态切换） */
  function buildExpandBtn() {
    const btn = document.createElement('button');
    btn.className = 'detail-expand-btn';
    btn.type = 'button';
    btn.dataset.tooltip = '向上展开';
    btn.innerHTML =
      '<svg class="icon-up" viewBox="0 0 1024 1024" width="18" height="18"><path d="M838.116 732.779 877.7 693.195 511.979 327.549 146.3 693.195 185.883 732.779 512.003 406.652Z" fill="#4a3a2d"/></svg>' +
      '<svg class="icon-down" viewBox="0 0 1024 1024" width="18" height="18"><path d="M185.884 327.55 146.3 367.133 512.021 732.779 877.7 367.133 838.117 327.55 511.997 653.676Z" fill="#4a3a2d"/></svg>';
    btn.addEventListener('click', function () {
      const sidebar = document.getElementById('rightSidebar');
      if (!sidebar) return;
      setDetailExpanded(!sidebar.classList.contains('detail-expanded'));
    });
    return btn;
  }

  /* 侧边栏水平拖动调整宽度（200~600px） */
  function initSidebarResizer() {
    const sidebar = document.getElementById('rightSidebar');
    const resizer = document.getElementById('sidebarResizer');
    if (!sidebar || !resizer) return;

    let startX, startWidth, onMove, onUp;

    resizer.addEventListener('mousedown', function (e) {
      if (sidebar.classList.contains('hidden') || sidebar.classList.contains('fullscreen')) return;
      startX = e.clientX;
      startWidth = sidebar.getBoundingClientRect().width;
      document.body.style.userSelect = 'none';
      document.addEventListener('mousemove', onMove = function (ev) {
        const delta = startX - ev.clientX;
        const w = Math.min(800, Math.max(200, startWidth + delta));
        sidebar.style.width = w + 'px';
        sidebar.style.flex = '0 0 ' + w + 'px';
      });
      document.addEventListener('mouseup', onUp = function () {
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      });
    });
  }

  /* Detail 区垂直拖动调整高度（侧边栏高度的 1/5 ~ 4/5） */
  function initDetailResizer() {
    const sidebar = document.getElementById('rightSidebar');
    const detail = document.getElementById('traceDetail');
    const resizer = document.getElementById('detailResizer');
    if (!sidebar || !detail || !resizer) return;

    let startY, startHeight, sidebarHeight, onMove, onUp;

    resizer.addEventListener('mousedown', function (e) {
      if (sidebar.classList.contains('detail-expanded')) return;
      startY = e.clientY;
      startHeight = detail.getBoundingClientRect().height;
      sidebarHeight = sidebar.getBoundingClientRect().height;
      document.body.style.userSelect = 'none';
      document.addEventListener('mousemove', onMove = function (ev) {
        const delta = startY - ev.clientY;
        const minH = sidebarHeight * 0.2;
        const maxH = sidebarHeight * 0.8;
        const h = Math.min(maxH, Math.max(minH, startHeight + delta));
        detail.style.flex = '0 0 ' + h + 'px';
      });
      document.addEventListener('mouseup', onUp = function () {
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      });
    });

    window.addEventListener('resize', function () {
      if (sidebar.classList.contains('detail-expanded')) return;
      if (!detail.style.flex) return;
      const sh = sidebar.getBoundingClientRect().height;
      const currentH = detail.getBoundingClientRect().height;
      const newH = Math.min(sh * 0.8, Math.max(sh * 0.2, currentH));
      if (Math.abs(newH - currentH) > 1) detail.style.flex = '0 0 ' + newH + 'px';
    });
  }

  function bindChat() {
    const inner = document.querySelector('.main-inner');
    const chatArea = document.getElementById('chatArea');
    const textarea = document.querySelector('.input-textarea');
    const sendBtn = document.querySelector('.send-btn');
    const chatList = document.querySelector('.chat-list');
    const sectionCount = document.querySelector('.section-count');
    /* 「最近对话」列表项的默认图标 SVG（恒用兜底常量，不再依赖任何会被清空的 DOM）。
       避免「清除站点数据（Cookie）→ localStorage 清空 → 图标丢失」的问题。 */
    const DEFAULT_CHAT_ICO = (chatList && chatList.querySelector('.chat-ico'))
      ? chatList.querySelector('.chat-ico').innerHTML
      : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#8C6B5D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7a8.5 8.5 0 0 1-.9-3.8A8.38 8.38 0 0 1 12.5 3 8.38 8.38 0 0 1 21 11.5z"/></svg>';
    const chatMask = document.getElementById('chatMask');
    const rightPanel = document.getElementById('rightSidebar');
    const openRightBtn = document.getElementById('openRightBtn');
    if (!inner || !chatArea || !textarea || !sendBtn) return;

    /* 底部遮罩高度与输入区同步：遮罩需覆盖输入区（bottom:44px）及其下方。
       chat-area 沉底后其底部 = main-inner 底部 = 遮罩顶部（遮罩紧跟 main-inner 之后），
       故 chat-area 底部留白固定 20px，最后一条消息停在输入区上方约 20px。 */
    function syncChatMask() {
      if (!chatMask) return;
      const ia = document.querySelector('.input-area');
      if (!ia) return;
      const h = 44 + ia.offsetHeight;
      chatMask.style.height = h + 'px';
      chatArea.style.paddingBottom = '20px';
    }
    if (window.ResizeObserver) {
      const ia = document.querySelector('.input-area');
      if (ia) new ResizeObserver(syncChatMask).observe(ia);
    }
    if (textarea) textarea.addEventListener('input', syncChatMask);

    /* 发送按钮状态：无文字输入时禁用（浅色 #FAF3EC），有文字后恢复 */
    function updateSendState() {
      sendBtn.disabled = !((textarea.innerText || '').trim().length > 0);
    }
    textarea.addEventListener('input', updateSendState);
    updateSendState();

    /* 发送按钮两种态：默认纸飞机（发送）/ 处理中方块停止（中断）。
       外框与底色不变（#B37560），仅替换中间图标；处理中态始终可点。 */
    const SEND_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#FFFFFF" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>';
    const STOP_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#FFFFFF"><rect x="5" y="5" width="14" height="14" rx="3" /></svg>';
    /* mode: 'idle' 默认发送态（按有无文字决定灰/彩色）；'processing' 处理中→停止按钮（可点） */
    function setSendMode(mode) {
      if (mode === 'processing') {
        sendBtn.innerHTML = STOP_ICON;
        sendBtn.dataset.tooltip = '中断';
        sendBtn.classList.add('sending');
        sendBtn.disabled = false;
      } else {
        sendBtn.innerHTML = SEND_ICON;
        sendBtn.dataset.tooltip = '发送';
        sendBtn.classList.remove('sending');
        updateSendState();
      }
    }

    /* 会话数据（内存态；聊天历史经 saveHistory 持久化到 localStorage） */
    let conversations = [];
    let currentConvoId = null;

    /* ===== 聊天历史持久化（浏览器 localStorage，刷新后仍保留） ===== */
    /* system_default 默认对话种子：由 collect_seed.py 采集、Python 启动期以 base64 注入，避免破坏 JS_CODE 三引号字符串或特殊字符 */
    const SEED_CONVERSATIONS = __SEED_PLACEHOLDER__;

    const STORAGE_KEY = 'fip_chat_history_v2';  /* v2：time 升级为完整日期时间；旧 key 自动失效，实现上线前数据清理 */

    /* 保存全部会话到 localStorage（会话列表 + 当前会话 id） */
    /* 保存全部会话到 localStorage：始终写入（含空数组）。
       这样「清空对话」后的空状态可持久化；只有 key 缺失（清 cookie）时才重新播种默认对话。 */
    function saveHistory() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ conversations: conversations, currentConvoId: currentConvoId }));
      } catch (e) { /* 隐私模式 / 存储不可用时静默失败 */ }
    }

    /* 进入聊天态：切换布局（hero 上移、输入区固定底部、自动开右侧栏），
       供「首次发送」与「恢复历史」两处复用 */
    function enterChatMode() {
      if (inner.classList.contains('chat-mode')) return;
      inner.classList.add('chat-mode');
      /* 先量取布局偏移（此刻 input-area 仍在 inner 文档流中，布局为空态） */
      const ir = inner.getBoundingClientRect();
      const hr = inner.querySelector('.hero').getBoundingClientRect();
      /* 再移动输入区：把 input-area 移到 main-area（position:relative）下，
         containing block 变为 main-area，彻底脱离滚动流，固定在中间区域底部 */
      const ma = document.querySelector('.main-area');
      const ia = document.querySelector('.input-area');
      if (ma && ia) {
        ma.appendChild(ia);
        ia.classList.add('chat-fixed');
      }
      if (chatMask) chatMask.classList.add('show');
      /* 自动打开右侧边栏（与手动打开行为一致） */
      if (rightPanel) {
        rightPanel.classList.remove('hidden');
        if (openRightBtn) openRightBtn.style.display = 'none';
      }
      /* 布局切换：center → flex-start，用 padding-top 补偿消除跳变 */
      inner.style.transition = 'none';
      inner.style.justifyContent = 'flex-start';
      inner.style.paddingTop = (hr.top - ir.top) + 'px';
      chatArea.offsetHeight;
      inner.style.transition = '';
      requestAnimationFrame(function () {
        inner.style.paddingTop = '';
      });
    }

    /* 渲染某个会话的全部消息到聊天区（user 直接气泡，bot 填文本不打字机） */
    function renderConvo(convo) {
      chatArea.innerHTML = '';
      clearTraceSelection();
      (convo.msgs || []).forEach(function (m, idx) {
        if (m.role === 'user') {
          addUserMsg(m.text);
        } else if (m.role === 'bot' && m.text) {
          const row = addBotMsg();
          row.querySelector('.bubble-body').textContent = m.text;
          addIntentChip(row, m.intent);
          /* 历史 bot 消息挂「查看执行轨迹」图标（无 trace 字段时点击显示占位，兼容旧数据） */
          attachTraceIcon(row, m.trace || null);
          row.dataset.mid = String(idx);
        }
      });
      scrollChatBottom();
      /* 恢复待澄清状态：若该会话此前触发了澄清且未解决，重新渲染引导气泡 + 追问面板 */
      if (convo.pendingClarify && convo.pendingClarify.options && convo.pendingClarify.options.length) {
        addClarifyMsg(convo.pendingClarify.options);
      }
    }

    /* 切换当前会话：清空聊天区并渲染目标会话，更新高亮。
       点击当前会话也重渲染（作为「跳转」反馈），不做防抖早退。 */
    function switchConvo(cid) {
      let target = null;
      for (var i = 0; i < conversations.length; i++) {
        if (conversations[i].id === cid) { target = conversations[i]; break; }
      }
      if (!target) return;
      /* 切换对话时清除可能残留的追问/澄清面板（它挂在 input-box 上，不随消息区重建） */
      hideClarifyPanel();
      currentConvoId = cid;
      enterChatMode();
      renderConvo(target);
      updateActiveConvo();
      /* 右侧栏回显该会话最后一次回答的分析过程；无轨迹则空态 */
      if (target.lastTrace) {
        renderTrace(target.lastTrace, true);
      } else {
        resetTracePanel();
      }
    }

    /* 高亮「最近对话」列表中当前会话条目 */
    function updateActiveConvo() {
      if (!chatList) return;
      chatList.querySelectorAll('.chat-item').forEach(function (li) {
        if (li.dataset.cid === currentConvoId) {
          li.classList.add('active');
        } else {
          li.classList.remove('active');
        }
      });
    }

    /* 页面加载时恢复历史：读 localStorage，重建会话列表 + 渲染当前会话 */
    function loadHistory() {
      let raw = null;
      try { raw = localStorage.getItem(STORAGE_KEY); } catch (e) { raw = null; }

      /* 分支一：key 完全缺失（首次打开 / 清 cookie）→ 播种 system_default 默认对话 */
      if (raw === null) {
        conversations = [];
        chatList.innerHTML = '';
        (SEED_CONVERSATIONS || []).forEach(function (c) {
          var copy = JSON.parse(JSON.stringify(c));
          conversations.push(copy);
          addConversationItem(copy);   /* insertBefore(firstChild)：按数组顺序 1→2→3 遍历，组1 落在最下方 */
        });
        if (!conversations.length) {
          var empty0 = document.createElement('li');
          empty0.className = 'chat-empty';
          empty0.textContent = '（无）';
          chatList.appendChild(empty0);
        }
        currentConvoId = null;
        saveHistory();              /* 持久化默认对话，避免每次刷新重复播种 */
        updateConvoCount();
        return;
      }

      /* 分支二：key 存在但为空数组（用户清空过）→ 显示「（无）」，不重新播种 */
      let saved = null;
      try { saved = JSON.parse(raw); } catch (e) { saved = null; }
      if (!saved || !Array.isArray(saved.conversations) || !saved.conversations.length) {
        /* 清空后：清空列表并展示灰色「（无）」占位 */
        conversations = [];
        chatList.innerHTML = '';
        const empty = document.createElement('li');
        empty.className = 'chat-empty';
        empty.textContent = '（无）';
        chatList.appendChild(empty);
        updateConvoCount();
        return;
      }

      /* 分支三：有数据 → 正常重建 */
      conversations = saved.conversations;
      /* 默认进入「新任务对话」空态首页，不自动恢复到最后一次会话 */
      currentConvoId = null;

      /* 清空静态占位项（避免与真实历史重复），随后重建列表 */
      chatList.innerHTML = '';
      /* 重建「最近对话」列表（倒序插入，保持最新在前） */
      for (var i = conversations.length - 1; i >= 0; i--) {
        addConversationItem(conversations[i]);
      }
      updateConvoCount();
    }

    function nowTime() {
      const d = new Date();
      const p = (n) => (n < 10 ? '0' : '') + n;
      return (
        d.getFullYear() + '-' +
        p(d.getMonth() + 1) + '-' +
        p(d.getDate()) + ' ' +
        p(d.getHours()) + ':' +
        p(d.getMinutes())
      );
    }

    /* 相对时间格式化：今天→HH:MM；昨天→昨天；2~31天→X天前；>31天→X月前（整月近似 d/30）。
       仅接受 YYYY-MM-DD HH:MM；格式非法（理论不会发生，因已升 STORAGE_KEY 版本）返回空串避免报错。 */
    function formatConvoTime(raw) {
      if (!raw) return '';
      const m = /^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2})$/.exec(raw);
      if (!m) return '';
      const y = +m[1], mo = +m[2], d = +m[3], hh = m[4], mm = m[5];
      const today = new Date(); today.setHours(0, 0, 0, 0);
      const convoDate = new Date(y, mo - 1, d); convoDate.setHours(0, 0, 0, 0);
      const diffDays = Math.round((today - convoDate) / 86400000);
      if (diffDays <= 0) return hh + ':' + mm;   /* 今天或将来 */
      if (diffDays === 1) return '昨天';
      if (diffDays <= 31) return diffDays + '天前';
      return Math.floor(diffDays / 30) + '月前';
    }

    function updateConvoCount() {
      if (sectionCount && chatList) {
        const n = chatList.querySelectorAll('.chat-item').length;
        sectionCount.textContent = '(' + n + ')';
      }
    }

    /* 创建「最近对话」列表条目（含点击切换绑定），插入列表最前 */
    function addConversationItem(convo) {
      /* 生成首个对话时移除「（无）」占位符（它曾是 firstChild，会被新条目挤到后面残留） */
      const empty = chatList.querySelector('.chat-empty');
      if (empty) empty.remove();
      /* 图标始终使用启动捕获的默认 SVG，不再依赖可能已被清空的 DOM 克隆 */
      const iconHTML = DEFAULT_CHAT_ICO;
      const li = document.createElement('li');
      li.className = 'chat-item chat-item-new';
      li.dataset.cid = convo.id;
      li.innerHTML =
        '<span class="chat-ico">' + iconHTML + '</span>' +
        '<span class="chat-title"></span>' +
        '<span class="chat-time"></span>';
      li.querySelector('.chat-title').textContent = convo.title;
      li.querySelector('.chat-time').textContent = formatConvoTime(convo.time);
      chatList.insertBefore(li, chatList.firstChild);
      return li;
    }

    /* 新建会话：标题 = 首条消息，置顶插入「最近对话」，历史条目顺次下推 */
    function addConversation(title) {
      const convo = {
        id: 'c' + Date.now(),
        title: title,
        time: nowTime(),
        msgs: [],
        contextEntities: [],
        kind: 'user_creat'
      };
      conversations.unshift(convo);
      currentConvoId = convo.id;
      addConversationItem(convo);
      updateConvoCount();
      updateActiveConvo();
      return convo;
    }

    function getCurrentConvo() {
      for (var i = 0; i < conversations.length; i++) {
        if (conversations[i].id === currentConvoId) return conversations[i];
      }
      return null;
    }

    /* 点击聊天区交互逻辑：
       - 点 bot 气泡（任意位置，含图标）：右侧切换为该轮历史轨迹并高亮；若该轮无轨迹则恢复最新。
       - 点用户气泡或聊天区空白：清除高亮并恢复最新轨迹。 */
    chatArea.addEventListener('click', function (e) {
      const msg = e.target.closest('.message.message-bot');
      if (msg) {
        if (msg._traceData) {
          selectTrace(msg, msg._traceData);
        } else {
          clearTraceSelection();
          const c = getCurrentConvo();
          renderTrace(c && c.lastTrace ? c.lastTrace : null, true);
        }
        return;
      }
      if (!currentTraceMsgEl) return;   // 当前已是最新轨迹，无需处理
      clearTraceSelection();
      const c = getCurrentConvo();
      renderTrace(c && c.lastTrace ? c.lastTrace : null, true);
    });

    /* 新建任务：结束当前会话，回到空态首页。之后的首次发送会新建会话条目，
       这样同一页面内可积累多个会话（「最近对话」条目变多后支持内部滚动） */
    function resetChat() {
      currentConvoId = null;
      updateActiveConvo();
      chatArea.innerHTML = '';
      chatArea.classList.remove('msg-in');
      inner.classList.remove('chat-mode');
      inner.style.transition = '';
      inner.style.justifyContent = '';
      inner.style.paddingTop = '';
      if (textarea) textarea.innerText = '';
      updateSendState();
      /* 复位遮罩/留白为 CSS 默认值（chat-mode 移除后遮罩自动隐藏） */
      if (chatMask) {
        chatMask.style.height = '';
        chatMask.classList.remove('show');
      }
      chatArea.style.paddingBottom = '';
      /* 输入区移回 main-inner（hero 与 quick-start 之间），恢复空态文档流布局 */
      const ia = document.querySelector('.input-area');
      if (ia && ia.parentElement !== inner) {
        ia.classList.remove('chat-fixed');
        const qs = inner.querySelector('.quick-start');
        if (qs) inner.insertBefore(ia, qs);
        else inner.appendChild(ia);
      }
      const sc = document.querySelector('.main-scroll');
      if (sc) sc.scrollTop = 0;
      /* 收起右侧边栏，回到空态默认隐藏 */
      if (rightPanel) {
        rightPanel.classList.add('hidden');
        if (openRightBtn) openRightBtn.style.display = '';
      }
      /* 右侧栏回到初始空态 */
      resetTracePanel();
      /* 清理可能残留的追问面板 */
      hideClarifyPanel();
    }

    /* 「删除全部对话」真实实现：必须在 bindChat 作用域内执行，以访问内存态 conversations /
       currentConvoId 与本地函数（updateConvoCount / resetChat / saveHistory）。
       通过 window 暴露给设置面板（IIFE #2 的 clearAction）调用。 */
    function clearAllConversations() {
      conversations = [];
      currentConvoId = null;
      if (chatList) {
        chatList.innerHTML = '';
        var empty = document.createElement('li');
        empty.className = 'chat-empty';
        empty.textContent = '（无）';
        chatList.appendChild(empty);
      }
      updateConvoCount();
      resetChat();   /* 若正查看某条对话，复位主区到首页 */
      saveHistory(); /* 持久化空数组，使 loadHistory 走分支二（刷新不重新播种，仅清 cookie 才恢复默认） */
    }
    window.__fipClearConversations = clearAllConversations;

    function scrollChatBottom() {
      const sc = document.querySelector('.main-scroll');
      if (!sc) return;
      /* 智能滚动：只有当消息内容真正溢出可视区时才滚到底。
         main-scroll 的可滚动量 = scrollHeight - clientHeight。
         内容未溢出时，该值恰好等于遮罩高度（main-inner min-height 100%
         撑满 + 遮罩 151px），此时应保持 scrollTop=0，让第一句停在顶部；
         内容溢出时该值大于遮罩高度，才滚动到底显示最新消息。 */
      const maskH = chatMask ? chatMask.offsetHeight : 0;
      const overflow = sc.scrollHeight - sc.clientHeight;
      sc.scrollTop = overflow > maskH ? sc.scrollHeight : 0;
    }

    function addUserMsg(text) {
      const row = document.createElement('div');
      row.className = 'message message-user';
      row.innerHTML =
        '<div class="bubble bubble-user"><div class="bubble-body"></div></div>' +
        '<div class="avatar avatar-user">宠</div>';
      row.querySelector('.bubble-body').textContent = text;
      chatArea.appendChild(row);
      /* 入场动画期间允许溢出（气泡从画面中部浮入，chat-area 尚在长高） */
      chatArea.classList.add('msg-in');
      clearTimeout(chatArea._msgInTimer);
      chatArea._msgInTimer = setTimeout(function () {
        chatArea.classList.remove('msg-in');
      }, 520);
      scrollChatBottom();
    }

    function addThinkingMsg() {
      const row = document.createElement('div');
      row.className = 'message message-bot message-thinking';
      row.innerHTML =
        '<div class="avatar avatar-bot"><img src="file=asset/bot_avatar.jpg" alt="bot" /></div>' +
        '<div class="bubble bubble-bot bubble-thinking">' +
        '<div class="bubble-header"><span class="bubble-name">宠医助手</span><span class="bubble-paw">🐾</span></div>' +
        '<div class="bubble-body">思考中<span class="thinking-dots"><span></span><span></span><span></span></span></div>' +
        '</div>';
      chatArea.appendChild(row);
      scrollChatBottom();
      return row;
    }

    /* 中断 / 取消当前任务：发送按钮（处理中→停止图标）与追问澄清面板 X 共用。
       置空 activeReqId 使迟到的服务端回调因 id 不匹配被忽略；
       移除「思考中」气泡、关闭追问澄清面板，新增一个正常的 bot 对话气泡「回答已中断」，
       并恢复发送按钮为默认态（写入会话数据，便于切换/刷新后回显）。 */
    function interruptCurrent() {
      activeReqId = null;
      /* 移除「思考中」气泡（普通对话中断时存在；追问澄清态下通常不存在） */
      const thinking = chatArea.querySelector('.message-thinking');
      if (thinking) thinking.remove();
      /* 关闭追问澄清面板 + 引导气泡（若有） */
      hideClarifyPanel();
      /* 新增「回答已中断」对话气泡 + 清状态 */
      const convo = getCurrentConvo();
      if (convo) {
        convo.pendingClarify = null;
        convo.msgs.push({ role: 'bot', text: '回答已中断', trace: null });
        saveHistory();
      }
      if (convo && currentConvoId === convo.id) {
        const r2 = addBotMsg();
        typeText(r2, '回答已中断');
        attachTraceIcon(r2, null);
      }
      /* 恢复发送按钮为默认发送态（无文字时为灰色禁用） */
      setSendMode('idle');
    }

    function addBotMsg() {
      const row = document.createElement('div');
      row.className = 'message message-bot';
      row.innerHTML =
        '<div class="avatar avatar-bot"><img src="file=asset/bot_avatar.jpg" alt="bot" /></div>' +
        '<div class="bubble bubble-bot">' +
        '<div class="bubble-header"><span class="bubble-name">宠医助手</span><span class="bubble-paw">🐾</span></div>' +
        '<div class="bubble-body"></div>' +
        '</div>';
      chatArea.appendChild(row);
      return row;
    }

    function typeText(row, text) {
      const body = row.querySelector('.bubble-body');
      const cursor = document.createElement('span');
      cursor.className = 'type-cursor';
      body.appendChild(cursor);
      let i = 0;
      const timer = setInterval(function () {
        i += 2;
        body.textContent = text.slice(0, i);
        body.appendChild(cursor);
        scrollChatBottom();
        if (i >= text.length) {
          clearInterval(timer);
          cursor.remove();
          scrollChatBottom();
        }
      }, 28);
    }

    /* 意图标签：仅在 meta / emergency 等高优先级意图时显示暖杏风 chip（其余意图不显） */
    function addIntentChip(row, intent) {
      if (!row || !intent || !INTENT_CHIP_INTENTS[intent]) return;
      const header = row.querySelector('.bubble-header');
      if (!header) return;
      const chip = document.createElement('span');
      chip.className = 'bubble-intent ' + INTENT_CHIP_INTENTS[intent];
      chip.textContent = INTENT_LABELS[intent] || intent;
      header.appendChild(chip);
    }

    /* ===== 后端推理调用与结果渲染 ===== */

    /* 在途请求跟踪：reqSeq 自增生成唯一 id，activeReqId 指向当前进行中的请求。
       中断时把 activeReqId 置空，使后续迟到的回调因 id 不匹配而被忽略，达到「中断回答」效果。 */
    let reqSeq = 0;
    let activeReqId = null;

    function runQuery(text) {
      /* 锁定发起时的会话 id：避免回复返回前用户切换会话，导致回复错配到新会话 */
      const convoId = currentConvoId;
      const reqId = ++reqSeq;
      activeReqId = reqId;
      /* 发送按钮切换为「停止」态（外框不变，纸飞机→方块中止图标，始终可点） */
      setSendMode('processing');
      /* 读取发起时会话的上下文实体（上一轮成功解析的实体，供连续对话继承） */
      let convo = null;
      for (var i = 0; i < conversations.length; i++) {
        if (conversations[i].id === convoId) { convo = conversations[i]; break; }
      }
      const contextEntities = convo ? (convo.contextEntities || []) : [];
      const thinking = addThinkingMsg();
      logBehavior(BEHAVIOR_QUESTION, text);
      server.respond(text, contextEntities, window.currentBackend ? window.currentBackend() : 'local').then(function (result) {
        /* 若请求已被中断（用户点了停止 / 面板 X），直接丢弃该迟到结果 */
        if (reqId !== activeReqId) return;
        activeReqId = null;
        setSendMode('idle');
        thinking.remove();
        /* 回填到发起时的会话（而非「当前」会话） */
        if (convo) {
          /* 保存本次推理轨迹：供切换/恢复会话时回显最后一步分析过程 */
          convo.lastTrace = result.trace;
          /* 更新上下文实体：本轮成功解析到实体则缓存，供下一轮继承 */
          if (result.entities && result.entities.length) {
            convo.contextEntities = result.entities;
          }
          if (result.status === 'clarify') {
            /* 待澄清状态：存入会话数据，切换/刷新后可继续；不清空已有消息 */
            convo.pendingClarify = { options: result.clarify_options };
          } else {
            /* 已澄清/已解答：清除待澄清状态，并写入 bot 回复 */
            convo.pendingClarify = null;
            convo.msgs.push({ role: 'bot', text: result.summary || result.boundary_hint || '', intent: result.intent || null, trace: result.trace || null });
          }
        }
        saveHistory();
        /* 仅当仍停留在发起时的会话，才把回复渲染到当前画面 */
        if (currentConvoId === convoId) {
          renderResult(result);
        }
      }).catch(function () {
        /* 若请求已被中断，忽略错误（不重复渲染） */
        if (reqId !== activeReqId) return;
        activeReqId = null;
        setSendMode('idle');
        thinking.remove();
        if (currentConvoId === convoId) {
          typeText(addBotMsg(), '抱歉，服务暂时不可用，请稍后再试。');
        }
      });
    }

    function renderResult(result) {
      /* 新回复渲染前，清除任何历史轨迹高亮（右侧面板将显示最新轨迹） */
      clearTraceSelection();
      let row = null;
      if (result.status === 'ok') {
        row = addBotMsg();
        typeText(row, result.summary);
        addIntentChip(row, result.intent);
        attachTraceIcon(row, result.trace);
      } else if (result.status === 'clarify') {
        addClarifyMsg(result.clarify_options);
      } else if (result.status === 'boundary') {
        row = addBotMsg();
        typeText(row, result.boundary_hint || '当前知识库暂无该路径，建议咨询兽医。');
        addIntentChip(row, result.intent);
        attachTraceIcon(row, result.trace);
      } else if (result.status === 'error') {
        row = addBotMsg();
        typeText(row, '抱歉，查询时出现异常：' + (result.error_message || '未知错误'));
        attachTraceIcon(row, null);
      }
      renderTrace(result.trace);
    }

    function addClarifyMsg(options) {
      const row = addBotMsg();
      row.classList.add('clarify-bubble');
      const body = row.querySelector('.bubble-body');
      const tip = document.createElement('div');
      tip.className = 'clarify-tip';
      tip.textContent = '这个问题可能涉及多个方面，你想了解哪一方面？';
      body.appendChild(tip);
      showClarifyPanel(options);
  scrollChatBottom();
    }

    /* 追问面板：覆盖在 textarea 区域（遮住「描述你的问题…」），竖排候选项 + 底部自由输入 */
    function showClarifyPanel(options) {
      hideClarifyPanel();
      const box = document.querySelector('.input-box');
      const textWrap = document.querySelector('.input-text-wrap');
      if (!box || !textWrap) return;
      const panel = document.createElement('div');
      panel.className = 'clarify-panel';
      /* 顶部小标题：请您确认： */
      const sub = document.createElement('div');
      sub.className = 'clarify-subtitle';
      sub.textContent = '请您确认：';
      panel.appendChild(sub);
      /* 右上角关闭 X（无外框，仅简单 X）：点击走与发送按钮停止相同的中断逻辑 */
      const closeX = document.createElement('button');
      closeX.type = 'button';
      closeX.className = 'clarify-close';
      closeX.dataset.tooltip = '中断';
      closeX.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>';
      closeX.addEventListener('click', function () { interruptCurrent(); });
      panel.appendChild(closeX);
      /* 2~3 个追问选项（纵向轻量胶囊，右侧箭头） */
      (options || []).forEach(function (o) {
        const opt = document.createElement('button');
        opt.type = 'button';
        opt.className = 'clarify-opt';
        const lbl = document.createElement('span');
        lbl.className = 'clarify-opt-label';
        lbl.textContent = o.label;
        const arr = document.createElement('span');
        arr.className = 'clarify-opt-arrow';
        arr.innerHTML = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
        opt.appendChild(lbl);
        opt.appendChild(arr);
        opt.addEventListener('click', function () {
          hideClarifyPanel();
          runQuery(o.value);
        });
        panel.appendChild(opt);
      });
      /* 底部自由输入：与上面一致的胶囊，占位「其他（请补充）」（回车 / 点发送，继承当前实体上下文） */
      const other = document.createElement('div');
      other.className = 'clarify-other';
      const inp = document.createElement('input');
      inp.type = 'text';
      inp.className = 'clarify-other-input';
      inp.placeholder = '其他（请补充）';
      const obtn = document.createElement('button');
      obtn.type = 'button';
      obtn.className = 'clarify-send';
      obtn.dataset.tooltip = '发送';
      obtn.disabled = true;
      obtn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';
      function updateClarifySend() {
        obtn.disabled = !((inp.value || '').trim());
      }
      obtn.addEventListener('click', function () {
        const v = (inp.value || '').trim();
        if (!v) return;
        hideClarifyPanel();
        send(v);
      });
      inp.addEventListener('keydown', function (e) {
        if (e.isComposing || e.keyCode === 229) return;
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          const v = (inp.value || '').trim();
          if (!v) return;
          hideClarifyPanel();
          send(v);
        }
      });
      inp.addEventListener('input', updateClarifySend);
      other.appendChild(inp);
      other.appendChild(obtn);
      panel.appendChild(other);
      box.insertBefore(panel, textWrap);
      /* 标记 clarifying：隐藏真正的 textarea，避免两个可输入区域同时出现 */
      box.classList.add('clarifying');
    }

    function hideClarifyPanel() {
      const p = document.querySelector('.clarify-panel');
      if (p) p.remove();
      const bubble = document.querySelector('.clarify-bubble');
      if (bubble) bubble.remove();
      const box = document.querySelector('.input-box');
      if (box) box.classList.remove('clarifying');
    }

    /* ===== 右侧栏 AI 分析过程（三段式：Header + Timeline + Detail）===== */
    const STEP_STATUS_MAP = { success: 'completed', failed: 'error', skipped: 'skipped' };
    const KEY_LABELS = {
      entities: '实体', inherited: '上下文继承', scores: '得分', candidates: '候选意图',
      intent: '意图', template: '查询模板', steps: '关系', groups: '分组', risks: '风险',
      summary: '摘要', cards: '结果项', reason: '原因', error: '错误',
      source: '来源', rel: '关系', target: '目标', polarity: '极性', confidence: '置信度', evidence: '支撑依据',
      kind: '类型', group_key: '分组', step_index: '位置', note: '说明',
      label: '名称', count: '数量', key: '键', flagged: '风险标记'
    };
    const POLARITY_LABELS = { Positive: '正面', Negative: '负面', Neutral: '中性' };
    const CONFIDENCE_LABELS = { High: '高', Medium: '中', Low: '低' };
    const KIND_LABELS = { low_confidence: '低置信度' };
    /* 意图标签（仅 meta/emergency 在气泡内显示，其余意图不显以保持简洁）；颜色走暖杏风 */
    const INTENT_LABELS = {
      concept: '概念科普', diagnosis: '诊断判断', treatment: '治疗与预后',
      risk: '药物风险', general: '综合问答', meta: '系统引导', emergency: '紧急提示'
    };
    const INTENT_CHIP_INTENTS = { meta: 'intent-meta', emergency: 'intent-emergency' };
    const TRACE_STEP_INTERVAL = 400;  // 每步点亮间隔（毫秒）

    const analysisState = {
      steps: [],             // 后端步骤映射后的数组
      selectedStepId: null,  // 当前选中（查看）的步骤 id
      isUserSelected: false, // 用户是否主动点击过（锁定跟随）
      playToken: 0           // 播放令牌（新消息/切会话自增，中断旧播放）
    };

    /* 清空右侧栏为初始空态（新建任务 / 切换到无轨迹会话时调用） */
    function resetTracePanel() {
      analysisState.playToken++;
      analysisState.steps = [];
      analysisState.selectedStepId = null;
      analysisState.isUserSelected = false;
      setDetailExpanded(false);
      const status = document.getElementById('analysisStatus');
      if (status) status.innerHTML = '';
      const input = document.getElementById('analysisInput');
      if (input) input.innerHTML = '';
      const timeline = document.getElementById('traceTimeline');
      if (timeline) timeline.innerHTML = '<div class="trace-empty">发送问题后，这里会展示 AI 分析 Timeline</div>';
      const detail = document.getElementById('traceDetailBody');
      if (detail) detail.innerHTML = '<div class="detail-empty">点击步骤查看详细内容</div>';
    }

    function renderTrace(trace, instant) {
      const timeline = document.getElementById('traceTimeline');
      const detail = document.getElementById('traceDetail');
      if (!timeline || !detail) return;
      /* 空轨迹（历史消息无 trace 字段 / 无步骤）：清空面板并显示占位提示，
         避免沿用上一轮内容；兼容旧版 localStorage 数据（无 trace 字段不报错）。 */
      if (!trace || !trace.steps || !trace.steps.length) {
        analysisState.playToken++;
        analysisState.steps = [];
        analysisState.selectedStepId = null;
        analysisState.isUserSelected = false;
        setDetailExpanded(false);
        const status = document.getElementById('analysisStatus');
        if (status) status.innerHTML = '';
        const input = document.getElementById('analysisInput');
        if (input) input.innerHTML = '';
        timeline.innerHTML = '<div class="trace-empty">该轮暂无执行轨迹</div>';
        renderDetailEmpty();
        return;
      }

      const token = ++analysisState.playToken;
      analysisState.selectedStepId = null;
      analysisState.isUserSelected = false;
      setDetailExpanded(false);

      /* 映射后端步骤 -> 前端状态：finalStatus 为落定态，status 为播放中的当前态 */
      analysisState.steps = (trace.steps || []).map(function (s) {
        return {
          id: s.step_id,
          title: s.step_name,
          summary: s.output_summary || '',
          finalStatus: STEP_STATUS_MAP[s.status] || 'pending',
          status: 'pending',
          detail: s.detail,
          skip_reason: s.skip_reason || '',
          output_summary: s.output_summary || ''
        };
      });

      renderHeaderInput(trace);
      renderTimeline();
      renderDetailEmpty();
      if (instant) {
        /* 回显历史：不播放动画，直接落定全部步骤并选中最后一步 */
        analysisState.steps.forEach(function (s) {
          s.status = s.finalStatus;
          setStepStatus(s.id, s.finalStatus);
        });
        updateHeaderStatus();
        const last = analysisState.steps[analysisState.steps.length - 1];
        if (last) selectStep(last.id, false);
      } else {
        playSteps(token);
      }
    }

    /* ===== 历史回答「查看执行轨迹」交互 ===== */
    var currentTraceMsgEl = null;     // 当前高亮的历史气泡 DOM 引用（对应规格 currentTraceMessageId）
    var currentTraceMessageId = null; // 当前选中的消息标识（convoId:mid），供状态记录

    /* 在 bot 气泡右上角挂一个轻量「查看执行轨迹」图标（整段气泡均可点击查看，图标仅为视觉提示） */
    function attachTraceIcon(row, trace) {
      const bubble = row.querySelector('.bubble-bot');
      if (!bubble) return;
      row._traceData = trace;   // 把该轮轨迹挂到整段消息 row 上，供气泡任意位置点击复用
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'trace-view-btn';
      btn.setAttribute('data-tooltip', '查看执行轨迹');   // 复用通用白色浮窗（替代原生 title 黑底）
      btn.setAttribute('aria-label', '查看执行轨迹');
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h11M4 18h14"/></svg>';
      bubble.appendChild(btn);
    }

    /* 选中某条历史轨迹：高亮该气泡 + 右侧面板切换为该轮（instant 不重播动画） */
    function selectTrace(row, trace) {
      clearTraceSelection();
      row.classList.add('trace-active');
      currentTraceMsgEl = row;
      currentTraceMessageId = (getCurrentConvo() ? getCurrentConvo().id : '') + ':' + (row.dataset.mid || 'live');
      renderTrace(trace, true);
    }

    /* 清除气泡高亮并复位选中状态（用于：点空白区域 / 新对话 / 切换会话） */
    function clearTraceSelection() {
      if (currentTraceMsgEl) currentTraceMsgEl.classList.remove('trace-active');
      currentTraceMsgEl = null;
      currentTraceMessageId = null;
    }

    /* Header 输入摘要（类型标签 + 用户输入，最多两行） */
    function renderHeaderInput(trace) {
      const inputEl = document.getElementById('analysisInput');
      if (!inputEl) return;
      inputEl.innerHTML = '';
      const tag = document.createElement('span');
      const isComposite = trace.input_type === '复合澄清输入';
      tag.className = 'input-type-tag ' + (isComposite ? 'type-composite' : 'type-normal');
      tag.textContent = trace.input_type || '普通文本';
      inputEl.appendChild(tag);
      inputEl.appendChild(document.createTextNode(trace.user_input || ''));
    }

    /* Header 状态：正在分析 X / N 或 已完成 X / N */
    function updateHeaderStatus() {
      const el = document.getElementById('analysisStatus');
      if (!el) return;
      const steps = analysisState.steps;
      const total = steps.length;
      const settled = steps.filter(function (s) {
        return s.status === 'completed' || s.status === 'error' || s.status === 'skipped';
      }).length;
      const failed = steps.filter(function (s) { return s.status === 'error'; }).length;
      const running = steps.some(function (s) { return s.status === 'running'; });

      let cls, text;
      if (running) { cls = 'is-running'; text = '正在分析 · ' + settled + ' / ' + total; }
      else if (failed > 0) { cls = 'is-error'; text = '执行异常 · 已完成 ' + settled + ' / ' + total; }
      else { cls = 'is-completed'; text = '已完成 ' + settled + ' / ' + total + ' 个分析步骤'; }

      el.className = 'analysis-status ' + cls;
      el.innerHTML = '';
      const dot = document.createElement('span');
      dot.className = 'status-dot';
      el.appendChild(dot);
      el.appendChild(document.createTextNode(text));
    }

    /* Timeline：渲染全部步骤为 pending 态 */
    function renderTimeline() {
      const timeline = document.getElementById('traceTimeline');
      if (!timeline) return;
      timeline.innerHTML = '';
      analysisState.steps.forEach(function (s) {
        timeline.appendChild(buildStepNode(s));
      });
    }

    function buildStepNode(s) {
      const el = document.createElement('div');
      el.className = 'analysis-step';
      el.dataset.stepId = s.id;

      const rail = document.createElement('div');
      rail.className = 'step-rail';
      const node = document.createElement('div');
      node.className = 'step-node node-pending';
      rail.appendChild(node);

      const info = document.createElement('div');
      info.className = 'step-info';
      const title = document.createElement('div');
      title.className = 'step-title';
      title.textContent = s.title;
      info.appendChild(title);
      if (s.summary) {
        const summary = document.createElement('div');
        summary.className = 'step-summary';
        summary.textContent = s.summary;
        info.appendChild(summary);
      }

      el.appendChild(rail);
      el.appendChild(info);
      el.addEventListener('click', function () { selectStep(s.id, true); });
      return el;
    }

    /* 更新某一步的节点状态（含节点文案 ✓ / ✕） */
    function setStepStatus(stepId, status) {
      const el = document.querySelector('.analysis-step[data-step-id="' + stepId + '"]');
      if (!el) return;
      const node = el.querySelector('.step-node');
      if (node) {
        node.className = 'step-node node-' + status;
        if (status === 'completed') node.textContent = '✓';
        else if (status === 'error') node.textContent = '✕';
        else node.textContent = '';
      }
      el.classList.toggle('is-skipped', status === 'skipped');
    }

    /* 选中步骤：更新选中态 + 刷新 Detail（点击锁定跟随） */
    function selectStep(stepId, isUser) {
      if (isUser) analysisState.isUserSelected = true;
      const changed = analysisState.selectedStepId !== stepId;
      analysisState.selectedStepId = stepId;
      document.querySelectorAll('.analysis-step').forEach(function (el) {
        el.classList.toggle('is-selected', String(el.dataset.stepId) === String(stepId));
      });
      if (changed) renderDetail(stepId);
    }

    /* Timeline 自动滚动到指定步骤（使当前 running 步骤保持可见） */
    function scrollTimelineToStep(stepId) {
      const timeline = document.getElementById('traceTimeline');
      const el = timeline && timeline.querySelector('.analysis-step[data-step-id="' + stepId + '"]');
      if (!el) return;
      const tRect = timeline.getBoundingClientRect();
      const eRect = el.getBoundingClientRect();
      timeline.scrollTop += (eRect.top - tRect.top) - 8;
    }

    /* 播放：success/failed 先 running 再落定；skipped 立即灰态 */
    function playSteps(token) {
      const steps = analysisState.steps;
      let i = 0;
      function next() {
        if (token !== analysisState.playToken) return;
        if (i >= steps.length) { updateHeaderStatus(); return; }
        const s = steps[i++];
        if (s.finalStatus === 'skipped') {
          s.status = 'skipped';
          setStepStatus(s.id, 'skipped');
          if (!analysisState.isUserSelected) selectStep(s.id, false);
          updateHeaderStatus();
          next();
          return;
        }
        s.status = 'running';
        setStepStatus(s.id, 'running');
        scrollTimelineToStep(s.id);
        if (!analysisState.isUserSelected) selectStep(s.id, false);
        updateHeaderStatus();
        setTimeout(function () {
          if (token !== analysisState.playToken) return;
          s.status = s.finalStatus;
          setStepStatus(s.id, s.finalStatus);
          if (!analysisState.isUserSelected) selectStep(s.id, false);
          /* 落定后若当前查看的就是本步骤，刷新 Detail 反映最终态（副标题「正在执行…」→「已完成」） */
          if (String(analysisState.selectedStepId) === String(s.id)) renderDetail(s.id);
          updateHeaderStatus();
          next();
        }, TRACE_STEP_INTERVAL);
      }
      next();
    }

    /* Detail 空态 */
    function renderDetailEmpty() {
      const panel = document.getElementById('traceDetailBody');
      if (!panel) return;
      panel.innerHTML = '';
      const empty = document.createElement('div');
      empty.className = 'detail-empty';
      empty.textContent = '点击步骤查看详细内容';
      panel.appendChild(empty);
    }

    /* Detail 渲染 */
    function renderDetail(stepId) {
      const panel = document.getElementById('traceDetailBody');
      if (!panel) return;
      const s = analysisState.steps.find(function (x) { return String(x.id) === String(stepId); });
      panel.innerHTML = '';
      if (!s) { renderDetailEmpty(); return; }

      const head = document.createElement('div');
      head.className = 'detail-head';
      const headText = document.createElement('div');
      headText.className = 'detail-head-text';
      const title = document.createElement('div');
      title.className = 'detail-head-title';
      title.textContent = s.title;
      headText.appendChild(title);
      const subtitle = document.createElement('div');
      subtitle.className = 'detail-head-subtitle';
      subtitle.textContent = detailSubtitle(s);
      headText.appendChild(subtitle);
      head.appendChild(headText);
      head.appendChild(buildExpandBtn());
      panel.appendChild(head);

      const content = document.createElement('div');
      content.className = 'detail-content';
      renderDetailContent(content, s);
      panel.appendChild(content);
    }

    function detailSubtitle(s) {
      if (s.status === 'skipped') return '该步骤已跳过';
      if (s.status === 'running') return '正在执行…';
      if (s.status === 'error') return '执行失败';
      return '已完成';
    }

    function renderDetailContent(container, s) {
      if (s.status === 'skipped') {
        addDetailText(container, s.skip_reason || '该步骤未执行');
        return;
      }
      if (s.status === 'error') {
        addDetailText(container, s.output_summary || '执行异常');
        return;
      }
      renderField(container, s.detail, s.output_summary);
    }

    /* 有限字段渲染：已知字段针对性处理，未知字段走通用 kv */
    function renderField(container, value, fallback) {
      if (value == null) {
        if (fallback) addDetailText(container, fallback);
        return;
      }
      if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
        addDetailText(container, String(value));
        return;
      }
      if (Array.isArray(value)) {
        if (value.length === 0) { addDetailText(container, '无'); return; }
        value.forEach(function (item) {
          if (item != null && typeof item === 'object' && (item.source != null || item.rel != null)) {
            container.appendChild(buildRelationRow(item));
          } else if (item != null && typeof item === 'object') {
            addDetailItem(container, item);
          } else {
            addDetailText(container, String(item));
          }
        });
        return;
      }
      if (typeof value === 'object') {
        Object.keys(value).forEach(function (k) {
          const v = value[k];
          const label = KEY_LABELS[k] || k;
          if (k === 'cards') {
            renderCards(container, v);
          } else if (k === 'summary') {
            addDetailText(container, formatScalar(k, v));
          } else if (k === 'scores') {
            addDetailSection(container, label, v, 'scores');
          } else if (Array.isArray(v)) {
            addDetailSection(container, label, v);
          } else if (v != null && typeof v === 'object') {
            addDetailSection(container, label, v);
          } else {
            addDetailKV(container, label, formatScalar(k, v));
          }
        });
      }
    }

    function renderCards(container, cards) {
      (cards || []).forEach(function (card) {
        if (card == null) return;
        const sec = document.createElement('div');
        sec.className = 'detail-section';
        const lab = document.createElement('div');
        lab.className = 'detail-label';
        lab.textContent = card.label || card.key || '分组';
        sec.appendChild(lab);
        (card.steps || []).forEach(function (st) {
          sec.appendChild(buildRelationRow(st));
        });
        container.appendChild(sec);
      });
    }

    function buildRelationRow(st) {
      const row = document.createElement('div');
      row.className = 'detail-relation';
      const main = document.createElement('div');
      main.className = 'rel-main';
      main.textContent = (st.source || '') + ' → ' + (st.target || '') + '（' + (st.rel || '') + '）';
      row.appendChild(main);
      const meta = document.createElement('div');
      meta.className = 'rel-meta';
      meta.textContent = '极性：' + (POLARITY_LABELS[st.polarity] || st.polarity || '—') +
        ' · 置信度：' + (CONFIDENCE_LABELS[st.confidence] || st.confidence || '—') +
        (st.flagged ? ' · ⚠ 低置信度风险' : '');
      row.appendChild(meta);
      if (st.evidence) {
        const ev = document.createElement('div');
        ev.className = 'rel-evidence';
        ev.textContent = '依据：' + st.evidence;
        row.appendChild(ev);
      }
      return row;
    }

    /* 带标题的子区块：内部值按类型渲染 */
    function addDetailSection(container, label, value, mode) {
      const sec = document.createElement('div');
      sec.className = 'detail-section';
      const lab = document.createElement('div');
      lab.className = 'detail-label';
      lab.textContent = label;
      sec.appendChild(lab);

      if (mode === 'scores') {
        Object.keys(value || {}).forEach(function (k) {
          addDetailKV(sec, k, String(value[k]));
        });
      } else if (Array.isArray(value)) {
        if (value.length === 0) { addDetailText(sec, '无'); }
        value.forEach(function (item) {
          if (item != null && typeof item === 'object') {
            if (item.source != null || item.rel != null) {
              sec.appendChild(buildRelationRow(item));
            } else if (item.kind != null) {
              addDetailKV(sec, KIND_LABELS[item.kind] || item.kind, item.note || '');
            } else if (item.label != null) {
              addDetailKV(sec, item.label, (item.count != null ? item.count + ' 条' : ''));
            } else {
              addDetailItem(sec, item);
            }
          } else {
            addDetailText(sec, String(item));
          }
        });
      } else if (value != null && typeof value === 'object') {
        Object.keys(value).forEach(function (k) {
          addDetailKV(sec, KEY_LABELS[k] || k, formatScalar(k, value[k]));
        });
      } else {
        addDetailText(sec, formatScalar(null, value));
      }
      container.appendChild(sec);
    }

    /* 把对象扁平化为若干键值行 */
    function addDetailItem(container, obj) {
      Object.keys(obj).forEach(function (k) {
        addDetailKV(container, KEY_LABELS[k] || k, formatScalar(k, obj[k]));
      });
    }

    function addDetailText(container, text) {
      const p = document.createElement('div');
      p.className = 'detail-text';
      p.textContent = text;
      container.appendChild(p);
    }

    function addDetailKV(container, label, text) {
      const row = document.createElement('div');
      row.className = 'detail-kv';
      const kl = document.createElement('span');
      kl.className = 'dk-label';
      kl.textContent = label;
      row.appendChild(kl);
      const kv = document.createElement('span');
      kv.className = 'dk-value';
      kv.textContent = text;
      row.appendChild(kv);
      container.appendChild(row);
    }

    function formatScalar(key, v) {
      if (v == null) return '—';
      if (typeof v === 'boolean') return v ? '是' : '否';
      if (Array.isArray(v)) return v.join('、');
      if (typeof v === 'object') { try { return JSON.stringify(v); } catch (e) { return String(v); } }
      if (key === 'polarity') return POLARITY_LABELS[v] || v;
      if (key === 'confidence') return CONFIDENCE_LABELS[v] || v;
      if (key === 'kind') return KIND_LABELS[v] || v;
      return String(v);
    }

    /* ===== 模型选择下拉 ===== */
    const modelBtn = document.querySelector('.model-btn');
    const modelPopover = document.querySelector('.model-popover');
    const modelLabel = document.querySelector('.model-label');
    function toggleModelPopover(show) {
      if (!modelPopover || !modelBtn) return;
      if (typeof show === 'undefined') show = modelPopover.classList.contains('hidden');
      if (show) {
        modelPopover.classList.remove('hidden');
        modelBtn.classList.add('open');
      } else {
        modelPopover.classList.add('hidden');
        modelBtn.classList.remove('open');
      }
    }
    if (modelBtn && modelPopover) {
      modelBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        toggleModelPopover();
      });
      modelPopover.addEventListener('click', function (e) {
        const opt = e.target.closest('.model-option');
        if (!opt || opt.classList.contains('disabled')) return;
        if (opt.dataset.value === 'pro' && modelLabel) modelLabel.textContent = '宠医助手 · Pro';
        modelPopover.querySelectorAll('.model-option').forEach(function (o) { o.classList.toggle('active', o === opt); });
        toggleModelPopover(false);
      });
      document.addEventListener('click', function (e) {
        if (!modelPopover.classList.contains('hidden') && !e.target.closest('.model-select-wrap')) {
          toggleModelPopover(false);
        }
      });
    }

    function send(prefill) {
      const text = (prefill != null ? String(prefill) : (textarea.innerText || '')).trim();
      if (!text) return;
      if (prefill == null) textarea.innerText = '';
      updateSendState();
      enterChatMode();
      /* 会话记录：首次发送新建条目（标题 = 首条消息）置顶插入最近对话 */
      let convo = getCurrentConvo();
      if (!convo) convo = addConversation(text);
      convo.msgs.push({ role: 'user', text: text });
      addUserMsg(text);
      saveHistory();
      runQuery(text);
    }

    /* 发送按钮：处理中（activeReqId 非空）点击=中断；否则=发送 */
    sendBtn.addEventListener('click', function () {
      if (activeReqId !== null) {
        interruptCurrent();
      } else {
        send();
      }
    });
    textarea.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });
    /* 新建任务按钮 / 最近对话：改用 document 事件委托，
       避免 Gradio 重渲染导致一次性 forEach 绑定丢失（与 nav-item 委托同理）。
       页面模式下（图数据库/文献库/产品设计）main-area 被隐藏，必须先退出页面模式
       回到首页聊天界面，否则功能执行了但看不到反馈 */
    document.addEventListener('click', function (e) {
      var t = e.target;
      if (!t || !t.closest) return;
      if (t.closest('.new-task-btn') || t.closest('.collapsed-tool')) {
        var shell = document.getElementById('appShell');
        if (shell) shell.classList.remove('mode-graph', 'mode-docs', 'mode-design');
        /* 回到首页对话时，取消左侧导航页高亮 */
        document.querySelectorAll('.nav-item.active').forEach(function(n){n.classList.remove('active');});
        resetChat();
        return;
      }
      var ci = t.closest('.chat-item');
      if (ci && ci.dataset.cid) {
        var shell = document.getElementById('appShell');
        if (shell) shell.classList.remove('mode-graph', 'mode-docs', 'mode-design');
        var pageDesign = document.getElementById('pageDesign');
        if (pageDesign) pageDesign.classList.remove('is-modal');
        document.body.style.overflow = '';
        /* 切换到历史对话时，取消左侧导航页高亮 */
        document.querySelectorAll('.nav-item.active').forEach(function(n){n.classList.remove('active');});
        switchConvo(ci.dataset.cid);
        return;
      }
      /* 快速开始卡片：点击直接用卡片文字发起对话 */
      var fc = t.closest('.feature-card');
      if (fc) {
        var nameEl = fc.querySelector('.feature-name');
        if (nameEl) {
          var shell = document.getElementById('appShell');
          if (shell) shell.classList.remove('mode-graph', 'mode-docs', 'mode-design');
          document.querySelectorAll('.nav-item.active').forEach(function(n){n.classList.remove('active');});
          send(nameEl.textContent.trim());
        }
        return;
      }
      /* 左上角 LOGO + slogan：点击回到默认首页（与新建任务一致的复位逻辑） */
      if (t.closest('.brand')) {
        var shell = document.getElementById('appShell');
        if (shell) shell.classList.remove('mode-graph', 'mode-docs', 'mode-design');
        document.querySelectorAll('.nav-item.active').forEach(function(n){n.classList.remove('active');});
        resetChat();
        return;
      }
    });

    /* 页面加载：从 localStorage 恢复历史记录 */
    loadHistory();

    /* 初始化可拖动调整尺寸 */
    initSidebarResizer();
    initDetailResizer();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindShell);
  } else {
    bindShell();
  }

})();

/* ===== 设置功能：面板 / Modal / Password / Toast（前端壳，真实参数待补） ===== */
(function () {
  if (typeof document === 'undefined') return;
  var $ = function (id) { return document.getElementById(id); };
  var settingsEl = $('stSettings');
  var modalEl = $('stModal');
  var modalBox = $('stModalBox');
  var modalContent = $('stModalContent');
  var toastStack = $('stToastStack');
  var bridgeEl = $('stBridge');
  if (!settingsEl || !modalEl) return;

  /* 密码校验：仅保存「盐 + 密码」的 SHA-256 摘要，不再出现明文密码（本地软性门禁，非强安全）。
     支持多密码白名单：把每个允许密码用相同 salt 重算后的摘要追加到 ST_PWD_HASHES 数组即可。
       python -c "import hashlib;print(hashlib.sha256(('aeropan-fip-gate-v1'+'YOUR_PWD').encode()).hexdigest())"
     注意：crypto.subtle 需安全上下文（https 或 localhost）；非安全 http 环境下校验将直接失败（安全兜底）。
     当前有效密码（仅存摘要）：069473doublE / 20130506 */
  var ST_PWD_SALT = 'aeropan-fip-gate-v1';
  var ST_PWD_HASHES = [
    '277d6be779d1d6ce60e34d2835576f0e9defd8de119b7fc39597764968bb6a08',
    '6735a98cfc8f114cb2cf9b5e41d6ff70883f505c85114cfc80f7203ec5666e35'
  ];
  function bufToHex(buf) {
    return Array.prototype.map.call(new Uint8Array(buf), function (b) {
      return ('0' + b.toString(16)).slice(-2);
    }).join('');
  }
  function hashPwdEquals(pwd) {
    var data = new TextEncoder().encode(ST_PWD_SALT + pwd);
    if (window.crypto && window.crypto.subtle && window.crypto.subtle.digest) {
      return window.crypto.subtle.digest('SHA-256', data).then(function (buf) {
        return ST_PWD_HASHES.indexOf(bufToHex(buf)) !== -1;
      });
    }
    return Promise.resolve(false);
  }

  var ICONS = {
    success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><line x1="12" y1="8" x2="12" y2="8.01"/></svg>',
    warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9 16H3z"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="12" y1="17" x2="12" y2="17.01"/></svg>',
    error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    eye: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>',
    eyeOff: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
  };

  var st = { panelOpen: false, modalOpen: false, modalReturnToPanel: false, bridgeMode: 'networkx', pwdAction: null, watermarked: true };

  /* ---------- 设置面板 ---------- */
  function getAnchor() {
    var sidebar = document.querySelector('.left-sidebar');
    if (sidebar && sidebar.classList.contains('collapsed')) return sidebar;
    return document.querySelector('.left-footer') || sidebar;
  }
  function positionPanel() {
    var anchor = getAnchor();
    if (!anchor) return;
    var r = anchor.getBoundingClientRect();
    var left = r.left;
    if (left < 12) left = 12;
    settingsEl.style.left = left + 'px';
    settingsEl.style.bottom = '24px';
  }
  window.addEventListener('resize', function () { if (st.panelOpen) positionPanel(); });
  function renderBridge() {
    if (!bridgeEl) return;
    var segN = bridgeEl.querySelector('[data-st-bridge="networkx"]');
    var segJ = bridgeEl.querySelector('[data-st-bridge="neo4j"]');
    if (st.bridgeMode === 'neo4j') {
      if (segN) segN.classList.remove('is-active');
      if (segJ) segJ.classList.add('is-active');
    } else {
      if (segJ) segJ.classList.remove('is-active');
      if (segN) segN.classList.add('is-active');
    }
  }
  function currentBackend() {
    return st.bridgeMode === 'neo4j' ? 'neo4j' : 'local';
  }
  window.currentBackend = currentBackend;
  function openPanel() {
    if (st.panelOpen) return;
    fbGuideHide();
    renderBridge();
    positionPanel();
    settingsEl.classList.remove('is-closing');
    settingsEl.classList.add('is-open');
    settingsEl.setAttribute('aria-hidden', 'false');
    st.panelOpen = true;
  }
  function closePanel(immediate) {
    if (!st.panelOpen) return;
    if (immediate) {
      settingsEl.classList.remove('is-open', 'is-closing');
      settingsEl.setAttribute('aria-hidden', 'true');
      st.panelOpen = false;
      return;
    }
    settingsEl.classList.add('is-closing');
    settingsEl.classList.remove('is-open');
    setTimeout(function () {
      settingsEl.classList.remove('is-closing');
      settingsEl.setAttribute('aria-hidden', 'true');
      st.panelOpen = false;
    }, 140);
  }

  /* ---------- Modal ---------- */
  function openModal(opts) {
    st.modalReturnToPanel = !!opts.returnToPanel;
    modalContent.innerHTML = opts.html;
    modalBox.className = 'st-modal__box' + (opts.boxClass ? ' ' + opts.boxClass : '');
    modalContent.style.animation = 'none';
    modalEl.classList.remove('is-closing');
    modalEl.classList.add('is-open');
    modalEl.setAttribute('aria-hidden', 'false');
    fbGuideHide();
    st.modalOpen = true;
    if (opts.onMount) opts.onMount(modalContent);
  }
  function closeModal(noReturn) {
    if (!st.modalOpen) return;
    if (window.__fbOpenSelect) window.__fbOpenSelect.__close();
    if (noReturn) st.modalReturnToPanel = false;
    modalEl.classList.add('is-closing');
    modalEl.classList.remove('is-open');
    var returnToPanel = st.modalReturnToPanel;
    setTimeout(function () {
      modalEl.classList.remove('is-closing');
      modalEl.setAttribute('aria-hidden', 'true');
      modalContent.innerHTML = '';
      st.modalOpen = false;
      if (returnToPanel) openPanel();
    }, 180);
  }
  function replaceModalContent(html, onMount) {
    var box = modalBox;
    var h0 = box.offsetHeight;
    modalContent.style.animation = 'stContentOut 150ms var(--ease) both';
    setTimeout(function () {
      modalContent.innerHTML = html;
      if (onMount) onMount(modalContent);
      var h1 = box.offsetHeight;
      if (h1 !== h0) {
        box.style.transition = 'none';
        box.style.height = h0 + 'px';
        void box.offsetHeight;
        box.style.transition = 'height 160ms var(--ease)';
        box.style.height = h1 + 'px';
        setTimeout(function () {
          box.style.transition = '';
          box.style.height = 'auto';
        }, 220);
      }
      modalContent.style.animation = 'stContentIn 150ms var(--ease) both';
    }, 150);
  }
  function confirmHtml(title, desc, okText, desc2) {
    return '<div class="st-modal__pane">' +
      '<div class="st-modal__title">' + title + '</div>' +
      '<div class="st-modal__desc">' + desc + (desc2 ? '<br><span class="st-modal__desc2">' + desc2 + '</span>' : '') + '</div>' +
      '<div class="st-modal__actions">' +
      '<button class="st-btn st-btn--cancel" data-st-x>取消</button>' +
      '<button class="st-btn st-btn--primary" data-st-ok>' + (okText || '确认') + '</button>' +
      '</div></div>';
  }
  function passwordHtml(desc) {
    return '<div class="st-modal__pane">' +
      '<div class="st-modal__title">身份验证</div>' +
      '<div class="st-modal__desc" id="stPwdDesc">' + desc + '</div>' +
      '<label class="st-field__label" for="stPwdInput">密码<span class="st-field__hint">（密码提示：8位数字，晴天的生日）</span></label>' +
      '<div class="st-input-wrap">' +
      '<input class="st-input" id="stPwdInput" type="password" placeholder="请输入密码" autocomplete="off" />' +
      '<button class="st-eye" id="stPwdEye" type="button" aria-label="显示密码">' + ICONS.eye + '</button>' +
      '</div>' +
      '<div class="st-error" id="stPwdError">密码输入不正确，请重新输入。</div>' +
      '<div class="st-modal__actions">' +
      '<button class="st-btn st-btn--cancel" id="stPwdCancel">取消</button>' +
      '<button class="st-btn st-btn--primary" id="stPwdContinue" disabled>继续</button>' +
      '</div></div>';
  }

  /* ---------- Toast ---------- */
  function showToast(message, type) {
    type = type || 'success';
    var color = ({ success: '#6F8A6A', info: '#6D8795', warning: '#C38A35', error: '#B86B5B' })[type] || '#6F8A6A';
    var toast = document.createElement('div');
    toast.className = 'st-toast';
    toast.innerHTML = '<span class="st-toast__icon" style="color:' + color + '">' + (ICONS[type] || ICONS.success) + '</span><div class="st-toast__msg">' + message + '</div>';
    toastStack.appendChild(toast);
    setTimeout(function () {
      toast.classList.add('is-closing');
      setTimeout(function () { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 160);
    }, 3000);
  }

  /* ---------- 各功能 ---------- */
  function feedbackFormHtml() {
    return '' +
    '<div class="fb-modal" id="fbModal">' +
      '<div class="fb-modal__head">' +
        '<div class="fb-modal__titles">' +
          '<div class="fb-modal__title">意见反馈</div>' +
        '</div>' +
        '<button class="fb-modal__close" data-st-x type="button" aria-label="关闭"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>' +
      '</div>' +
      '<div class="fb-modal__body">' +
        '<div class="fb-modal__sub">感谢你愿意分享你的想法，你的反馈将帮助我们持续改进。</div>' +
        '<div class="fb-field">' +
          '<label class="fb-label" for="fbName">如何称呼您<span class="fb-req">*</span></label>' +
          '<input class="st-input fb-input" id="fbName" type="text" placeholder="请输入您的称呼" />' +
          '<div class="st-error" id="fbNameErr">请输入您的称呼</div>' +
        '</div>' +
        '<div class="fb-field">' +
          '<label class="fb-label" for="fbSource">您是通过什么方式了解到这个项目的？<span class="fb-req">*</span></label>' +
          '<div class="fb-select" data-fb-select>' +
            '<div class="fb-select__trigger" tabindex="0">' +
              '<span class="fb-select__value is-placeholder">请选择</span>' +
              '<span class="fb-select__arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg></span>' +
            '</div>' +
            '<input type="hidden" id="fbSource" value="" />' +
            '<div class="fb-select__dropdown">' +
              '<div class="fb-select__option" data-value="简历链接">简历链接</div>' +
              '<div class="fb-select__option" data-value="他人推荐">他人推荐</div>' +
              '<div class="fb-select__option" data-value="搜索">搜索</div>' +
              '<div class="fb-select__option" data-value="其他">其他</div>' +
            '</div>' +
          '</div>' +
          '<div class="st-error" id="fbSourceErr">请选择了解方式</div>' +
          '<div class="fb-nest" id="fbSourceNest" style="display:none">' +
            '<label class="fb-label fb-nest__label" for="fbSourceOther">请简单说明<span class="fb-req">*</span></label>' +
            '<input class="st-input fb-input" id="fbSourceOther" type="text" placeholder="请输入您了解到该项目的方式" />' +
            '<div class="st-error" id="fbSourceOtherErr">请填写说明</div>' +
          '</div>' +
        '</div>' +
        '<div class="fb-field">' +
          '<label class="fb-label">如何联系您<span class="fb-opt">(选填)</span></label>' +
          '<div class="fb-contact">' +
            '<div class="fb-select fb-contact__type" data-fb-select>' +
              '<div class="fb-select__trigger" tabindex="0">' +
                '<span class="fb-select__value is-placeholder">选择类型</span>' +
                '<span class="fb-select__arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg></span>' +
              '</div>' +
              '<input type="hidden" id="fbContactType" value="" />' +
              '<div class="fb-select__dropdown">' +
                '<div class="fb-select__option" data-value="微信">微信</div>' +
                '<div class="fb-select__option" data-value="电话">电话</div>' +
                '<div class="fb-select__option" data-value="邮箱">邮箱</div>' +
                '<div class="fb-select__option" data-value="其他">其他</div>' +
              '</div>' +
            '</div>' +
            '<input class="st-input fb-input fb-contact__input" id="fbContact" type="text" placeholder="请输入联系方式" />' +
          '</div>' +
        '</div>' +
        '<div class="fb-field">' +
          '<label class="fb-label" for="fbOpinion">您的意见或建议<span class="fb-opt">(选填)</span></label>' +
          '<div class="fb-textarea-wrap">' +
            '<textarea class="st-input fb-textarea" id="fbOpinion" maxlength="1000" placeholder="欢迎告诉我们你的使用感受、遇到的问题，或任何希望改进的地方。"></textarea>' +
            '<span class="fb-count" id="fbCount">0 / 1000</span>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="fb-modal__foot">' +
        '<button class="st-btn st-btn--cancel" data-st-x type="button">取消</button>' +
        '<button class="st-btn st-btn--primary" id="fbSubmit" type="button" disabled>提交反馈</button>' +
      '</div>' +
      '<div class="fb-success">' +
        '<div class="fb-success__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg></div>' +
        '<div class="fb-success__title">感谢你的反馈</div>' +
        '<div class="fb-success__desc">非常感谢您的意见与建议。我已经收到您的问卷，我会仔细认真阅读每一条反馈。</div>' +
        '<button class="fb-success__btn" id="fbDone" type="button">完成</button>' +
      '</div>' +
    '</div>';
  }
  function initCustomSelect(wrap, onChange) {
    var trigger = wrap.querySelector('.fb-select__trigger');
    var valueEl = wrap.querySelector('.fb-select__value');
    var dropdown = wrap.querySelector('.fb-select__dropdown');
    var hidden = wrap.querySelector('input[type=hidden]');
    var options = Array.prototype.slice.call(wrap.querySelectorAll('.fb-select__option'));
    var savedParent = null, savedNext = null;
    function restoreDropdown() {
      if (!savedParent || dropdown.parentNode === savedParent) return;
      if (savedNext && savedNext.parentNode === savedParent) {
        savedParent.insertBefore(dropdown, savedNext);
      } else {
        savedParent.appendChild(dropdown);
      }
    }
    function close() {
      wrap.classList.remove('is-open');
      dropdown.classList.remove('is-open');
      dropdown.style.top = ''; dropdown.style.left = ''; dropdown.style.width = '';
      restoreDropdown();
      if (window.__fbOpenSelect === wrap) window.__fbOpenSelect = null;
    }
    function position() {
      var r = trigger.getBoundingClientRect();
      dropdown.style.width = r.width + 'px';
      dropdown.style.left = r.left + 'px';
      var dh = dropdown.offsetHeight || 0;
      if (r.bottom + 8 + dh > window.innerHeight && r.top - 8 - dh > 0) {
        dropdown.style.top = (r.top - dh - 4) + 'px';
      } else {
        dropdown.style.top = (r.bottom + 4) + 'px';
      }
    }
    function open() {
      if (wrap.classList.contains('is-open')) { close(); return; }
      if (window.__fbOpenSelect && window.__fbOpenSelect !== wrap) window.__fbOpenSelect.__close();
      savedParent = dropdown.parentNode;
      savedNext = dropdown.nextSibling;
      document.body.appendChild(dropdown);
      wrap.classList.add('is-open');
      dropdown.classList.add('is-open');
      window.__fbOpenSelect = wrap;
      position();
    }
    wrap.__close = close;
    trigger.addEventListener('click', function (e) { e.stopPropagation(); open(); });
    options.forEach(function (opt) {
      opt.addEventListener('click', function (e) {
        e.stopPropagation();
        var val = opt.getAttribute('data-value');
        hidden.value = val;
        valueEl.textContent = opt.textContent;
        valueEl.classList.remove('is-placeholder');
        options.forEach(function (o) { o.classList.remove('is-selected'); });
        opt.classList.add('is-selected');
        close();
        if (onChange) onChange(val);
        hidden.dispatchEvent(new Event('change'));
      });
    });
    document.addEventListener('click', function (e) {
      if (!wrap.classList.contains('is-open')) return;
      if (wrap.contains(e.target) || dropdown.contains(e.target)) return;
      close();
    });
    var body = document.querySelector('.fb-modal__body');
    if (body) body.addEventListener('scroll', function () { if (wrap.classList.contains('is-open')) close(); }, true);
    window.addEventListener('resize', function () { if (wrap.classList.contains('is-open')) close(); });
  }
  function bindFeedbackForm(root) {
    var nameEl = root.querySelector('#fbName');
    var sourceEl = root.querySelector('#fbSource');
    var sourceNest = root.querySelector('#fbSourceNest');
    var sourceOther = root.querySelector('#fbSourceOther');
    var contactType = root.querySelector('#fbContactType');
    var contactInput = root.querySelector('#fbContact');
    var opinion = root.querySelector('#fbOpinion');
    var count = root.querySelector('#fbCount');
    var submitBtn = root.querySelector('#fbSubmit');
    var modal = root.querySelector('#fbModal');
    function clearError(el) {
      el.classList.remove('is-error');
      var f = el.closest('.fb-field');
      if (f) f.querySelectorAll('.st-error').forEach(function (e) { e.classList.remove('is-show'); });
    }
    function setError(el, errId) {
      el.classList.add('is-error');
      var e = root.querySelector('#' + errId);
      if (e) e.classList.add('is-show');
    }
    function checkValid() {
      if (!nameEl.value.trim()) return false;
      if (!sourceEl.value) return false;
      if (sourceEl.value === '其他' && !sourceOther.value.trim()) return false;
      return true;
    }
    function refresh() { submitBtn.disabled = !checkValid(); }
    opinion.addEventListener('input', function () {
      count.textContent = opinion.value.length + ' / 1000';
      refresh();
    });
    sourceEl.addEventListener('change', function () {
      sourceNest.style.display = (sourceEl.value === '其他') ? 'block' : 'none';
      if (sourceEl.value !== '其他') { sourceOther.value = ''; clearError(sourceOther); }
      clearError(sourceEl);
      refresh();
    });
    var PH = { '邮箱': '请输入邮箱地址', '微信': '请输入微信号', '电话': '请输入电话号码', '其他': '请输入联系方式，并注明平台' };
    contactType.addEventListener('change', function () {
      contactInput.placeholder = PH[contactType.value] || '请输入联系方式';
      refresh();
    });
    [nameEl, sourceOther, contactInput].forEach(function (el) {
      el.addEventListener('input', function () { clearError(el); refresh(); });
    });
    root.querySelectorAll('[data-st-x]').forEach(function (b) {
      b.addEventListener('click', function () { closeModal(); });
    });
    submitBtn.addEventListener('click', function () {
      if (submitBtn.disabled) return;
      var firstBad = null;
      if (!nameEl.value.trim()) { setError(nameEl, 'fbNameErr'); if (!firstBad) firstBad = nameEl; }
      if (!sourceEl.value) { setError(sourceEl, 'fbSourceErr'); if (!firstBad) firstBad = sourceEl; }
      if (sourceEl.value === '其他' && !sourceOther.value.trim()) { setError(sourceOther, 'fbSourceOtherErr'); if (!firstBad) firstBad = sourceOther; }
      if (firstBad) { firstBad.scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }
      submitBtn.disabled = true;
      submitBtn.textContent = '提交中…';
      var fbSourceVal = sourceEl.value === '其他' ? ('其他：' + sourceOther.value.trim()) : sourceEl.value;
      logFeedback({
        name: nameEl.value.trim(),
        source: fbSourceVal,
        contact_type: contactType.value === '其他' ? ('其他：' + contactInput.value.trim()) : contactType.value,
        contact: contactInput.value.trim() || '',
        content: opinion.value.trim() || ''
      }).then(function () {
        if (server && server.log_feedback_behavior) {
          server.log_feedback_behavior({ user_id: VISITOR_ID }).catch(function () {});
        }
      });
      setTimeout(function () { modal.classList.add('is-success'); try { localStorage.setItem('fip_fb_submitted', '1'); } catch (e) {} }, 500);
    });
    var doneBtn = root.querySelector('#fbDone');
    if (doneBtn) doneBtn.addEventListener('click', function () { closeModal(true); });
    root.querySelectorAll('.fb-select').forEach(function (w) { initCustomSelect(w, null); });
    refresh();
  }
  function feedbackAction() {
    logBehavior(BEHAVIOR_FEEDBACK, '打开问卷');
    closePanel(true);
    openModal({
      returnToPanel: false,
      boxClass: 'st-modal__box--feedback',
      html: feedbackFormHtml(),
      onMount: bindFeedbackForm
    });
  }

  /* ===== 反馈引导：累计停留 3 分钟出现，箭头气泡指向左下角设置图，可直接弹问卷 ===== */
  var FB_GUIDE_KEY_MS = 'fip_fb_active_ms';
  var FB_GUIDE_KEY_SUBMITTED = 'fip_fb_submitted';
  var FB_GUIDE_KEY_PROMPTED = 'fip_fb_prompted';
  var GUIDE_THRESHOLD_MS = 3 * 60 * 1000;
  var GUIDE_COOLDOWN_MS = 3 * 24 * 60 * 60 * 1000;
  var GUIDE_TICK_MS = 5000;
  var guideShownThisSession = false;
  var guideEl = null;
  function fbGuideNum(key) { var v = parseInt(localStorage.getItem(key), 10); return isNaN(v) ? 0 : v; }
  function fbGuideShouldShow() {
    if (guideShownThisSession) return false;
    if (localStorage.getItem(FB_GUIDE_KEY_SUBMITTED) === '1') return false;
    var p = localStorage.getItem(FB_GUIDE_KEY_PROMPTED);
    if (p === 'never') return false;
    if (p && (Date.now() - parseInt(p, 10) < GUIDE_COOLDOWN_MS)) return false;
    if (fbGuideNum(FB_GUIDE_KEY_MS) < GUIDE_THRESHOLD_MS) return false;
    if (st.modalOpen || st.panelOpen) return false;
    if (document.querySelector('.fb-guide')) return false;
    return true;
  }
  function fbGuidePosition() {
    if (!guideEl) return;
    var anchor = document.querySelector('.left-footer');
    var r = anchor ? anchor.getBoundingClientRect() : null;
    var bubble = guideEl.querySelector('.fb-guide__bubble');
    var bw = bubble ? bubble.offsetWidth : 240;
    if (!r || r.width === 0) {
      guideEl.style.left = '16px';
      guideEl.style.bottom = '16px';
    } else {
      var left = r.left + 8;
      if (left + bw > window.innerWidth - 8) left = window.innerWidth - bw - 8;
      if (left < 8) left = 8;
      var bottom = (window.innerHeight - r.top) + 8;
      guideEl.style.left = left + 'px';
      guideEl.style.bottom = bottom + 'px';
    }
  }
  function fbGuideHide() {
    window.__fipGuideActive = false;
    if (guideEl && guideEl.parentNode) guideEl.parentNode.removeChild(guideEl);
    guideEl = null;
  }
  function fbGuideShow() {
    if (!fbGuideShouldShow()) return;
    guideShownThisSession = true;
    window.__fipGuideActive = true;
    guideEl = document.createElement('div');
    guideEl.className = 'fb-guide';
    guideEl.innerHTML =
      '<div class="fb-guide__arrow"></div>' +
      '<div class="fb-guide__bubble">' +
        '<button class="fb-guide__close" data-fbg="close" aria-label="不再提示">×</button>' +
        '<div class="fb-guide__img"><img src="/gradio_api/file=asset/questionnaire.jpg" alt="问卷"></div>' +
        '<div class="fb-guide__body">' +
          '<div class="fb-guide__title">请给我一些建议反馈吧~</div>' +
          '<div class="fb-guide__actions">' +
            '<button class="fb-guide__btn fb-guide__btn--primary" data-fbg="go">去填写</button>' +
            '<button class="fb-guide__link" data-fbg="later">下次再说</button>' +
          '</div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(guideEl);
    fbGuidePosition();
    guideEl.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-fbg]');
      if (!btn) return;
      var act = btn.getAttribute('data-fbg');
      if (act === 'go') { fbGuideHide(); feedbackAction(); }
      else if (act === 'later') { try { localStorage.setItem(FB_GUIDE_KEY_PROMPTED, String(Date.now())); } catch (e) {} fbGuideHide(); }
      else if (act === 'close') { try { localStorage.setItem(FB_GUIDE_KEY_PROMPTED, 'never'); } catch (e) {} fbGuideHide(); }
    });
  }
  function initFeedbackGuide() {
    var lastTick = Date.now();
    function flush() {
      var now = Date.now();
      var delta = now - lastTick;
      if (delta > 0) {
        var cur = fbGuideNum(FB_GUIDE_KEY_MS) + delta;
        try { localStorage.setItem(FB_GUIDE_KEY_MS, String(cur)); } catch (e) {}
      }
      lastTick = now;
    }
    setInterval(function () {
      if (document.visibilityState === 'visible') flush();
      else lastTick = Date.now();
      if (document.visibilityState === 'visible' && fbGuideShouldShow()) fbGuideShow();
    }, GUIDE_TICK_MS);
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') flush();
      else lastTick = Date.now();
    });
    window.addEventListener('beforeunload', flush);
    window.addEventListener('resize', fbGuidePosition);
  }

  function bridgeAction(target) {
    if (target === st.bridgeMode) return;
    var fromLabel = st.bridgeMode === 'neo4j' ? 'Neo4j·联网' : 'NetworkX·本地';
    var toLabel = target === 'neo4j' ? 'Neo4j·联网' : 'NetworkX·本地';
    closePanel(true);
    openModal({
      returnToPanel: true,
      html: confirmHtml('切换服务端桥接方案？', '当前：' + fromLabel + '　→　目标：' + toLabel, '确认切换', 'Neo4j·联网模式下的数据更新更及时，但需要VPN环境'),
      onMount: function (root) {
        root.querySelector('[data-st-x]').addEventListener('click', closeModal);
        root.querySelector('[data-st-ok]').addEventListener('click', function () {
          st.bridgeMode = target;
          window.dispatchEvent(new CustomEvent('backendchange'));
          renderBridge();
          closeModal(true);
          showToast('已切换至 ' + toLabel, 'success');
        });
      }
    });
  }
  function clearAction() {
    closePanel(true);
    openModal({
      returnToPanel: true,
      html: confirmHtml('删除全部对话？', '将删除所有对话（含默认对话），此操作无法撤销。', '确认删除'),
      onMount: function (root) {
        root.querySelector('[data-st-x]').addEventListener('click', closeModal);
        root.querySelector('[data-st-ok]').addEventListener('click', function () {
          closeModal(true);
          /* 真实清空逻辑在 IIFE #1 的 bindChat 作用域内实现（可访问内存态 conversations / localStorage / resetChat），
             通过 window.__fipClearConversations 暴露给设置面板（IIFE #2）调用 */
          if (window.__fipClearConversations) window.__fipClearConversations();
          showToast('已删除全部对话', 'success');
        });
      }
    });
  }
  function passwordAction(action, desc) {
    st.pwdAction = action;
    closePanel(true);
    openModal({
      returnToPanel: true,
      boxClass: 'st-modal__box--password',
      html: passwordHtml(desc),
      onMount: function (root) {
        var input = root.querySelector('#stPwdInput');
        var eye = root.querySelector('#stPwdEye');
        var err = root.querySelector('#stPwdError');
        var cont = root.querySelector('#stPwdContinue');
        var cancel = root.querySelector('#stPwdCancel');
        if (input) input.focus();
        input.addEventListener('input', function () {
          cont.disabled = input.value.length === 0;
          err.classList.remove('is-show');
          input.classList.remove('is-error');
        });
        eye.addEventListener('click', function () {
          var show = input.type === 'password';
          input.type = show ? 'text' : 'password';
          eye.innerHTML = show ? ICONS.eyeOff : ICONS.eye;
          input.focus();
        });
        cancel.addEventListener('click', closeModal);
        cont.addEventListener('click', function () {
          var raw = input.value;
          if (!raw) return;
          cont.disabled = true;
          err.classList.remove('is-show');
          input.classList.remove('is-error');
          hashPwdEquals(raw).then(function (ok) {
            cont.disabled = false;
            if (!ok) {
              err.classList.add('is-show');
              input.classList.add('is-error');
              return;
            }
            if (action === 'unwatermark') {
            replaceModalContent(
              confirmHtml('确认去除水印？', '操作后将移除页面水印，并解除图数据库 / 文献库 / 设计说明的复制限制，此操作无法撤销。', '确认去水印'),
              function (r2) {
                r2.querySelector('[data-st-x]').addEventListener('click', closeModal);
                r2.querySelector('[data-st-ok]').addEventListener('click', function () {
                  closeModal(true);
                  setWatermarked(false);
                  showToast('已去除水印', 'success');
                });
              }
            );
          } else if (action === 'logs') {
            closeModal(true);
            window.open('https://my.feishu.cn/base/ZTt8blhVXa5ea3sjOvecpPc7nQg?table=tbl2CVrC6jQiNAWa&view=vewUMsj5mX', '_blank');
          }
          });
        });
      }
    });
  }

  /* ===== 隐私保护：默认水印 + iframe 禁复制（主页/对话始终可复制；去水印为一次性密码操作） ===== */
  var WM_TEXT = '潘页冰 个人MVP项目';
  var PRIVACY_KEY = 'fip_privacy';
  var wmEl = null;

  function buildWatermarkBg() {
    var svg = "<svg xmlns='http://www.w3.org/2000/svg' width='260' height='150'>" +
      "<text x='8' y='82' font-family='sans-serif' font-size='15' fill='rgba(62,56,54,0.10)' transform='rotate(-28 130 75)'>" +
      WM_TEXT + "</text></svg>";
    return 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '")';
  }

  function setWatermark(on) {
    if (on) {
      if (!wmEl) {
        wmEl = document.createElement('div');
        wmEl.className = 'st-watermark';
        wmEl.style.backgroundImage = buildWatermarkBg();
        document.body.appendChild(wmEl);
      }
    } else if (wmEl) {
      wmEl.remove();
      wmEl = null;
    }
  }

  function guardHandler(e) {
    var t = e.target;
    if (t && t.closest && t.closest('input,textarea')) return; /* 放行输入控件 */
    e.preventDefault();
  }

  /* iframe 内注入/撤销禁复制：iframe 不继承父 CSS，必须 JS 直接设 inline style + 事件监听（同源 srcdoc 可访问 contentDocument） */
  function attachIframeGuard(iframe) {
    if (!iframe) return;
    function apply(on) {
      try {
        var idoc = iframe.contentDocument;
        if (!idoc) return;
        var ib = idoc.body;
        if (!ib) return;
        if (on) {
          if (idoc.__stGuardWired) return;
          idoc.__stGuardWired = true;
          ib.style.userSelect = 'none';
          ib.style.webkitUserSelect = 'none';
          ib.addEventListener('copy', guardHandler);
          ib.addEventListener('cut', guardHandler);
          ib.addEventListener('contextmenu', guardHandler);
          ib.addEventListener('selectstart', guardHandler);
        } else {
          if (!idoc.__stGuardWired) return;
          idoc.__stGuardWired = false;
          ib.style.userSelect = '';
          ib.style.webkitUserSelect = '';
          ib.removeEventListener('copy', guardHandler);
          ib.removeEventListener('cut', guardHandler);
          ib.removeEventListener('contextmenu', guardHandler);
          ib.removeEventListener('selectstart', guardHandler);
        }
      } catch (err) {}
    }
    if (iframe.__stGuardAttached) { apply(st.watermarked); return; }
    iframe.__stGuardAttached = true;
    if (iframe.contentDocument && iframe.contentDocument.readyState === 'complete') apply(st.watermarked);
    iframe.addEventListener('load', function () { apply(st.watermarked); });
  }

  function savePrivacy() {
    try {
      localStorage.setItem(PRIVACY_KEY, JSON.stringify({ watermarked: st.watermarked }));
    } catch (e) {}
  }

  /* 水印 + iframe 禁复制 统一开关（一次性去水印：on=false 后持久化并隐藏去水印按钮，无恢复入口） */
  function setWatermarked(on) {
    st.watermarked = on;
    setWatermark(on);
    ['pageGraph', 'pageDocs', 'pageDesign', 'styleDemoFrame', 'designExpandFrame'].forEach(function (id) {
      var f = document.getElementById(id);
      if (f) attachIframeGuard(f);
    });
    savePrivacy();
    if (!on) {
      var uw = settingsEl.querySelector('[data-st-action="unwatermark"]');
      if (uw) uw.style.display = 'none';
    }
  }

  function loadPrivacy() {
    try {
      var raw = localStorage.getItem(PRIVACY_KEY);
      if (raw) {
        var s = JSON.parse(raw);
        if (typeof s.watermarked === 'boolean') st.watermarked = s.watermarked;
      }
    } catch (e) {}
    setWatermark(st.watermarked);
    ['pageGraph', 'pageDocs', 'pageDesign', 'styleDemoFrame', 'designExpandFrame'].forEach(function (id) {
      var f = document.getElementById(id);
      if (f) attachIframeGuard(f);
    });
    if (!st.watermarked) {
      var uw = settingsEl.querySelector('[data-st-action="unwatermark"]');
      if (uw) uw.style.display = 'none';
    }
  }

  /* ---------- 绑定 ---------- */
  /* ====== 左下角 APNG 队列播放（canvas 渲染，无缝切换） ====== */
  var CRC_TABLE = (function(){ var t=[]; for(var n=0;n<256;n++){ var c=n; for(var k=0;k<8;k++) c=(c&1)?(0xEDB88320^(c>>>1)):(c>>>1); t[n]=c>>>0; } return t; })();
  function crc32(bytes){ var c=0xFFFFFFFF; for(var i=0;i<bytes.length;i++) c=CRC_TABLE[(c^bytes[i])&0xFF]^(c>>>8); return (c^0xFFFFFFFF)>>>0; }

  /* 解析 APNG：提取 IHDR/acTL/PLTE 与各帧 fcTL+数据，逐帧重组成浏览器可解码的独立 PNG */
  function parseAPNG(buf){
    var SIG=[137,80,78,71,13,10,26,10];
    for(var i=0;i<8;i++) if(buf[i]!==SIG[i]) throw new Error('not png');
    function rd32(o){ return ((buf[o]<<24)|(buf[o+1]<<16)|(buf[o+2]<<8)|buf[o+3])>>>0; }
    function rd16(o){ return (buf[o]<<8)|buf[o+1]; }
    function str(o,n){ var s=''; for(var k=0;k<n;k++) s+=String.fromCharCode(buf[o+k]); return s; }
    var p=8, ihdr=null, plte=null, trns=null, actl=null, frames=[], fctl=null;
    /* fcTL 数据布局（含 4 字节序列号）：seq(4) w(4) h(4) xoff(4) yoff(4) delay_num(2) delay_den(2) dispose(1) blend(1) */
    function fc(o){ var nm=rd16(o+20), dn=rd16(o+22)||100; return { w:rd32(o+4), h:rd32(o+8), x:rd32(o+12), y:rd32(o+16), delay:(dn>0?(nm/dn*1000):0)||100, dispose:buf[o+24], blend:buf[o+25] }; }
    while(p<buf.byteLength){
      var len=rd32(p), type=str(p+4,4), ds=p+8, de=p+8+len;
      if(type==='IHDR') ihdr={ w:rd32(ds), h:rd32(ds+4), bd:buf[ds+8], ct:buf[ds+9] };
      else if(type==='PLTE') plte=buf.slice(ds,de);
      else if(type==='tRNS') trns=buf.slice(ds,de);
      else if(type==='acTL') actl={ num:rd32(ds), plays:rd32(ds+4) };
      else if(type==='fcTL') fctl=fc(ds);
      else if(type==='IDAT'){ if(fctl){ frames.push({fctl:fctl, parts:[]}); fctl=null; } if(frames.length) frames[frames.length-1].parts.push(buf.slice(ds,de)); }
      else if(type==='fdAT'){ var fd=buf.slice(ds+4,de); if(fctl){ frames.push({fctl:fctl, parts:[fd]}); fctl=null; } else if(frames.length) frames[frames.length-1].parts.push(fd); }
      p=de+4;
    }
    if(!actl) throw new Error('not apng (no acTL)');
    if(!frames.length) throw new Error('no frames');
    var SIGU=new Uint8Array(SIG);
    function chunk(t,d){ var out=new Uint8Array(8+d.byteLength+4); out[0]=(d.byteLength>>>24)&255; out[1]=(d.byteLength>>>16)&255; out[2]=(d.byteLength>>>8)&255; out[3]=d.byteLength&255; for(var k=0;k<4;k++) out[4+k]=t.charCodeAt(k); out.set(d,8); var c=crc32(out.subarray(4,8+d.byteLength)); out[8+d.byteLength]=(c>>>24)&255; out[8+d.byteLength+1]=(c>>>16)&255; out[8+d.byteLength+2]=(c>>>8)&255; out[8+d.byteLength+3]=c&255; return out; }
    function framePNG(fr){ var f=fr.fctl; var ih=new Uint8Array(13); ih[0]=(f.w>>>24)&255; ih[1]=(f.w>>>16)&255; ih[2]=(f.w>>>8)&255; ih[3]=f.w&255; ih[4]=(f.h>>>24)&255; ih[5]=(f.h>>>16)&255; ih[6]=(f.h>>>8)&255; ih[7]=f.h&255; ih[8]=ihdr.bd; ih[9]=ihdr.ct; ih[10]=0; ih[11]=0; ih[12]=0; var total=0; fr.parts.forEach(function(pt){ total+=pt.byteLength; }); var idat=new Uint8Array(total); var o=0; fr.parts.forEach(function(pt){ idat.set(pt,o); o+=pt.byteLength; }); var parts=[chunk('IHDR',ih)]; if(plte) parts.push(chunk('PLTE',plte)); if(trns) parts.push(chunk('tRNS',trns)); parts.push(chunk('IDAT',idat)); parts.push(chunk('IEND',new Uint8Array(0))); var sz=SIGU.length; parts.forEach(function(c){ sz+=c.byteLength; }); var out=new Uint8Array(sz); var p2=0; out.set(SIGU,p2); p2+=SIGU.length; parts.forEach(function(c){ out.set(c,p2); p2+=c.byteLength; }); return new Blob([out],{type:'image/png'}); }
    return Promise.all(frames.map(function(fr){ var url=URL.createObjectURL(framePNG(fr)); return new Promise(function(res,rej){ var im=new Image(); im.onload=function(){ res({img:im,w:fr.fctl.w,h:fr.fctl.h,x:fr.fctl.x,y:fr.fctl.y,delay:fr.fctl.delay,dispose:fr.fctl.dispose,blend:fr.fctl.blend}); }; im.onerror=function(){ rej(new Error('frame fail')); }; im.src=url; }); })).then(function(imgs){ return { w:ihdr.w, h:ihdr.h, imgs:imgs }; });
  }

  /* 左下角：静止 left_bottom.jpg；hover 播放 start(1次)→progress(循环)；离开等当前轮播完再播 end(1次)。APNG 读取失败兜底 left_bottom_2.jpg */
  function installLeftFooterAnim(lfEl){
    var ASSET='/gradio_api/file=asset/';
    /* 素材每帧延迟被设成 400ms（start/progress），逐帧停顿式播放观感很卡。
       这里把每帧绘制间隔钳制到一个固定上限，让 37 帧在约 1.9s 内干脆播完。 */
    var FRAME_DELAY_CAP_MS = 50;
    var START_URL=ASSET+'left_bottom_start.png';
    var PROG_URL=ASSET+'left_bottom_progress.png';
    var END_URL=ASSET+'left_bottom_end.png';
    var FALLBACK=ASSET+'left_bottom_2.jpg';
    var canvas=lfEl.querySelector('.lf-canvas');
    var img=lfEl.querySelector('.lf-img');
    if(!canvas) return;
    var ctx=canvas.getContext('2d');
    var cache={}, decoding={}, apngOk=true, state='idle', pendingEnd=false, runId=0, timers=[];
    function clearTimers(){ timers.forEach(clearTimeout); timers=[]; }
    function later(fn,ms){ var t=setTimeout(fn,ms); timers.push(t); return t; }
    function showCanvas(){ lfEl.classList.add('is-anim'); }
    function hideCanvas(){ lfEl.classList.remove('is-anim'); clearTimers(); ctx.clearRect(0,0,canvas.width,canvas.height); }
    function fallback(){ lfEl.classList.remove('is-anim'); if(img && img.getAttribute('src')!==FALLBACK) img.src=FALLBACK; clearTimers(); state='idle'; }
    function getPlayer(url){
      if(cache[url]) return Promise.resolve(cache[url]);
      if(decoding[url]) return decoding[url];
      decoding[url]=fetch(url).then(function(r){ return r.arrayBuffer(); }).then(function(b){ return parseAPNG(new Uint8Array(b)); }).then(function(p){ cache[url]=p; return p; }).catch(function(e){ apngOk=false; throw e; });
      return decoding[url];
    }
    /* 逐帧按 APNG 规范合成到 canvas；loop 时 stopWhen() 为 true 则在当前轮边界停止 */
    function playPlayer(player, opts, myRun){
      clearTimers();
      canvas.width=player.w; canvas.height=player.h;
      var W=player.w, H=player.h, i=0, snapPrev=null;
      function render(){
        if(myRun!==runId) return;
        var fr=player.imgs[i];
        /* 先快照“本帧绘制前”的状态（供本帧 dispose=2 时还原） */
        var snapNow=document.createElement('canvas'); snapNow.width=W; snapNow.height=H; snapNow.getContext('2d').drawImage(canvas,0,0);
        /* 应用上一帧的 dispose_op */
        if(i>0){
          var pv=player.imgs[i-1], pd=pv.dispose;
          if(pd===1){ ctx.clearRect(pv.x,pv.y,pv.w,pv.h); }
          else if(pd===2){ if(snapPrev) ctx.drawImage(snapPrev,0,0); }
        } else { ctx.clearRect(0,0,W,H); }
        /* 应用本帧 blend_op 后绘制 */
        if(fr.blend===0){ ctx.clearRect(fr.x,fr.y,fr.w,fr.h); }
        ctx.drawImage(fr.img, fr.x, fr.y, fr.w, fr.h);
        snapPrev=snapNow;
        later(function(){
          if(myRun!==runId) return;
          i++;
          if(i>=player.imgs.length){ if(opts.loop && !(opts.stopWhen && opts.stopWhen())){ i=0; render(); } else { if(opts.onDone) opts.onDone(); } }
          else { render(); }
        }, Math.min(fr.delay, FRAME_DELAY_CAP_MS));
      }
      render();
    }
    function startSequence(){
      if(!apngOk){ fallback(); return; }
      var myRun=++runId; state='start';
      getPlayer(START_URL).then(function(p){
        if(myRun!==runId) return;
        if(pendingEnd){ playEnd(myRun); return; }
        showCanvas(); playPlayer(p,{loop:false,onDone:function(){ if(myRun!==runId) return; if(pendingEnd) playEnd(myRun); else playProgress(myRun); }}, myRun);
      }).catch(function(){ if(myRun===runId) fallback(); });
    }
    function playProgress(myRun){
      state='progress';
      getPlayer(PROG_URL).then(function(p){
        if(myRun!==runId) return;
        showCanvas(); playPlayer(p,{loop:true, stopWhen:function(){ return pendingEnd; }, onDone:function(){ if(myRun===runId) playEnd(myRun); }}, myRun);
      }).catch(function(){ if(myRun===runId) fallback(); });
    }
    function playEnd(myRun){
      state='end';
      getPlayer(END_URL).then(function(p){
        if(myRun!==runId) return;
        showCanvas(); playPlayer(p,{loop:false,onDone:function(){ if(myRun===runId){ hideCanvas(); state='idle'; } }}, myRun);
      }).catch(function(){ if(myRun===runId) fallback(); });
    }
    /* 预载 start+progress：首次 hover 即时播放，避免 jpg 空窗；任一失败则 apngOk=false 走兜底 left_bottom_2.jpg */
    getPlayer(START_URL);
    getPlayer(PROG_URL);
    lfEl.addEventListener('mouseenter', function(){ pendingEnd=false; if(state==='idle'||state==='end') startSequence(); });
    lfEl.addEventListener('mouseleave', function(){ pendingEnd=true; });
  }

  /* 右侧 hero：middle.jpg 静态兜底，视频 canplay 后切换循环播放；载入失败保留图片 */
  function installHeroVideo(){
    var wrap=document.querySelector('.hero-image'); if(!wrap) return;
    var video=wrap.querySelector('.hero-video'); if(!video) return;
    function showVideo(){ wrap.classList.add('video-on'); var pr=video.play(); if(pr&&pr.catch) pr.catch(function(){}); }
    video.addEventListener('canplay', showVideo, {once:true});
    video.addEventListener('loadeddata', showVideo, {once:true});
    video.addEventListener('error', function(){ wrap.classList.remove('video-on'); });
    if(video.readyState>=3) showVideo(); else { try { video.load(); } catch(e){} }
  }

  /* ===== APNG 动画备选（已注释；切回时：取消本块注释 + 把调用处 installHeroVideo() 改为 installHeroAnim()）=====
  function installHeroAnim(){
    var wrap=document.querySelector('.hero-image'); if(!wrap) return;
    var canvas=wrap.querySelector('.hero-canvas'); if(!canvas) return;
    var ctx=canvas.getContext('2d');
    var FRAME_DELAY_CAP_MS = 250;
    var APNG_URL='/gradio_api/file=asset/middle_hello.png';
    var runId=0, timers=[];
    function clearTimers(){ timers.forEach(clearTimeout); timers=[]; }
    function later(fn,ms){ var t=setTimeout(fn,ms); timers.push(t); return t; }
    function showCanvas(){ if(!wrap.classList.contains('video-on')) wrap.classList.add('video-on'); }
    function fallback(){ wrap.classList.remove('video-on'); clearTimers(); ctx.clearRect(0,0,canvas.width,canvas.height); }
    function play(player, myRun){
      clearTimers();
      canvas.width=player.w; canvas.height=player.h;
      var W=player.w, H=player.h, i=0, snapPrev=null;
      function render(){
        if(myRun!==runId) return;
        var fr=player.imgs[i];
        var snapNow=document.createElement('canvas'); snapNow.width=W; snapNow.height=H; snapNow.getContext('2d').drawImage(canvas,0,0);
        if(i>0){
          var pv=player.imgs[i-1], pd=pv.dispose;
          if(pd===1){ ctx.clearRect(pv.x,pv.y,pv.w,pv.h); }
          else if(pd===2){ if(snapPrev) ctx.drawImage(snapPrev,0,0); }
        } else { ctx.clearRect(0,0,W,H); }
        if(fr.blend===0){ ctx.clearRect(fr.x,fr.y,fr.w,fr.h); }
        ctx.drawImage(fr.img, fr.x, fr.y, fr.w, fr.h);
        snapPrev=snapNow;
        later(function(){
          if(myRun!==runId) return;
          i++;
          if(i>=player.imgs.length){ i=0; render(); } // 循环播放
          else { render(); }
        }, Math.min(fr.delay, FRAME_DELAY_CAP_MS));
      }
      render();
    }
    fetch(APNG_URL).then(function(r){ return r.arrayBuffer(); }).then(function(b){ return parseAPNG(new Uint8Array(b)); }).then(function(p){ showCanvas(); play(p, ++runId); }).catch(function(){ fallback(); });
  }
  ===== 结束 APNG 备选 ===== */

  function bindSettings() {
    /* 左下角媒体：静止态 left_bottom.jpg；hover 用 canvas 播放 APNG 队列（start→progress→end），失败兜底 left_bottom_2.jpg */
    var lfEl = document.querySelector('.left-footer');
    if (lfEl) {
      installLeftFooterAnim(lfEl);
      lfEl.addEventListener('click', openPanel);
    }
    /* 右侧 hero：middle.jpg 静态兜底，视频 canplay 后切换循环播放 */
    installHeroVideo();
    /* 收起态左下角设置入口：点击展开设置面板（面板定位已自动锚定到收起侧栏） */
    var collapsedSettingsBtn = document.getElementById('collapsedSettingsBtn');
    if (collapsedSettingsBtn) collapsedSettingsBtn.addEventListener('click', openPanel);

    settingsEl.addEventListener('click', function (e) {
      if (e.target.closest('[data-st-settings-close]')) { closePanel(); return; }
      var item = e.target.closest('[data-st-action]');
      if (!item) return;
      var action = item.getAttribute('data-st-action');
      if (action === 'feedback') feedbackAction();
      else if (action === 'clear') clearAction();
      else if (action === 'unwatermark') passwordAction('unwatermark', '此操作需要验证身份，请输入密码后继续。');
      else if (action === 'logs') passwordAction('logs', '查看运行日志需要进行身份验证。');
    });
    var fbCard = settingsEl.querySelector('.st-feedback-card');
    if (fbCard) {
      fbCard.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); feedbackAction(); }
      });
    }

    if (bridgeEl) {
      bridgeEl.addEventListener('click', function (e) {
        var opt = e.target.closest('[data-st-bridge]');
        if (!opt) return;
        bridgeAction(opt.getAttribute('data-st-bridge'));
      });
    }

    modalEl.addEventListener('click', function (e) {
      if (e.target.closest('[data-st-overlay]')) closeModal();
    });

    document.addEventListener('click', function (e) {
      if (!st.panelOpen) return;
      if (e.target.closest && e.target.closest('.st-settings')) return;
      if (e.target.closest && e.target.closest('.st-modal')) return;
      if (e.target.closest && e.target.closest('.left-footer')) return;
      if (e.target.closest && e.target.closest('#collapsedSettingsBtn')) return;
      closePanel();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        if (st.modalOpen) closeModal();
        else if (st.panelOpen) closePanel();
      }
    });

    /* iframe 内点击无法冒泡到父 document，故需在 iframe 内部挂监听以关闭面板 */
    function attachIframeClose(iframe) {
      if (!iframe) return;
      function wire() {
        try {
          var idoc = iframe.contentDocument;
          if (!idoc || idoc.__stCloseWired) return;
          idoc.__stCloseWired = true;
          idoc.addEventListener('click', function () {
            if (st.panelOpen) closePanel();
          });
        } catch (err) {}
      }
      if (iframe.contentDocument && iframe.contentDocument.readyState === 'complete') wire();
      iframe.addEventListener('load', wire);
    }
    ['pageGraph', 'pageDocs', 'pageDesign'].forEach(function (id) {
      attachIframeClose(document.getElementById(id));
    });

    window.addEventListener('resize', function () { if (st.panelOpen) positionPanel(); });
    renderBridge();
    loadPrivacy(); /* 应用持久化的隐私保护状态（水印 + 禁复制 + iframe 注入） */
    initFeedbackGuide(); /* 反馈引导：累计停留超 3 分钟后箭头气泡提示填写问卷 */
  }

  bindSettings();
})();
"""

_GRADIO_CSS = """/* ============================================================
   全局容器重置：彻底去除 Gradio 外层容器带来的边距/圆角/阴影
   ============================================================ */
html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  height: 100% !important;
  background: #FDFCFA !important;
  overflow: hidden;
}
gradio-app { display: block !important; width: 100% !important; height: 100% !important; }
#root { height: 100% !important; }
.gradio-container, .contain, .wrap, .block, form, .main, .panel {
  padding: 0 !important;
  margin: 0 !important;
  max-width: none !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: transparent !important;
}
/* 包裹 app-shell 的容器（Gradio 生成的 div）也清零 */
div:has(> .app-shell) { padding: 0 !important; margin: 0 !important; background: #FDFCFA !important; }

/* ============================================================
   Design Tokens — 用户校准色值（:root + .app-shell 双保险）
   ============================================================ */
:root {
  --p-900: #6B5045;
  --p-700: #B37560;
  --p-500: #C7A18E;
  --p-100: #FEFAF7;
  --n-text: #3E3836;
  --n-text-sec: #6F6763;
  --n-border: #F8F1EB;
  --n-surface: #FDFCFA;
  --n-card: #FCFBF9;
  --n-header: #FFF9F5;
  --warm-gray: #A89F93;
  --shadow: rgba(62, 56, 54, 0.08);
  --r-sm: 6px;
  --r-md: 12px;
  --r-lg: 16px;
  --r-pill: 999px;
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  /* 设置功能设计令牌（作用域为顶层浮层，不依赖 .app-shell） */
  --st-surface: #FFFFFF;
  --st-border: #EDE5DD;
  --st-hover: #FAF3EC;
  --st-text: #3E3836;
  --st-text2: #6F6763;
  --st-primary: #8C6B5D;
  --st-primary-hover: #6B5045;
  --st-focus: #8C6B5D;
  --st-error: #B86B5B;
  --st-error-hover: #9C5547;
  --st-disabled-bg: #EDE5DD;
  --st-disabled-text: #A9A19C;
  --st-page: #FDFBF7;
  --st-success: #6F8A6A;
  --st-info: #6D8795;
  --st-warning: #C38A35;
  --st-shadow-panel: 0 8px 24px rgba(62,56,54,0.10);
  --st-shadow-modal: 0 12px 32px rgba(62,56,54,0.14);
  --st-group: #8B817C;
  --st-seg-hover: #F5E9DF;
  --st-modal-bg: #FFFEFC;
  --st-success-bg: #F4F7F1;
  --st-select-active: #F4E7DD;
  --st-input-hover-border: #DCC9BC;
  --st-placeholder: #9A918C;
  --st-input-focus: #C7A18E;
  --st-nest-line: #F1E3D9;
}

.app-shell {
  --p-900: #6B5045;
  --p-700: #B37560;
  --p-500: #C7A18E;
  --p-100: #FEFAF7;
  --n-text: #3E3836;
  --n-text-sec: #6F6763;
  --n-border: #F8F1EB;
  --n-surface: #FDFCFA;
  --n-card: #FCFBF9;
  --n-header: #FFF9F5;
  --warm-gray: #A89F93;
  --shadow: rgba(62, 56, 54, 0.08);

  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", -apple-system, BlinkMacSystemFont, sans-serif;
  color: #3E3836;
  background: #FDFCFA;
  position: fixed;
  inset: 0;
  box-sizing: border-box;
}

.app-shell *, .app-shell *::before, .app-shell *::after { box-sizing: border-box; }

/* 按钮重置 + 对抗 Gradio 主题（高优先级 + !important） */
.app-shell button {
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  color: inherit;
}

/* 通用图标按钮 */
.icon-btn {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #6F6763;
  background: transparent !important;
  padding: 0 !important;
  transition: background 150ms var(--ease), color 150ms var(--ease);
  flex-shrink: 0;
}
.icon-btn svg, .collapsed-tool svg, .refresh-btn svg, .send-btn svg { display: inline-block !important; }
.icon-btn:hover { background: #F9F1E9 !important; color: #6B5045; }

/* ============================================================
   左侧边栏（暖杏 #F9F1E9，贴边全高）
   ============================================================ */
.left-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #FEFAF7 !important;
  border-right: 1px solid #F1E4D5;
  display: flex;
  flex-direction: column;
  transition: width 280ms var(--ease), transform 300ms var(--ease);
  position: relative;
  z-index: 30;
  overflow: hidden;
}

.sidebar-content {
  width: 240px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px 14px 10px;
  box-sizing: border-box;
  opacity: 1;
  transition: opacity 180ms var(--ease);
}

/* 顶部 Header：flex-start 让折叠按钮顶部与 logo 顶部对齐（都=16px，即 sidebar padding-top）；
   此前 align-items:center 使 30px 按钮在 40px header 内居中，顶部落在 21px，比右侧图标低 5px */
.left-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
.brand { display: flex; align-items: center; gap: 10px; min-width: 0; cursor: pointer; }
.brand-logo { width: 40px; height: 40px; border-radius: 999px; object-fit: cover; box-shadow: 0 1px 4px rgba(107, 80, 69, 0.15); }
/* 文本块固定 40px 高并垂直居中，使 .brand 总高 = logo 高(40px)，
   logo 在 align-items:center 下精确位于 padding-top 16px 处，与收起态一致 */
.brand-text { display: flex; flex-direction: column; justify-content: center; flex-shrink: 0; height: 40px; min-width: 0; }
.brand-title { font-size: 16px; font-weight: 600; color: #6B5045; line-height: 1.4; white-space: nowrap; }
.brand-subtitle { font-size: 12px; font-weight: 500; color: #6F6763; line-height: 1.4; margin-top: 2px; white-space: nowrap; }

/* 新建任务按钮（用户色 #B37560） */
.app-shell .primary-btn.new-task-btn {
  width: 100%;
  height: 38px;
  border-radius: 10px;
  background: #B37560 !important;
  color: #FFFFFF !important;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-bottom: 14px;
  border: 1px solid rgba(255, 255, 255, 0.92) !important;
  box-shadow: 0 2px 8px rgba(179, 117, 96, 0.25), 0 1px 0 rgba(255, 255, 255, 0.25) inset;
  transition: background 150ms var(--ease), transform 80ms;
}
.app-shell .primary-btn.new-task-btn:hover { background: #9E5F4E !important; }
.app-shell .primary-btn.new-task-btn:active { transform: scale(0.98); }
.plus-icon { font-size: 16px; line-height: 1; font-weight: 400; }
.new-task-btn span { color: #FFFFFF !important; }

/* 导航菜单 */
.nav-menu {
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid #F1E4D5;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 0;
  border-radius: 10px;
  color: #3E3836;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.3;
  margin-bottom: 12px;
  text-decoration: none !important;
  transition: background 150ms var(--ease);
}
.nav-item:hover { background: #FAF3EC; color: #6B5045; }
.nav-item.active { color: #3E3836; font-weight: 600; background: #FAF3EC; box-shadow: none; }
/* 选中态与 hover 态完全一致，不再单独加深 */
.nav-icon { width: 18px; height: 18px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }

/* 分栏：固定总高度，条目过多时内部滚动，不顶走底部装饰图 */
.section {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  margin-bottom: 0;
}
.section-header { display: flex; align-items: center; justify-content: flex-start; gap: 6px; margin-bottom: 6px; padding: 0; flex-shrink: 0; }
.section-title { font-size: 12px; font-weight: 500; color: #A89F93 !important; line-height: 1.4; }
.section-count { font-size: 12px; font-weight: 500; color: #A89F93 !important; line-height: 1.4; }

.chat-list {
  list-style: none;
  margin: 0;
  padding: 0 !important;
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  /* 底部羽化：聊天条目接近装饰图时淡出，避免硬切 */
  -webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 calc(100% - 16px), transparent 100%);
          mask-image: linear-gradient(to bottom, #000 0%, #000 calc(100% - 16px), transparent 100%);
  /* Firefox：默认 20% 不透明，悬停侧边栏时提升为 50%（与中间区域一致） */
  scrollbar-width: thin;
  scrollbar-color: rgba(111, 103, 99, 0.2) transparent;
  transition: scrollbar-color 150ms var(--ease);
}
/* Chrome/Edge WebKit 滚动条（与中间区域配色一致） */
.chat-list::-webkit-scrollbar { width: 8px; }
.chat-list::-webkit-scrollbar-track { background: transparent; }
.chat-list::-webkit-scrollbar-thumb {
  background: rgba(111, 103, 99, 0.2);
  border-radius: 4px;
}
.chat-list::-webkit-scrollbar-thumb:hover { background: #6F6763; }
.left-sidebar:hover .chat-list::-webkit-scrollbar-thumb { background: rgba(111, 103, 99, 0.5); }
.left-sidebar:hover .chat-list { scrollbar-color: rgba(111, 103, 99, 0.5) transparent; }
.chat-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 3px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 150ms var(--ease);
}
.chat-item:hover { background: #FAF3EC; }
.chat-item.active { color: #3E3836; font-weight: 600; background: #FAF3EC; }
/* 选中态与 hover 一致，字体颜色沿用默认（hover 不改变字体色） */
/* 新会话条目淡入 */
.chat-item-new { animation: chatItemIn 240ms var(--ease); }
@keyframes chatItemIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
/* 无历史时的灰色占位（与 section-count 同色系，不可点击） */
.app-shell .chat-empty {
  list-style: none;
  padding: 10px 12px;
  font-size: 13px;
  color: #A89F93 !important;
  cursor: default;
}
.chat-ico { width: 16px; height: 16px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.chat-title {
  flex: 1;
  font-size: 13px;
  line-height: 1.3;
  color: #3E3836;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chat-time { color: #A89F93 !important; font-size: 10px; font-weight: 500; line-height: 1.4; flex-shrink: 0; }

/* 底部装饰图：静止态 left_bottom.jpg；hover 由 JS 用 canvas 播放 APNG 队列 */
.left-footer {
  padding: 12px 4px 6px;
  text-align: left;
  flex-shrink: 0;
  position: relative;            /* canvas / 气泡定位锚点 */
  cursor: pointer !important;    /* 需求3：hover 显示可点击 */
}
.left-footer img,
.left-footer canvas {
  width: 100%;
  max-height: 108px;
  object-fit: contain;
  object-position: left bottom;
  display: block;
  /* 顶部羽化：让图片上边缘柔和过渡到透明，避免硬切 */
  -webkit-mask-image: linear-gradient(to top, #000 100%, transparent 100%);
          mask-image: linear-gradient(to top, #000 100%, transparent 100%);
}
/* canvas 默认隐藏（静止态显示 lf-img）；hover 序列播放时由 JS 切换 is-anim */
.left-footer .lf-canvas { display: none !important; }
.left-footer.is-anim .lf-img { display: none !important; }
.left-footer.is-anim .lf-canvas { display: block !important; }

/* 缩略态 */
.collapsed-bar {
  position: absolute;
  inset: 0;
  width: 72px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding-top: 16px; /* 与展开态 sidebar-content padding-top 对齐，避免 logo 纵向跳动 */
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms var(--ease);
}
.left-sidebar.collapsed { width: 72px; }
.left-sidebar.collapsed .sidebar-content { opacity: 0; pointer-events: none; }
.left-sidebar.collapsed .collapsed-bar { opacity: 1; pointer-events: auto; }
.collapsed-logo-wrap {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  cursor: pointer;
  /* 与展开态 sidebar-content padding-left(14px) 对齐，避免 logo 横向跳动 */
  align-self: flex-start;
  margin-left: 14px;
}
.collapsed-logo {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  object-fit: cover;
  box-shadow: 0 1px 4px rgba(107, 80, 69, 0.15);
}
/* 展开图标：默认隐藏，hover logo 时叠加显示为展开按钮 */
.expand-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(250, 243, 236, 0.92);
  color: #6B5045;
  opacity: 0;
  transform: scale(0.85);
  transition: opacity 150ms var(--ease), transform 150ms var(--ease);
}
.collapsed-logo-wrap:hover .expand-icon {
  opacity: 1;
  transform: scale(1);
}
.collapsed-tool {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6F6763;
  background: transparent !important;
  border: 1px solid #F1E4D5;
  padding: 0 !important;
  transition: background 150ms var(--ease), color 150ms var(--ease);
}
.collapsed-tool:hover { background: #FFFFFF !important; color: #6B5045; }
.collapsed-plus { font-size: 18px; line-height: 1; }
/* 收起态左下角设置入口：推到底部并与 logo 左对齐，形成「左下角」固定入口 */
#collapsedSettingsBtn {
  align-self: flex-start;
  margin-left: 14px;
  margin-top: auto;
}

/* ============================================================
   中间主区域
   ============================================================ */
.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #FDFCFA;
  position: relative;
  overflow: hidden;
}

.open-right-btn {
  position: absolute;
  /* top:16px 与左侧 logo 顶端对齐（左 logo 顶端 = sidebar-content padding-top 16） */
  top: 16px;
  right: 30px;
  z-index: 20;
  /* 右栏默认收起时显示的「打开右栏」图标：去掉白色背景 / 边框 / 阴影，
     与其他 icon-btn 风格一致（透明，仅 SVG 描边） */
  background: transparent !important;
  border: none;
  box-shadow: none;
  display: flex;
}

.main-scroll {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  scrollbar-width: thin;
  /* Firefox：默认 20% 不透明，悬停中间区域时提升为 50% 不透明 */
  scrollbar-color: rgba(111, 103, 99, 0.2) transparent;
  transition: scrollbar-color 150ms var(--ease);
}
/* Chrome/Edge WebKit 滚动条 */
.main-scroll::-webkit-scrollbar { width: 8px; }
.main-scroll::-webkit-scrollbar-track { background: transparent; }
.main-scroll::-webkit-scrollbar-thumb {
  background: rgba(111, 103, 99, 0.2);
  border-radius: 4px;
}
.main-scroll::-webkit-scrollbar-thumb:hover { background: #6F6763; }
/* 鼠标焦点在中间区域（含输入区）时，滚动条降为 50% 不透明 */
.main-area:hover .main-scroll::-webkit-scrollbar-thumb { background: rgba(111, 103, 99, 0.5); }
.main-area:hover .main-scroll { scrollbar-color: rgba(111, 103, 99, 0.5) transparent; }

/* 内容层：动态宽度 clamp(768px, 57vw, 1000px) 居中；
   屏幕变宽时内容按比例增长（57vw），封顶 1000px（暂定，后续按效果调整）；
   空态内容整体垂直居中（免责声明除外，固定屏幕底部） */
.main-inner {
  width: 100%;
  max-width: clamp(768px, 57vw, 1000px);
  margin: 0 auto;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 22px 52px;
  transition: padding-top 480ms var(--ease);
}

/* Hero */
.hero { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 30px; max-height: 240px; flex-shrink: 0; transition: max-height 480ms var(--ease), opacity 480ms var(--ease), transform 480ms var(--ease), margin-bottom 480ms var(--ease); }
/* hero 子元素（slogan/插图）同步上移：避免容器高度塌缩时 align-items:center
   造成的居中对称裁剪（视觉上内容向下沉），改为内容向上穿出容器顶部 */
.hero-text, .hero-image { transition: transform 480ms var(--ease); }
.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #3E3836 !important;
  margin: 0 0 6px 0;
  line-height: 1.3;
}
.paw-emoji { color: #C7A18E; margin-left: 4px; font-size: 20px; }
.hero-subtitle { margin: 0; font-size: 13px; color: #6F6763; line-height: 1.5; }
.hero-image { width: 176px; flex-shrink: 0; }
.hero-image img {
  width: 100%;
  height: 108px;
  object-fit: contain;
  border-radius: 0;
  display: block;
  box-shadow: none;
}
.hero-image video {
  width: 100% !important;
  height: 108px !important;
  object-fit: contain !important;
  border-radius: 0;
  display: block;
  box-shadow: none;
}
.hero-image .hero-video { display: none !important; }
.hero-image.video-on .hero-img { display: none !important; }
.hero-image.video-on .hero-video { display: block !important; }

/* APNG 备选样式（切回时取消注释即可）：
.hero-image canvas {
  width: 100% !important;
  height: 108px !important;
  object-fit: contain !important;
  border-radius: 0;
  display: block;
  box-shadow: none;
}
.hero-image .hero-canvas { display: none !important; }
.hero-image.video-on .hero-canvas { display: block !important; }
*/

/* 快速开始 */
.quick-start { margin: 0; max-height: 200px; flex-shrink: 0; transition: max-height 480ms var(--ease), opacity 480ms var(--ease), transform 480ms var(--ease); }
.quick-title {
  text-align: left;
  font-size: 14px;
  font-weight: 400;
  color: #6F6763 !important;
  line-height: 1.4;
  margin: 0 0 14px;
}

/* 功能卡片：用户色 #FCFBF9/#F8F1EB */
.feature-grid {
  display: grid;
  /* 按卡片字数比例分配宽度：卡片1/2 约 7 字，卡片3（含「常问」标签）约 13 字，取 8:8:11 */
  grid-template-columns: 8fr 8fr 11fr;
  gap: 12px;
  margin-bottom: 0;
}
.feature-card {
  background: #FCFBF9 !important;
  border: 1.5px solid #F8F1EB !important;
  border-radius: 12px;
  height: 48px;
  padding: 0 16px;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  text-align: left;
  transition: box-shadow 180ms var(--ease), transform 180ms var(--ease);
}
.feature-card:hover { box-shadow: 0 4px 14px rgba(62, 56, 54, 0.08); transform: translateY(-1px); }
.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.feature-text { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
/* 卡片标题：Body-sm 风格（常规字重 400，非粗体），14px */
.feature-name { font-size: 13px; font-weight: 400; color: #3E3836 !important; line-height: 1.5; white-space: nowrap; }
/* 卡片右侧「常问」灰色小字标签 */
.app-shell .feature-tag {
  margin-left: auto !important;
  flex-shrink: 0 !important;
  font-size: 11px !important;
  font-weight: 400 !important;
  color: #A89F93 !important;
  line-height: 1 !important;
  letter-spacing: 0.5px !important;
}

/* 示例问题（用户色：底 #FDF8F4 框 #F8F1EB 图标 #B47B68） */
.example-section { margin-bottom: 18px; }
.example-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #3E3836;
  line-height: 1.4;
  margin-bottom: 8px;
}
.refresh-btn {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: #8C6B5D;
  background: transparent !important;
  padding: 0 !important;
  transition: background 150ms var(--ease);
}
.refresh-btn:hover { background: #F9F1E9 !important; color: #6B5045; }
.example-pills { display: flex; flex-wrap: wrap; gap: 8px; }
.example-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 999px;
  background: #FDF8F4 !important;
  border: 1.5px solid #F8F1EB !important;
  color: #6F6763;
  font-size: 13px !important;
  font-weight: 400 !important;
  line-height: 1.3;
  transition: background 150ms var(--ease), border-color 150ms var(--ease), color 150ms var(--ease);
}
.example-pill:hover { border-color: #E8D9C8 !important; background: #FAF0E6 !important; color: #6B5045; }
.pill-paw { display: inline-flex; align-items: center; flex-shrink: 0; }

/* 聊天记录 */
.chat-history { padding: 2px 0 4px; }
.message {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  align-items: flex-start;
  min-width: 0;
}
.message-user { flex-direction: row; justify-content: flex-end; }
.avatar { width: 36px; height: 36px; border-radius: 999px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; }
.avatar-bot { background: #F9F1E9; overflow: hidden; }
.avatar-bot img { width: 100%; height: 100%; object-fit: cover; }
.avatar-user { background: #C7A18E; color: #FFFFFF; }
.bubble {
  max-width: 72%;
  border-radius: 2px 18px 18px 18px;
  padding: 8px 12px;
  font-size: 15px;
  line-height: 1.5;
  overflow: hidden;
  position: relative;
}
.bubble-bot { background: #FFFFFF; border: 1.5px solid #F8F1EB; }
.bubble-user {
  background: #FAF3EC !important;
  color: #6B5045 !important;
  border-radius: 18px 2px 18px 18px;
}
.bubble-header { display: flex; align-items: center; gap: 4px; margin-bottom: 3px; }
.bubble-name { font-size: 13px; font-weight: 400; color: #6B5045; line-height: 1.3; }
.bubble-paw { font-size: 12px; }
.bubble-body { white-space: pre-wrap; word-break: break-word; min-width: 0; }
/* 历史回答「查看执行轨迹」图标：气泡右上角，轻量暖杏风，独立按钮不挡文本选择/点击 */
.app-shell .trace-view-btn {
  position: absolute !important;
  top: 8px !important;
  right: 8px !important;
  width: 24px !important;
  height: 24px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  border-radius: 6px !important;
  color: #C7A18E !important;
  cursor: pointer !important;
  opacity: 0.6;
  z-index: 2 !important;
  transition: background 150ms var(--ease), color 150ms var(--ease), opacity 150ms var(--ease) !important;
}
.app-shell .trace-view-btn:hover { background: #FAF3EC !important; color: #8C6B5D !important; opacity: 1; }
/* 有图标时给气泡右侧留白，避免文本压到图标 */
.app-shell .bubble-bot:has(.trace-view-btn) { padding-right: 30px !important; }
/* 被选中的历史气泡高亮（浅杏底 + 暖棕描边，清晰但不刺眼，符合暖杏奶油风）。
   高亮类加在 .message（row）上，故用后代选择器命中 .bubble-bot */
.app-shell .message.trace-active .bubble-bot {
  background: #FDFBF7 !important;
  border-color: #E8D8CC !important;
  box-shadow: 0 0 0 3px rgba(199, 161, 142, 0.18) !important;
}
/* 意图标签（暖杏风）：仅 meta/emergency 等高优先级意图显示，普通医学回复不显以保持简洁 */
.app-shell .bubble-intent {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 6px;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.6;
  border: 1px solid #EDE5DD;
  background: #FAF3EC;
  color: #8C6B5D;
}
.app-shell .bubble-intent.intent-meta { background: #F3EDE6; color: #8C6B5D; border-color: #E3D8CD; }
.app-shell .bubble-intent.intent-emergency { background: #F6E4DC; color: #B37560; border-color: #E8C7B8; }
.bubble-time { font-size: 10px; font-weight: 500; color: #A89F93 !important; line-height: 1.4; margin-top: 4px; }
/* 思考中气泡：不设独立样式，完全复用 .bubble-bot（白底 + 实线边框），仅以「思考中」文案与跳动点区分状态 */
.thinking-dots { display: inline-flex; gap: 3px; margin-left: 5px; vertical-align: middle; }
.thinking-dots span {
  width: 5px; height: 5px;
  background: #C7A18E;
  border-radius: 50%;
  display: inline-block;
  animation: thinkingBlink 1.2s infinite ease-in-out;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes thinkingBlink { 0%, 80%, 100% { opacity: 0.3; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-2px); } }

/* ============================================================
   聊天态（chat-mode）：空态首页 → 对话布局
   发送后 hero 向上 / quick-start 向下平滑塌缩移出，
   chat-area 占满中间（内部滚动），输入区贴底。
   ============================================================ */
.chat-area {
  display: none;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  padding: 4px 0 16px;
}

.main-inner.chat-mode {
  /* 聊天态：内容可多可少；hero 向上移出后，chat-area 从顶部开始排列，
     第一句对话停在画面顶部（main-inner 的 padding-top 提供留白）；
     消息多时 chat-area 自然撑开让外层 main-scroll 滚动，滚动条在最右侧 */
  min-height: 100%;
  /* 底部占位交给 .chat-mask（main-inner 之后的 sticky 元素），
     这里不再需要额外 padding-bottom */
  padding-bottom: 0;
}
.main-inner.chat-mode .chat-area {
  display: flex;
  /* 从顶部排列：第一句对话停在顶部（留白来自 main-inner 的 padding-top）。
     底部留白固定 20px，滚动到底时最后一条消息停在输入区上方约 20px。 */
  padding-bottom: 20px;
}
.input-area.chat-fixed {
  margin-bottom: 0;
  /* 聊天态由 JS 将 input-area 移动到 main-area 下（main-scroll 之外），
     containing block = main-area（position:relative），彻底脱离滚动流，
     固定在中间区域底部，不受 hero/chat-area 动画与滚动影响 */
  position: absolute;
  left: 0;
  right: 0;
  bottom: 44px; /* 距 main-area 底部 44px，disclaimer 在其下约 15px 处 */
  max-width: clamp(768px, 57vw, 1000px);
  margin-left: auto;
  margin-right: auto;
  /* 与 .main-inner 的横向 padding 一致，输入框与内容区左右对齐 */
  padding: 0 22px;
  /* 背景透明：输入区不再覆盖右侧滚动条；输入区背后及下方漏出的内容
     统一由 main-area 下的 .chat-mask 遮挡（滚动条绘制在遮罩之上） */
  background: transparent;
  z-index: 10;
  /* 聊天态出现时淡入上浮，掩盖从文档流切换为 absolute 的瞬间 */
  animation: inputAreaIn 480ms var(--ease) both;
}

/* 聊天态底部遮罩：置于 main-scroll 内部（main-inner 之后）。
   sticky bottom:0 相对滚动容器可视区固定 → 不随内容滚动，始终覆盖
   输入区（bottom:44px + 输入框高度）及其下方的漏出区；
   滚动条属于 main-scroll 且绘制在其内容之上 → 遮罩永远盖不住滚动条。
   高度默认 220px，JS 按输入区实际高度动态同步 */
.chat-mask {
  display: none;
  position: sticky;
  bottom: 0;
  height: 220px;
  background: #FDFCFA;
  pointer-events: none;
  flex-shrink: 0;
}
.chat-mask.show { display: block; }
@keyframes inputAreaIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
/* 空态区块移出动画：高度塌缩 + 位移 + 淡出 */
.main-inner.chat-mode .hero {
  max-height: 0;
  transform: translateY(-60px);
  opacity: 0;
  overflow: hidden;
  margin-bottom: 0;
}
.main-inner.chat-mode .hero-text,
.main-inner.chat-mode .hero-image {
  transform: translateY(-60px);
}
.main-inner.chat-mode .quick-start {
  max-height: 0;
  transform: translateY(60px);
  opacity: 0;
  overflow: hidden;
}

/* 消息入场动画：用户与 bot 气泡统一淡入上浮（10px） */
@keyframes userBubbleIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.message-user { animation: userBubbleIn 300ms ease-out both; }
@keyframes botBubbleIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.message-bot { animation: botBubbleIn 300ms ease-out both; }
/* 气泡入场动画期间允许溢出 chat-area（其尚在长高动画中，避免顶部裁剪） */
.chat-area.msg-in { overflow: visible; }

/* 流式输出光标 */
.type-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: #6B5045;
  margin-left: 2px;
  vertical-align: -2px;
  animation: cursorBlink 0.8s infinite ease-in-out;
}
@keyframes cursorBlink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* 输入区：文档流排列在 Hero 与快速开始之间（空态首页布局）
   聊天态时 sticky 在 main-scroll 底部，保持对话框可见 */
.input-area {
  width: 100%;
  margin: 0 0 30px;
  padding: 0;
  flex-shrink: 0;
  transition: margin-bottom 480ms var(--ease);
  /* 为 sticky 定位做准备（空态不触发，聊天态 content 超出时生效） */
  position: sticky;
  bottom: 0;
  z-index: 10;
  background: #FDFCFA;
}
.input-box {
  display: flex;
  flex-direction: column;
  background: #FEFEFE !important;
  border: 1.5px solid #F8F1EB !important;
  border-radius: 14px;
  padding: 10px 12px 8px;
  box-shadow: 0 3px 14px rgba(62, 56, 54, 0.07);
}
.input-text-wrap {
  min-height: 40px;
  max-height: 132px;
  overflow-y: auto;
  display: flex;
  align-items: flex-start;
}
.input-textarea {
  flex: 1;
  width: 100%;
  min-height: 24px;
  outline: none;
  font-size: 14px;
  line-height: 1.6;
  color: #3E3836;
  padding: 6px 2px;
  word-break: break-word;
}
.input-textarea:empty::before { content: "描述你的问题，或直接开始提问…"; color: rgba(168, 159, 147, 0.85); }
.input-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid #F8F1EB;
  padding-top: 8px;
  margin-top: 2px;
}
.toolbar-spacer { flex: 1; }
.input-tool {
  height: 32px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  border-radius: 8px;
  color: #6F6763;
  font-size: 12px !important;
  font-weight: 400 !important;
  line-height: 1.3;
  background: transparent !important;
  transition: background 150ms var(--ease), color 150ms var(--ease);
  flex-shrink: 0;
}
.input-tool:hover { background: #F9F1E9 !important; color: #6B5045; }
.plus-btn { font-size: 20px; font-weight: 400; padding: 0 8px; color: #8C6B5D; }
.template-btn, .model-btn { border: 1.5px solid #F8F1EB !important; background: #FDF8F4 !important; }
.template-btn:hover, .model-btn:hover { background: #FAF0E6 !important; }
.template-paw, .model-paw { display: inline-flex; align-items: center; }
.caret { color: #A99A90; transition: transform 180ms var(--ease); }
.model-btn.open .caret { transform: rotate(180deg); }
.mic-btn { display: none !important; }
/* 模型选择下拉 */
.model-select-wrap { position: relative; }
.model-popover {
  position: absolute;
  left: 0;
  bottom: calc(100% + 6px);
  min-width: 220px;
  background: #FFFFFF;
  border: 1px solid #EDE5DD;
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 -4px 20px rgba(62, 56, 54, 0.1);
  z-index: 100;
  opacity: 1;
  transform: translateY(0);
  transition: opacity 150ms var(--ease), transform 150ms var(--ease);
}
.model-popover.hidden { display: none; }
.model-option {
  padding: 9px 12px;
  border-radius: 7px;
  font-size: 13px;
  line-height: 1.4;
  color: #3E3836;
  cursor: pointer;
  transition: background 150ms var(--ease);
  white-space: nowrap;
}
.model-option:hover:not(.disabled) { background: #FAF3EC; }
.model-option.active { background: #FAF3EC; color: #6B5045; font-weight: 500; }
.model-option.disabled { color: #A99A90; cursor: not-allowed; }
.send-btn {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #B37560 !important;
  color: #FFFFFF !important;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 !important;
  flex-shrink: 0;
  transition: background 150ms var(--ease), transform 80ms;
}
.send-btn:hover { background: #9E5F4E !important; }
.send-btn:active { transform: scale(0.93); }
/* 无文字输入时：不可点击，浅色占位态（#FAF3EC）；有文字后恢复正常（#B37560） */
.send-btn:disabled {
  background: #FAF3EC !important;
  color: #C7A18E !important;
  cursor: not-allowed;
}
.send-btn:disabled svg { stroke: #C7A18E; }
.send-btn:disabled:hover { background: #FAF3EC !important; }
.send-btn:disabled:active { transform: none; }
/* 免责声明：始终固定在中间区域屏幕底部，不随内容滚动 */
.disclaimer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 12px;
  z-index: 20; /* 高于输入区及其底部遮罩（z-index:10），确保不被遮罩盖住 */
  text-align: center;
  padding: 0 16px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(168, 159, 147, 0.85);
  line-height: 1.4;
  pointer-events: none;
}

/* ============================================================
   右侧边栏（默认隐藏，宽 380）
   ============================================================ */
.right-sidebar {
  flex: 0 0 auto;
  width: 380px;
  min-width: 0;
  background: #FFFFFF;
  border-left: 1px solid #EDE5DD;
  display: flex;
  flex-direction: column;
  transition: width 300ms var(--ease), opacity 200ms var(--ease);
  overflow: hidden;
  position: relative;
}
.right-sidebar.hidden { flex: 0 0 0; width: 0; min-width: 0; max-width: 0; opacity: 0; border-left: none; }
.right-sidebar.fullscreen { position: fixed; top: 0; right: 0; bottom: 0; width: 100vw; flex: 0 0 auto; min-width: 0; max-width: none; z-index: 50; }
.sidebar-resizer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  z-index: 10;
  background: transparent;
  transition: background 150ms;
}
.sidebar-resizer:hover { background: #C7A18E; }
.right-sidebar.hidden .sidebar-resizer,
.right-sidebar.fullscreen .sidebar-resizer { display: none; }
.right-inner { position: relative; width: 100%; min-width: 0; height: 100%; display: flex; flex-direction: column; }

.right-header {
  flex: 0 0 auto;
  /* padding-top 16px 使收起按钮顶端与左侧 logo 顶端对齐（sidebar padding-top 16，左侧 logo 顶端 y=16） */
  padding: 16px 16px 12px;
  border-bottom: 1px solid #EDE5DD;
}
.right-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.right-title { display: flex; align-items: center; gap: 7px; font-size: 16px; font-weight: 600; color: #3E3836; line-height: 1.4; }
.title-star { color: #C7A18E; font-size: 14px; line-height: 1; }
.right-actions { display: flex; gap: 2px; }

.right-timeline { flex: 1 1 0; min-height: 0; overflow-y: auto; padding: 12px 12px 4px; scrollbar-width: thin; scrollbar-color: rgba(111, 103, 99, 0.2) transparent; transition: scrollbar-color 150ms var(--ease); }
.right-detail { flex: 1 1 0; min-height: 0; display: flex; flex-direction: column; border-top: 1px solid #EDE5DD; }
.detail-resizer {
  flex: 0 0 auto;
  height: 4px;
  margin: -2px 0;
  cursor: row-resize;
  background: transparent;
  transition: background 150ms;
  position: relative;
  z-index: 5;
}
.detail-resizer:hover { background: #C7A18E; }
.right-sidebar.detail-expanded .detail-resizer { display: none; }
.detail-body { flex: 1 1 auto; min-height: 0; overflow-y: auto; padding: 12px 16px 16px; scrollbar-width: thin; scrollbar-color: rgba(111, 103, 99, 0.2) transparent; transition: scrollbar-color 150ms var(--ease); }
/* 右侧边栏滚动条 WebKit 样式，与中间区域统一 */
.right-timeline::-webkit-scrollbar,
.detail-body::-webkit-scrollbar { width: 8px; }
.right-timeline::-webkit-scrollbar-track,
.detail-body::-webkit-scrollbar-track { background: transparent; }
.right-timeline::-webkit-scrollbar-thumb,
.detail-body::-webkit-scrollbar-thumb { background: rgba(111, 103, 99, 0.2); border-radius: 4px; }
.right-timeline::-webkit-scrollbar-thumb:hover,
.detail-body::-webkit-scrollbar-thumb:hover { background: #6F6763; }
.right-timeline:hover::-webkit-scrollbar-thumb,
.detail-body:hover::-webkit-scrollbar-thumb { background: rgba(111, 103, 99, 0.5); }
.right-timeline:hover,
.detail-body:hover { scrollbar-color: rgba(111, 103, 99, 0.5) transparent; }
/* 展开：隐藏 Timeline，详情填满 Header 以下区域 */
.right-sidebar.detail-expanded .right-timeline { display: none; }
.right-sidebar.detail-expanded .right-detail { border-top: none; }
.right-group { margin-bottom: 6px; }
.right-group-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 6px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #3E3836;
  line-height: 1.4;
  cursor: pointer;
  list-style: none;
  transition: background 150ms var(--ease);
}
.right-group-title:hover { background: #F9F1E9; }
.right-group-title::-webkit-details-marker { display: none; }
.chevron { color: #A99A90; transition: transform 180ms var(--ease); }
details[open] .chevron { transform: rotate(180deg); }
.right-group-content { padding: 2px 0 6px 4px; }
.empty-hint { font-size: 13px; font-weight: 400; color: #6F6763; line-height: 1.3; padding: 6px 4px; }

.file-tree { display: flex; flex-direction: column; gap: 1px; }
.file-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.3;
  color: #3E3836;
  cursor: pointer;
  transition: background 150ms var(--ease), color 150ms var(--ease);
}
.file-node:hover { background: #F9F1E9; color: #6B5045; }
.file-dot { width: 9px; height: 9px; border-radius: 3px; flex-shrink: 0; }
.dot-py { background: #4B8BBE; }
.dot-env { background: #C4A35A; }
.dot-txt { background: #8C8C8C; }

.right-more {
  width: 100%;
  margin-top: 8px;
  padding: 6px;
  border: none;
  background: transparent !important;
  color: #8C6B5D;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.3;
  transition: color 150ms var(--ease);
}
.right-more:hover { background: transparent !important; color: #6B5045; }

/* ============================================================
   右侧栏 AI 分析过程（三段式：Header + Timeline + Detail）
   配色遵循 design-system-spec.md 方案 B
   ============================================================ */
.trace-empty { font-size: 13px; color: #6F6763; line-height: 1.6; padding: 16px 8px; text-align: center; }

/* Header 状态行 + 输入摘要 */
.analysis-status {
  margin-top: 8px;
  font-size: 12px;
  color: #6F6763;
  line-height: 1.4;
}
.analysis-status .status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: 1px;
  background: #CFC7C2;
}
.analysis-status.is-running .status-dot { background: #907063; animation: nodePulse 1.8s ease-in-out infinite; }
.analysis-status.is-completed .status-dot { background: #6F8A6A; }
.analysis-status.is-error .status-dot { background: #B86B5B; }

.analysis-input {
  margin-top: 6px;
  font-size: 12px;
  color: #A99A90;
  line-height: 1.5;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.input-type-tag {
  display: inline-block;
  margin-right: 6px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 11px;
  line-height: 1.7;
  vertical-align: 1px;
}
.input-type-tag.type-normal { background: #FDFBF7; border: 1px solid #EDE5DD; color: #6F6763; }
.input-type-tag.type-composite { background: #FAF3EC; border: 1px solid #E7D8CC; color: #6B5045; }

/* Timeline 步骤 */
.analysis-step {
  display: flex;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 150ms var(--ease);
}
.analysis-step:hover { background: #FAF3EC; }
.analysis-step.is-selected {
  background: #FAF3EC;
  border-color: #C7A18E;
}
.step-rail {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 16px;
  flex-shrink: 0;
}
.step-node {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #FFFFFF;
  line-height: 1;
}
.step-rail::after {
  content: '';
  position: absolute;
  top: 18px;
  bottom: -12px;
  width: 1px;
  background: #EDE5DD;
}
.analysis-step:last-child .step-rail::after { display: none; }

/* 节点五态 */
.step-node.node-pending { border: 1.5px solid #CFC7C2; background: transparent; }
.step-node.node-running { background: #907063; animation: nodePulse 1.8s ease-in-out infinite; }
.step-node.node-completed { background: #FFFFFF; border: 1.5px solid #6F8A6A; color: #6F8A6A; }
.step-node.node-error { background: #B86B5B; }
.step-node.node-skipped { border: 1.5px dashed #CFC7C2; background: transparent; }

.step-info { flex: 1; min-width: 0; padding-bottom: 2px; }
.step-title { font-size: 14px; font-weight: 600; color: #3E3836; line-height: 1.4; }
.step-summary { margin-top: 2px; font-size: 12px; color: #6F6763; line-height: 1.5; word-break: break-all; }
.analysis-step.is-skipped .step-title { color: #6F6763; font-weight: 400; text-decoration: line-through; }
.analysis-step.is-skipped .step-summary { color: #A99A90; }

@keyframes nodePulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* Detail Panel */
.detail-empty { font-size: 13px; color: #A99A90; line-height: 1.6; padding: 16px 8px; text-align: center; }
.detail-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.detail-head-text { flex: 1; min-width: 0; }
.detail-expand-btn {
  flex-shrink: 0;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 6px;
  color: #4a3a2d;
  cursor: pointer;
  transition: background 150ms;
}
.detail-expand-btn:hover { background: #FAF3EC; }
.detail-expand-btn svg { fill: #4a3a2d !important; }
.detail-expand-btn .icon-down { display: none; }
.right-sidebar.detail-expanded .detail-expand-btn .icon-up { display: none; }
.right-sidebar.detail-expanded .detail-expand-btn .icon-down { display: inline-block; }
.detail-head-title { font-size: 15px; font-weight: 600; color: #3E3836; line-height: 1.4; }
.detail-head-subtitle { margin-top: 2px; font-size: 12px; color: #6F6763; line-height: 1.5; }
.detail-content { margin-top: 12px; }
.detail-section { margin-bottom: 14px; }
.detail-section:last-child { margin-bottom: 0; }
.detail-label { font-size: 12px; font-weight: 600; color: #6B5045; margin-bottom: 6px; }
.detail-text { font-size: 13px; color: #3E3836; line-height: 1.7; word-break: break-word; white-space: pre-wrap; }
.detail-kv { display: flex; gap: 6px; font-size: 13px; line-height: 1.6; margin-bottom: 4px; }
.detail-kv .dk-label { color: #6F6763; flex-shrink: 0; }
.detail-kv .dk-value { color: #3E3836; word-break: break-all; }
.detail-relation {
  padding: 7px 10px;
  border: 1px solid #EDE5DD;
  border-radius: 8px;
  margin-bottom: 6px;
}
.detail-relation:last-child { margin-bottom: 0; }
.detail-relation .rel-main { font-size: 13px; color: #3E3836; line-height: 1.5; word-break: break-all; }
.detail-relation .rel-meta { margin-top: 3px; font-size: 12px; color: #6F6763; line-height: 1.5; }
.detail-relation .rel-evidence { margin-top: 3px; font-size: 12px; color: #A99A90; line-height: 1.5; word-break: break-all; }

/* 澄清按钮（中间对话区） */
/* 引导语（对话气泡内） */
.app-shell .clarify-tip { font-size: 13px; color: #6F6763; line-height: 1.6; margin-bottom: 4px; }
/* 追问面板：渲染在输入框上方，竖排候选项 + 最后的「其他补充」输入框 */
/* clarifying 时隐藏真正的 textarea，让追问面板覆盖输入区，避免两个可输入区域 */
.app-shell .input-box.clarifying .input-text-wrap { display: none; }
.app-shell .clarify-panel {
  position: relative !important;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  padding: 12px;
  background: #FFFFFF !important;
  border: 1.5px solid #F8F1EB !important;
  border-radius: 14px !important;
}
/* 追问澄清面板右上角关闭 X（无外框，仅简单 X） */
.app-shell .clarify-close {
  position: absolute !important;
  top: 8px !important;
  right: 8px !important;
  width: 22px !important;
  height: 22px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  border-radius: 6px !important;
  color: #A89F93 !important;
  cursor: pointer !important;
  transition: background 150ms var(--ease), color 150ms var(--ease) !important;
}
.app-shell .clarify-close:hover { background: #F6F0EA !important; color: #6B5045 !important; }
.app-shell .clarify-close svg { display: block; }
.app-shell .clarify-subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #6F6763;
  line-height: 1.5;
  margin-bottom: 2px;
}
.app-shell .clarify-opt {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  width: 100% !important;
  text-align: left !important;
  padding: 11px 14px !important;
  background: #FDFBF7 !important;
  border: 1px solid #EDE5DD !important;
  border-radius: 10px !important;
  color: #6F6763 !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  line-height: 1.4 !important;
  cursor: pointer !important;
  transition: background 150ms var(--ease), border-color 150ms var(--ease), color 150ms var(--ease) !important;
}
.app-shell .clarify-opt-label { flex: 1; min-width: 0; }
.app-shell .clarify-opt-arrow { display: inline-flex; color: #C7A18E; margin-left: 10px; flex-shrink: 0; transition: color 150ms var(--ease); }
.app-shell .clarify-opt:hover {
  background: #FAF3EC !important;
  border-color: #C7A18E !important;
  color: #3E3836 !important;
}
.app-shell .clarify-opt:hover .clarify-opt-arrow { color: #8C6B5D; }
.app-shell .clarify-opt:active { transform: scale(0.99); }
.app-shell .clarify-other {
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
  margin-top: 0 !important;
  padding: 11px 14px !important;
  background: #FDFBF7 !important;
  border: 1px solid #EDE5DD !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  transition: background 150ms var(--ease), border-color 150ms var(--ease) !important;
}
/* 焦点进入底部输入框时，胶囊呈现与 hover 一致的态 */
.app-shell .clarify-other:focus-within {
  background: #FAF3EC !important;
  border-color: #C7A18E !important;
}
.app-shell .clarify-other-input {
  flex: 1 !important;
  width: 100% !important;
  border: none !important;
  outline: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  font-size: 13px !important;
  color: #3E3836 !important;
  font-family: inherit !important;
}
.app-shell .clarify-other-input::placeholder { color: #A89F93 !important; }
/* 底部发送图标：与上面一致的 → 箭头，无外框；空时灰色不可点，有字时箭头色 */
.app-shell .clarify-send {
  flex-shrink: 0 !important;
  width: auto !important;
  height: auto !important;
  padding: 0 !important;
  border: none !important;
  background: transparent !important;
  color: #C4B9B1 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: not-allowed !important;
  transition: color 150ms var(--ease) !important;
}
.app-shell .clarify-send:not(:disabled) { cursor: pointer !important; color: #C7A18E !important; }
.app-shell .clarify-send:not(:disabled):hover { color: #8C6B5D !important; }
.app-shell .clarify-send:disabled { color: #C4B9B1 !important; }

/* ============================================================
   小屏适配：默认左侧缩略；常规 PC 优先完整展示
   ============================================================ */
@media (max-width: 1100px) {
  .left-sidebar { width: 72px; }
  .left-sidebar .sidebar-content { opacity: 0; pointer-events: none; }
  .left-sidebar .collapsed-bar { opacity: 1; pointer-events: auto; }
  .right-sidebar { flex: 0 0 auto; width: 250px; max-width: 250px; }
  .right-inner { width: 250px; min-width: 250px; }
}
@media (max-width: 920px) {
  .right-sidebar { flex: 0 0 0; width: 0; min-width: 0; max-width: 0; opacity: 0; border-left: none; }
  .right-sidebar .right-inner { display: none; }
  .main-inner { padding: 28px 16px 44px; }
  .feature-grid { grid-template-columns: repeat(2, 1fr); }
  .hero-image { display: none; }
}
"""


# ---------------------------------------------------------------------------
# asset 图片：运行时读取并转为 base64 data URI 内嵌
# （Gradio 的 file= 相对路径在页面路由下 404，无法直接使用）
# ---------------------------------------------------------------------------
_ASSET_DIR = Path(__file__).resolve().parent / "asset"


def _data_uri(name: str) -> str:
    data = (_ASSET_DIR / name).read_bytes()
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'svg': 'image/svg+xml', 'gif': 'image/gif', 'webp': 'image/webp'}.get(ext, 'application/octet-stream')
    return "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")


_IMG_REPLACEMENTS = {
    "file=asset/logo.jpg": _data_uri("logo.jpg"),
    "file=asset/left_bottom.jpg": _data_uri("left_bottom.jpg"),
    "file=asset/middle.jpg": _data_uri("middle.jpg"),
    "file=asset/bot_avatar.jpg": _data_uri("bot_avatar.jpg"),
    "file=asset/neo4j_demo_1.png": _data_uri("neo4j_demo_1.png"),
    "file=asset/neo4j_demo_2.png": _data_uri("neo4j_demo_2.png"),
}

_HOME_HTML = HOMEPAGE_HTML
for _k, _v in _IMG_REPLACEMENTS.items():
    _HOME_HTML = _HOME_HTML.replace(_k, _v)

# JS 动态创建的 bot 气泡头像同样需要内嵌 data URI（绕过 file= 404）
_JS_EXEC = JS_CODE
for _k, _v in _IMG_REPLACEMENTS.items():
    _JS_EXEC = _JS_EXEC.replace(_k, _v)

# favicon 强制保持：Gradio 6.x 前端会在运行时用默认图标覆盖 <head> 中的 favicon，
# 导致“favicon→默认→favicon”跳动。这里用 MutationObserver 持续保证我们的图标
# 始终是唯一生效的图标链接，无论 Gradio 何时注入默认图标都能即时压回。
_FAVICON_JS = (
    "(function(){"
    "var FAV=\"/gradio_api/file=asset/favicon.png\";"
    "function enforceFavicon(){"
    "var head=document.head||document.getElementsByTagName(\"head\")[0];"
    "if(!head) return;"
    "var links=head.querySelectorAll('link[rel=\"icon\"], link[rel=\"shortcut icon\"]');"
    "var hasOurs=false;"
    "for(var i=0;i<links.length;i++){"
    "if(links[i].getAttribute(\"href\")===FAV){hasOurs=true;}"
    "else{if(links[i].parentNode) links[i].parentNode.removeChild(links[i]);}"
    "}"
    "if(!hasOurs){"
    "var nl=document.createElement(\"link\");"
    "nl.rel=\"icon\"; nl.type=\"image/png\"; nl.href=FAV;"
    "head.appendChild(nl);"
    "}"
    "}"
    "enforceFavicon();"
    "if(window.MutationObserver){"
    "var obs=new MutationObserver(function(muts){"
    "for(var i=0;i<muts.length;i++){"
    "var added=muts[i].addedNodes;"
    "for(var j=0;j<added.length;j++){"
    "var n=added[j];"
    "if(n.nodeType===1 && n.tagName===\"LINK\" && (n.rel===\"icon\"||n.rel===\"shortcut icon\") && n.getAttribute(\"href\")!==FAV){"
    "enforceFavicon(); break;"
    "}"
    "}"
    "}"
    "});"
    "obs.observe(document.head||document.documentElement,{childList:true,subtree:false});"
    "}"
    "/* 兜底：加载初期 Gradio 可能在 js_on_load 之前写入默认图标，短时轮询复核 */"
    "var _t=0; var _iv=setInterval(function(){ enforceFavicon(); if(++_t>30){ clearInterval(_iv); } },100);"
    "})();"
)
_JS_EXEC = _FAVICON_JS + _JS_EXEC

# 注入图数据库页面 HTML（iframe srcdoc 懒加载）
import json as _json
_GRAPH_PAGE_HTML = open(os.path.join(os.path.dirname(__file__), 'source/design/graph-demo.html'), encoding='utf-8').read()
_JS_EXEC = _JS_EXEC.replace('__GRAPH_HTML_JSON__', _json.dumps(_GRAPH_PAGE_HTML).replace('</', '<\\/'))

# 文献库 / 产品设计说明：独立空页面文件（后续填充内容只改对应文件，无需动 app.py）
_DOCS_PAGE_HTML = open(os.path.join(os.path.dirname(__file__), 'source/design/docs.html'), encoding='utf-8').read()
_DESIGN_PAGE_HTML = open(os.path.join(os.path.dirname(__file__), 'source/design/design.html'), encoding='utf-8').read()
# design.html 内引用的 asset 图片需内嵌 base64（它在上面的 _IMG_REPLACEMENTS 循环之后才注入 _JS_EXEC，不会被自动替换）
for _k, _v in _IMG_REPLACEMENTS.items():
    _DESIGN_PAGE_HTML = _DESIGN_PAGE_HTML.replace(_k, _v)
_JS_EXEC = _JS_EXEC.replace('__DOCS_HTML_JSON__', _json.dumps(_DOCS_PAGE_HTML).replace('</', '<\\/'))
_JS_EXEC = _JS_EXEC.replace('__DESIGN_HTML_JSON__', _json.dumps(_DESIGN_PAGE_HTML).replace('</', '<\\/'))

# 视觉设计 demo（Module 04 标题栏入口）：独立 HTML 文件。
# 用 try/except 安全读取，缺失/失败时不阻断 app.py 启动（避免顶层异常导致 Gradio 起不来、被旧进程/缓存顶替）。
try:
    _STYLE_DEMO_HTML = open(os.path.join(os.path.dirname(__file__), 'source/UI/style-demo.html'), encoding='utf-8').read()
except Exception as _e:
    print('[warn] 未能加载 source/UI/style-demo.html，style-demo 弹窗将不可用：', repr(_e))
    _STYLE_DEMO_HTML = ''
_JS_EXEC = _JS_EXEC.replace('__STYLE_DEMO_HTML_JSON__', _json.dumps(_STYLE_DEMO_HTML).replace('</', '<\\/'))

_STYLE_HTML = (
    "<style>\n"
    + _GRADIO_CSS
    + "\n/* 图数据库页面 */\n"
    + ".page-graph{border:none;flex:1;background:#FDFBF7;display:none;}\n"
    + ".app-shell.mode-graph .main-area,"
    + ".app-shell.mode-graph .right-sidebar{display:none!important;}\n"
    + ".app-shell.mode-graph .page-graph{display:block;}\n"
    + ".app-shell.mode-graph .left-sidebar{z-index:1000!important;pointer-events:auto!important;}\n"
    + "\n/* 文献库 / 产品设计说明页面（空页面占位） */\n"
    + ".page-docs,.page-design{border:none;flex:1;background:#FDFBF7;display:none;}\n"
    + ".app-shell.mode-docs .main-area,.app-shell.mode-docs .right-sidebar{display:none!important;}\n"
    + ".app-shell.mode-docs .page-docs{display:block;}\n"
    + ".app-shell.mode-design .main-area,.app-shell.mode-design .right-sidebar{display:none!important;}\n"
    + ".app-shell.mode-design .page-design{display:block;}\n"
    + "body.design-expand-open #leftSidebar{position:absolute;top:0;left:0;bottom:0;transform:translateX(-100%);}\n"
    + "/* 全局自定义 tooltip：替代 title 黑底白字 */\n"
    + ".app-tooltip{position:fixed;z-index:9999;background:#FFFFFF;color:#3E3836;border:1px solid #EDE5DD;border-radius:6px;padding:6px 8px;font-size:12px;line-height:18px;box-shadow:0 4px 12px rgba(62,56,54,0.10);pointer-events:none;opacity:0;transform:translateY(2px);transition:opacity 100ms ease, transform 100ms ease;white-space:nowrap;max-width:260px;overflow:hidden;text-overflow:ellipsis;}\n"
    + ".app-tooltip.app-tooltip--show{opacity:1;transform:translateY(0);transition:opacity 150ms ease, transform 150ms ease;}\n"
    + ".app-tooltip.app-tooltip--bubble{border-radius:12px!important;padding:8px 12px!important;box-shadow:0 8px 24px rgba(62,56,54,0.12)!important;overflow:visible!important;}\n"
    + ".app-tooltip.app-tooltip--bubble::after{content:'';position:absolute!important;left:50%!important;bottom:-6px!important;width:12px!important;height:12px!important;background:#FFFFFF!important;border-right:1px solid #EDE5DD!important;border-bottom:1px solid #EDE5DD!important;transform:translateX(-50%) rotate(45deg)!important;}\n"
    + "/* 视觉设计 demo 模态框（独立顶层，避免受 Gradio reset 影响） */\n"
    + ".style-demo-modal{position:fixed;inset:0;z-index:3000;display:none;background:rgba(62,56,54,.45);}\n"
    + ".style-demo-modal.is-open{display:flex;align-items:center;justify-content:center;padding:24px;animation:demoFadeIn 300ms var(--ease) both;}\n"
    + ".style-demo-modal.is-closing{display:flex;align-items:center;justify-content:center;padding:24px;animation:demoFadeOut 300ms var(--ease) both;}\n"
    + ".style-demo-modal__content{position:relative;z-index:1;width:min(1100px,100%);height:min(780px, calc(100% - 48px));max-height:100%;background:#FDFBF7;border-radius:12px;box-shadow:0 24px 60px rgba(62,56,54,.18);display:flex;flex-direction:column;overflow:hidden;animation:demoIn 300ms var(--ease) both;}\n"
    + ".style-demo-modal__head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #EDE5DD;background:#FFFFFF!important;}\n"
    + ".style-demo-modal__title{font-size:15px;font-weight:600;color:#6B5045!important;}\n"
    + ".style-demo-modal__close{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border:none!important;box-shadow:none!important;outline:none!important;border-radius:6px;background:transparent!important;color:#6F6763!important;cursor:pointer;font-size:18px;line-height:1;}\n"
    + ".style-demo-modal__close:hover{background:#FAF3EC!important;color:#3E3836!important;}\n"
    + ".style-demo-modal__frame{flex:1;min-height:0;border:none;width:100%;height:100%;background:#fff;}\n"
    + ".style-demo-modal.is-closing .style-demo-modal__content{animation:demoOut 300ms var(--ease) both;}\n"
    + "/* 展开弹窗（产品设计说明详情）：顶层覆盖层，与 style-demo 弹窗同构 */\n"
    + ".design-expand-modal{position:fixed;inset:0;z-index:3000;display:none;background:rgba(62,56,54,.45);}\n"
    + ".design-expand-modal.is-open{display:flex;align-items:center;justify-content:center;padding:24px;animation:demoFadeIn 300ms var(--ease) both;}\n"
    + ".design-expand-modal.is-closing{display:flex;align-items:center;justify-content:center;padding:24px;animation:demoFadeOut 300ms var(--ease) both;}\n"
    + ".design-expand-modal__content{position:relative;z-index:1;max-width:90vw;height:min(780px, calc(100% - 48px));max-height:100%;background:#FFFFFF;border-radius:12px;box-shadow:0 24px 60px rgba(62,56,54,.18);display:flex;flex-direction:column;overflow:hidden;animation:demoIn 300ms var(--ease) both;}\n"
    + ".design-expand-modal__head{display:flex;align-items:center;justify-content:space-between;padding:24px 24px 16px;border-bottom:1px solid #EDE5DD;background:#FFFFFF!important;}\n"
    + ".design-expand-modal__title{font-size:15px;font-weight:600;color:#6B5045!important;}\n"
    + ".design-expand-modal__close{display:flex;align-items:center;justify-content:center;width:28px;height:28px;border:none!important;box-shadow:none!important;outline:none!important;border-radius:6px;background:transparent!important;color:#6F6763!important;cursor:pointer;font-size:18px;line-height:1;}\n"
    + ".design-expand-modal__close:hover{background:#FAF3EC!important;color:#3E3836!important;}\n"
    + ".design-expand-modal__frame{flex:1;min-height:0;border:none;width:100%;height:100%;background:#fff;}\n"
    + ".design-expand-modal.is-closing .design-expand-modal__content{animation:demoOut 300ms var(--ease) both;}\n"
    + "@keyframes demoFadeIn{from{opacity:0;}to{opacity:1;}}\n"
    + "@keyframes demoFadeOut{from{opacity:1;}to{opacity:0;}}\n"
    + "@keyframes demoIn{from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:translateY(0);}}\n"
    + "@keyframes demoOut{from{opacity:1;transform:translateY(0);}to{opacity:0;transform:translateY(12px);}}\n"
    + "/* 打开弹窗时：侧边栏向右划出（300ms）+ 下方不可交互 */\n"
    + "body.style-demo-open #leftSidebar{position:absolute;top:0;left:0;bottom:0;transform:translateX(-100%);}\n"
    + "body.style-demo-open #pageDesign{pointer-events:none!important;}\n"
    + ".img-lightbox{position:fixed;inset:0;z-index:4000;display:none;align-items:center;justify-content:center;padding:24px;}\n"
    + ".img-lightbox.is-open{display:flex;animation:demoFadeIn 200ms cubic-bezier(0.4,0,0.2,1) both;}\n"
    + ".img-lightbox__overlay{position:absolute;inset:0;background:rgba(42,38,36,.78);}\n"
    + ".img-lightbox__img{position:relative;z-index:1;max-width:92vw;max-height:92vh;width:auto;height:auto;border-radius:12px;box-shadow:0 24px 60px rgba(0,0,0,.35);background:#fff;}\n"
    + ".img-lightbox__close{position:absolute;top:18px;right:22px;z-index:2;display:flex;align-items:center;justify-content:center;width:36px;height:36px;padding:0!important;border:none!important;border-radius:999px;background:#FFFFFF!important;color:#3E3836!important;font-size:22px;line-height:1;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.25)!important;}\n"
    + ".img-lightbox__close:hover{background:#FAF3EC!important;color:#3E3836!important;}\n"
    + "/* ===== 设置功能：面板 / Modal / Password / Toast（body 作用域 .st-*，顶层浮层） ===== */\n"
    + "/* 设置面板（锚定左下角的轻量 Popover，无遮罩，点外部关闭） */\n"
    + "body .st-settings{position:fixed!important;z-index:3900!important;display:none!important;width:288px;max-width:calc(100vw - 24px);max-height:calc(100vh - 32px);background:var(--st-surface);border:1px solid var(--st-border);border-radius:12px;box-shadow:var(--st-shadow-panel);overflow:hidden;transform-origin:bottom left;}\n"
    + "body .st-settings.is-open{display:flex!important;flex-direction:column!important;animation:stPanelIn 180ms var(--ease) both;}\n"
    + "body .st-settings.is-closing{display:flex!important;flex-direction:column!important;animation:stPanelOut 140ms var(--ease) both;}\n"
    + "body .st-settings__head{display:flex!important;align-items:center!important;justify-content:space-between!important;padding:14px 12px 10px 16px!important;}\n"
    + "body .st-settings__title-group{display:flex!important;align-items:center!important;gap:8px!important;}\n"
    + "body .st-settings__gear{display:inline-flex!important;align-items:center!important;justify-content:center!important;color:var(--st-text2)!important;}\n"
    + "body .st-settings__gear svg{width:18px!important;height:18px!important;display:block!important;}\n"
    + "body .st-settings__title{font-size:16px!important;font-weight:600!important;color:var(--st-text)!important;}\n"
    + "body .st-settings__subtitle{font-size:11px!important;font-weight:600!important;letter-spacing:.08em!important;color:var(--st-primary)!important;}\n"
    + "body .st-settings__close{display:flex!important;align-items:center!important;justify-content:center!important;width:28px!important;height:28px!important;border:none!important;box-shadow:none!important;outline:none!important;border-radius:6px!important;background:transparent!important;color:var(--st-text2)!important;cursor:pointer!important;font-size:18px!important;line-height:1!important;}\n"
    + "body .st-settings__close svg{width:16px!important;height:16px!important;display:block!important;}\n"
    + "body .st-settings__close:hover{background:var(--st-hover)!important;color:var(--st-primary-hover)!important;}\n"
    + "body .st-settings__body{padding:4px 12px 14px!important;flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;scrollbar-width:thin!important;scrollbar-color:rgba(111,103,99,0.2) transparent!important;transition:scrollbar-color 150ms var(--ease)!important;}\n"
    + "body .st-settings__body::-webkit-scrollbar{width:8px!important;}\n"
    + "body .st-settings__body::-webkit-scrollbar-track{background:transparent!important;}\n"
    + "body .st-settings__body::-webkit-scrollbar-thumb{background:rgba(111,103,99,0.2)!important;border-radius:4px!important;}\n"
    + "body .st-settings__body::-webkit-scrollbar-thumb:hover{background:#6F6763!important;}\n"
    + "body .st-settings:hover .st-settings__body::-webkit-scrollbar-thumb{background:rgba(111,103,99,0.5)!important;}\n"
    + "body .st-settings:hover .st-settings__body{scrollbar-color:rgba(111,103,99,0.5) transparent!important;}\n"
    + "body .st-group{margin-top:6px!important;}\n"
    + "body .st-group__label{font-size:12px!important;font-weight:500!important;color:var(--st-group)!important;padding:10px 4px 6px!important;letter-spacing:.02em!important;}\n"
    + "body .st-divider{height:1px!important;background:var(--st-border)!important;margin:12px 4px!important;}\n"
    + "body .st-divider--head{margin:4px 4px 0!important;}\n"
    + "body .st-item{display:flex!important;align-items:center!important;justify-content:space-between!important;width:100%!important;height:38px!important;padding:0 14px!important;margin:2px 0!important;border:none!important;box-shadow:none!important;outline:none!important;border-radius:8px!important;background:transparent!important;color:var(--st-text)!important;font-size:14px!important;font-weight:500!important;cursor:pointer!important;text-align:left!important;transition:background 150ms var(--ease)!important;}\n"
    + "body .st-item:hover{background:var(--st-hover)!important;color:var(--st-text)!important;}\n"
    + "body .st-item__label{color:var(--st-text)!important;}\n"
    + "body .st-item__arrow{display:inline-flex!important;align-items:center!important;justify-content:center!important;color:var(--st-text2)!important;opacity:.7!important;transition:color 150ms var(--ease),opacity 150ms var(--ease),transform 150ms var(--ease)!important;}\n"
    + "body .st-item__arrow svg{width:18px!important;height:18px!important;display:block!important;}\n"
    + "body .st-item:hover .st-item__arrow{color:var(--st-primary)!important;opacity:1!important;transform:translateX(2px)!important;}\n"
    + "/* 轻量反馈 CTA Card：顶部独立模块，替代原「给我反馈」菜单行 */\n"
    + "body .st-feedback-card{display:flex!important;align-items:center!important;gap:10px!important;width:100%!important;height:84px!important;padding:12px!important;margin:12px 0!important;box-sizing:border-box!important;border:1px solid #E8D8CC!important;border-radius:12px!important;background:#FAF3EC!important;color:var(--st-text)!important;cursor:pointer!important;text-align:left!important;transition:background 150ms var(--ease),box-shadow 150ms var(--ease)!important;}\n"
    + "body .st-feedback-card:hover{background:#F2E4D7!important;box-shadow:0 2px 10px rgba(111,103,99,0.10)!important;}\n"
    + "body .st-feedback-card + .st-divider{margin-top:4px!important;}\n"
    + "body .st-feedback-card:focus-visible{outline:2px solid var(--st-focus)!important;outline-offset:2px!important;}\n"
    + "body .st-feedback-card__video{width:56px!important;height:60px!important;max-width:56px!important;max-height:60px!important;flex:0 0 auto!important;object-fit:cover!important;border-radius:8px!important;display:block!important;background:#EDE5DD!important;}\n"
    + "body .st-feedback-card__body{flex:1 1 auto!important;min-width:0!important;display:flex!important;flex-direction:column!important;gap:3px!important;margin-left:8px!important;}\n"
    + "body .st-feedback-card__title{font-size:16px!important;font-weight:600!important;color:#6B5045!important;line-height:1.2!important;margin:0!important;}\n"
    + "body .st-feedback-card__desc{font-size:12px!important;font-weight:400!important;color:#6F6763!important;line-height:1.3!important;margin:0!important;}\n"
    + "body .st-feedback-card__cta{font-size:12px!important;font-weight:600!important;color:var(--st-primary)!important;transition:transform 150ms var(--ease)!important;}\n"
    + "body .st-feedback-card:hover .st-feedback-card__cta{transform:translateX(3px)!important;}\n"
    + "body .st-feedback-card__art{flex:0 0 auto!important;width:40px!important;height:40px!important;display:flex!important;align-items:center!important;justify-content:center!important;}\n"
    + "body .st-feedback-card__art svg{width:40px!important;height:40px!important;display:block!important;}\n"
    + "/* 服务端桥接方案：传统 50% / 50% 等宽分段选择器（暖杏奶油规范） */\n"
    + "body .st-setting{margin:6px 0 0!important;padding:0 14px!important;}\n"
    + "body .st-setting__label{font-size:15px!important;font-weight:500!important;color:var(--st-text)!important;margin:0 0 8px!important;}\n"
    + "body .st-bridge{display:flex!important;width:100%!important;box-sizing:border-box!important;background:var(--st-hover)!important;border:1px solid var(--st-border)!important;border-radius:12px!important;padding:4px!important;gap:4px!important;}\n"
    + "body .st-bridge__seg{flex:1 1 0!important;width:50%!important;min-width:0!important;height:28px!important;display:flex!important;align-items:center!important;justify-content:center!important;padding:0 6px!important;border:none!important;outline:none!important;box-shadow:none!important;border-radius:10px!important;background:transparent!important;color:var(--st-text2)!important;font-size:13px!important;font-weight:500!important;cursor:pointer!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;transition:background 150ms var(--ease),color 150ms var(--ease)!important;}\n"
    + "body .st-bridge__seg:hover{background:var(--st-seg-hover)!important;}\n"
    + "body .st-bridge__seg.is-active{background:var(--st-primary)!important;color:#FFFFFF!important;}\n"
    + "/* 隐私保护：全屏水印遮罩（z-index 6000 全局最高；pointer-events:none 不挡操作与阅读） */\n"
    + "body .st-watermark{position:fixed!important;inset:0!important;z-index:6000!important;pointer-events:none!important;background-repeat:repeat!important;}\n"
    + "/* 设置面板：隐私保护开关 */\n"
    + "body .st-privacy-row{display:flex!important;align-items:center!important;justify-content:space-between!important;}\n"
    + "body .st-privacy-row .st-setting__label{margin:0!important;}\n"
    + "body .st-switch{position:relative!important;display:inline-flex!important;align-items:center!important;width:40px!important;height:22px!important;border-radius:999px!important;background:var(--st-border)!important;cursor:pointer!important;transition:background 150ms var(--ease)!important;flex:0 0 auto!important;}\n"
    + "body .st-switch.is-on{background:var(--st-primary)!important;}\n"
    + "body .st-switch__knob{position:absolute!important;top:2px!important;left:2px!important;width:18px!important;height:18px!important;border-radius:999px!important;background:#fff!important;box-shadow:0 1px 3px rgba(62,56,54,0.25)!important;transition:transform 150ms var(--ease)!important;}\n"
    + "body .st-switch.is-on .st-switch__knob{transform:translateX(18px)!important;}\n"
    + "/* 通用 Modal（居中浮层，共用暖灰遮罩） */\n"
    + "body .st-modal{position:fixed!important;inset:0!important;z-index:4100!important;display:none!important;align-items:center!important;justify-content:center!important;padding:24px!important;}\n"
    + "body .st-modal.is-open{display:flex!important;animation:stFadeIn 180ms var(--ease) both;}\n"
    + "body .st-modal.is-closing{display:flex!important;animation:stFadeOut 160ms var(--ease) both;}\n"
    + "body .st-modal__overlay{position:absolute!important;inset:0!important;background:rgba(62,56,54,0.32)!important;opacity:0!important;transition:opacity 180ms var(--ease)!important;}\n"
    + "body .st-modal.is-open .st-modal__overlay{opacity:1!important;}\n"
    + "body .st-modal.is-closing .st-modal__overlay{opacity:0!important;}\n"
    + "body .st-modal__box{position:relative!important;z-index:1!important;width:440px!important;max-width:100%!important;background:var(--st-surface)!important;border:1px solid var(--st-border)!important;border-radius:12px!important;box-shadow:var(--st-shadow-modal)!important;overflow:hidden!important;animation:stModalIn 220ms var(--ease) both;}\n"
    + "body .st-modal.is-closing .st-modal__box{animation:stModalOut 160ms var(--ease) both;}\n"
    + "body .st-modal__box--password{width:400px!important;}\n"
    + "body .st-modal__pane{padding:22px 22px 18px!important;}\n"
    + "body .st-modal__title{font-size:18px!important;font-weight:600!important;color:var(--st-text)!important;}\n"
    + "body .st-modal__desc{font-size:14px!important;line-height:2.0!important;color:var(--st-text2)!important;margin-top:10px!important;}\n"
    + "body .st-modal__desc2{color:var(--st-text2)!important;}\n"
    + "body .st-modal__actions{display:flex!important;justify-content:flex-end!important;gap:10px!important;margin-top:20px!important;}\n"
    + "/* 表单 */\n"
    + "body .st-field__label{display:block!important;font-size:13px!important;font-weight:500!important;color:var(--st-text)!important;margin:16px 0 6px!important;}\n"
    + "body .st-field__hint{color:var(--st-text2)!important;font-size:12px!important;font-weight:400!important;margin-left:6px!important;}\n"
    + "body .st-input-wrap{position:relative!important;display:flex!important;align-items:center!important;}\n"
    + "body .st-input{width:100%!important;height:40px!important;padding:0 40px 0 12px!important;border:1px solid var(--st-border)!important;border-radius:8px!important;background:var(--st-surface)!important;color:var(--st-text)!important;font-size:14px!important;outline:none!important;transition:border-color 150ms var(--ease)!important,box-shadow 150ms var(--ease)!important;}\n"
    + "body .st-input::placeholder{color:var(--st-disabled-text)!important;}\n"
    + "body .st-input:focus{border-color:var(--st-focus)!important;box-shadow:0 0 0 3px rgba(140,107,93,0.10)!important;}\n"
    + "body .st-input.is-error{border-color:var(--st-error)!important;}\n"
    + "body .st-eye{position:absolute!important;right:4px!important;display:flex!important;align-items:center!important;justify-content:center!important;width:32px!important;height:32px!important;border:none!important;box-shadow:none!important;background:transparent!important;color:var(--st-text2)!important;cursor:pointer!important;border-radius:6px!important;}\n"
    + "body .st-eye:hover{background:var(--st-hover)!important;color:var(--st-primary)!important;}\n"
    + "body .st-eye svg{width:18px!important;height:18px!important;display:block!important;}\n"
    + "body .st-error{display:none!important;color:var(--st-error)!important;font-size:12px!important;line-height:18px!important;margin-top:8px!important;}\n"
    + "body .st-error.is-show{display:block!important;}\n"
    + "/* 按钮 */\n"
    + "body .st-btn{height:36px!important;padding:0 16px!important;border-radius:8px!important;font-size:14px!important;cursor:pointer!important;border:1px solid transparent!important;transition:background 150ms var(--ease)!important,border-color 150ms var(--ease)!important,color 150ms var(--ease)!important;}\n"
    + "body .st-btn--cancel{background:var(--st-surface)!important;border-color:var(--st-border)!important;color:var(--st-text2)!important;}\n"
    + "body .st-btn--cancel:hover{background:var(--st-hover)!important;border-color:#C7A18E!important;color:var(--st-text)!important;}\n"
    + "body .st-btn--primary{background:var(--st-primary)!important;color:#FFFFFF!important;border-color:var(--st-primary)!important;}\n"
    + "body .st-btn--primary:hover{background:var(--st-primary-hover)!important;border-color:var(--st-primary-hover)!important;}\n"
    + "body .st-btn--primary:disabled,body .st-btn--primary[disabled]{background:var(--st-disabled-bg)!important;color:var(--st-disabled-text)!important;cursor:not-allowed!important;border-color:var(--st-disabled-bg)!important;}\n"
    + "body .st-btn--danger{background:var(--st-error)!important;border-color:var(--st-error)!important;color:#FFFFFF!important;}\n"
    + "body .st-btn--danger:hover{background:var(--st-error-hover)!important;border-color:var(--st-error-hover)!important;}\n"
    + "/* Toast（右上角堆叠） */\n"
    + "body .st-toast-stack{position:fixed!important;top:24px!important;right:24px!important;z-index:5000!important;display:flex!important;flex-direction:column!important;gap:10px!important;align-items:flex-end!important;pointer-events:none!important;}\n"
    + "body .st-toast{display:flex!important;align-items:flex-start!important;gap:10px!important;min-width:240px!important;max-width:360px!important;padding:12px 14px!important;background:var(--st-surface)!important;border:1px solid var(--st-border)!important;border-radius:8px!important;box-shadow:0 6px 20px rgba(62,56,54,0.12)!important;color:var(--st-text)!important;font-size:14px!important;line-height:20px!important;animation:stToastIn 180ms var(--ease) both;transition:transform 160ms var(--ease)!important,margin 160ms var(--ease)!important;}\n"
    + "body .st-toast.is-closing{animation:stToastOut 160ms var(--ease) both;}\n"
    + "body .st-toast__icon{flex-shrink:0!important;width:18px!important;height:18px!important;margin-top:1px!important;}\n"
    + "body .st-toast__icon svg{width:18px!important;height:18px!important;display:block!important;}\n"
    + "body .st-toast__msg{flex:1!important;}\n"
    + "/* keyframes */\n"
    + "@keyframes stFadeIn{from{opacity:0}to{opacity:1}}\n"
    + "@keyframes stFadeOut{from{opacity:1}to{opacity:0}}\n"
    + "@keyframes stModalIn{from{opacity:0;transform:translateY(12px) scale(0.985)}to{opacity:1;transform:translateY(0) scale(1)}}\n"
    + "@keyframes stModalOut{from{opacity:1;transform:translateY(0) scale(1)}to{opacity:0;transform:translateY(8px) scale(0.99)}}\n"
    + "/* 反馈问卷 Modal */\n"
    + "body .st-modal__box--feedback{width:560px!important;max-width:calc(100vw - 48px)!important;max-height:calc(92vh - 48px)!important;background:var(--st-modal-bg)!important;border:1px solid var(--st-border)!important;border-radius:16px!important;box-shadow:0 16px 48px rgba(107,80,69,0.12)!important;}\n"
    + "body .fb-modal{display:flex!important;flex-direction:column!important;width:100%!important;max-height:calc(92vh - 48px)!important;}\n"
    + "body .fb-modal__head{display:flex!important;align-items:flex-start!important;justify-content:space-between!important;gap:12px!important;padding:24px 28px 20px!important;}\n"
    + "body .fb-modal__title{font-size:20px!important;font-weight:600!important;line-height:28px!important;color:var(--st-text)!important;}\n"
    + "body .fb-modal__sub{margin-top:6px!important;font-size:13px!important;font-weight:400!important;line-height:20px!important;color:var(--st-text2)!important;}\n"
    + "body .fb-modal__close{display:flex!important;align-items:center!important;justify-content:center!important;width:32px!important;height:32px!important;flex-shrink:0!important;border:none!important;background:transparent!important;color:var(--st-text2)!important;border-radius:8px!important;cursor:pointer!important;transition:background 150ms var(--ease),color 150ms var(--ease)!important;}\n"
    + "body .fb-modal__close:hover{background:var(--st-hover)!important;color:var(--st-text)!important;}\n"
    + "body .fb-modal__close svg{width:16px!important;height:16px!important;display:block!important;}\n"
    + "body .fb-modal__body{flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;padding:4px 28px 24px!important;scrollbar-width:thin!important;scrollbar-color:rgba(111,103,99,0.2) transparent!important;transition:scrollbar-color 150ms var(--ease)!important;}\n"
    + "body .fb-modal__body::-webkit-scrollbar{width:8px!important;}\n"
    + "body .fb-modal__body::-webkit-scrollbar-track{background:transparent!important;}\n"
    + "body .fb-modal__body::-webkit-scrollbar-thumb{background:rgba(111,103,99,0.2)!important;border-radius:4px!important;}\n"
    + "body .fb-modal__body::-webkit-scrollbar-thumb:hover{background:#6F6763!important;}\n"
    + "body .fb-modal:hover .fb-modal__body::-webkit-scrollbar-thumb{background:rgba(111,103,99,0.5)!important;}\n"
    + "body .fb-modal:hover .fb-modal__body{scrollbar-color:rgba(111,103,99,0.5) transparent!important;}\n"
    + "body .fb-modal__body .fb-modal__sub{margin:2px 0 16px!important;}\n"
    + "body .fb-modal__foot{display:flex!important;justify-content:flex-end!important;gap:10px!important;padding:18px 28px 20px!important;border-top:1px solid var(--st-border)!important;}\n"
    + "body .fb-field{margin-bottom:20px!important;}\n"
    + "body .fb-field:last-child{margin-bottom:0!important;}\n"
    + "body .fb-label{display:block!important;font-size:14px!important;font-weight:500!important;color:var(--st-text)!important;margin:0 0 8px!important;}\n"
    + "body .fb-req{color:var(--st-error)!important;margin-left:4px!important;font-weight:500!important;}\n"
    + "body .fb-opt{color:var(--st-group)!important;font-weight:400!important;margin-left:4px!important;}\n"
    + "body .fb-modal .st-input{height:44px!important;border-radius:10px!important;background:var(--st-surface)!important;border:1px solid var(--st-border)!important;color:var(--st-text)!important;padding:0 14px!important;font-size:14px!important;transition:border-color 150ms var(--ease),box-shadow 150ms var(--ease),background 150ms var(--ease)!important;}\n"
    + "body .fb-modal .st-input:hover{border-color:var(--st-input-hover-border)!important;background:#FFFCF9!important;}\n"
    + "body .fb-modal .st-input:focus{border-color:var(--st-input-focus)!important;box-shadow:0 0 0 3px rgba(199,161,142,0.15)!important;background:var(--st-surface)!important;}\n"
    + "body .fb-modal .st-input::placeholder{color:var(--st-placeholder)!important;}\n"
    + "body .fb-modal .st-input.is-error{border-color:var(--st-error)!important;}\n"
    + "/* 自定义下拉（替代原生 select） */\n"
    + "body .fb-modal .fb-select{position:relative!important;width:100%!important;}\n"
    + "body .fb-modal .fb-select.fb-contact__type{width:132px!important;flex:0 0 132px!important;}\n"
    + "body .fb-modal .fb-select__trigger{display:flex!important;align-items:center!important;justify-content:space-between!important;height:44px!important;border-radius:10px!important;background:var(--st-surface)!important;border:1px solid var(--st-border)!important;color:var(--st-text)!important;padding:0 14px!important;font-size:14px!important;cursor:pointer!important;transition:border-color 150ms var(--ease),box-shadow 150ms var(--ease),background 150ms var(--ease)!important;}\n"
    + "body .fb-modal .fb-select__trigger:hover{border-color:var(--st-input-hover-border)!important;background:#FFFCF9!important;}\n"
    + "body .fb-modal .fb-select.is-open .fb-select__trigger,body .fb-modal .fb-select__trigger:focus{border-color:var(--st-input-focus)!important;box-shadow:0 0 0 3px rgba(199,161,142,0.15)!important;background:var(--st-surface)!important;outline:none!important;}\n"
    + "body .fb-modal .fb-select__value{overflow:hidden!important;white-space:nowrap!important;text-overflow:ellipsis!important;}\n"
    + "body .fb-modal .fb-select__value.is-placeholder{color:var(--st-placeholder)!important;}\n"
    + "body .fb-modal .fb-select__arrow{display:inline-flex!important;align-items:center!important;justify-content:center!important;color:var(--st-text2)!important;margin-left:8px!important;flex:0 0 auto!important;}\n"
    + "body .fb-modal .fb-select__arrow svg{width:16px!important;height:16px!important;display:block!important;}\n"
    + "body .fb-select__dropdown{display:none!important;position:fixed!important;z-index:5000!important;box-sizing:border-box!important;background:var(--st-modal-bg)!important;border:1px solid var(--st-border)!important;border-radius:10px!important;box-shadow:0 8px 24px rgba(107,80,69,0.10)!important;padding:8px!important;max-height:240px!important;overflow-y:auto!important;}\n"
    + "body .fb-select__dropdown.is-open{display:block!important;}\n"
    + "body .fb-select__option{display:flex!important;align-items:center!important;justify-content:space-between!important;height:40px!important;padding:0 18px!important;border-radius:8px!important;color:var(--st-text)!important;font-size:14px!important;cursor:pointer!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;transition:background 150ms var(--ease)!important;}\n"
    + "body .fb-select__option:hover{background:var(--st-hover)!important;}\n"
    + "body .fb-select__option.is-selected{background:var(--st-select-active)!important;color:#6B5045!important;font-weight:500!important;}\n"
    + "body .fb-select__option.is-selected::after{content:\"\\2713\"!important;margin-left:8px!important;color:#6B5045!important;font-weight:600!important;}\n"
    + "body .fb-modal textarea.st-input{padding:12px 14px!important;line-height:22px!important;}\n"
    + "body .fb-nest{margin-top:12px!important;padding-left:12px!important;border-left:2px solid var(--st-nest-line)!important;}\n"
    + "body .fb-nest__label{margin-top:0!important;}\n"
    + "body .fb-contact{display:flex!important;gap:8px!important;}\n"
    + "body .fb-contact__type{width:132px!important;flex:0 0 132px!important;}\n"
    + "body .fb-contact__input{flex:1 1 auto!important;min-width:0!important;}\n"
    + "body .fb-textarea-wrap{position:relative!important;}\n"
    + "body .fb-modal textarea.st-input{height:auto!important;min-height:128px!important;max-height:160px!important;resize:none!important;overflow-y:auto!important;}\n"
    + "body .fb-count{position:absolute!important;right:12px!important;bottom:10px!important;font-size:12px!important;color:var(--st-placeholder)!important;pointer-events:none!important;}\n"
    + "body .fb-modal__foot .st-btn{height:40px!important;border-radius:10px!important;font-size:14px!important;}\n"
    + "body .fb-modal__foot .st-btn--cancel{background:transparent!important;color:var(--st-text2)!important;border:1px solid transparent!important;}\n"
    + "body .fb-modal__foot .st-btn--cancel:hover{background:var(--st-hover)!important;color:var(--st-text)!important;}\n"
    + "body .fb-modal__foot .st-btn--primary:disabled,body .fb-modal__foot .st-btn--primary[disabled]{background:var(--st-disabled-bg)!important;color:#A59B95!important;cursor:not-allowed!important;border-color:var(--st-disabled-bg)!important;}\n"
    + "body .fb-modal.is-success .fb-modal__head,body .fb-modal.is-success .fb-modal__body,body .fb-modal.is-success .fb-modal__foot{display:none!important;}\n"
    + "body .fb-success{display:none!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;text-align:center!important;padding:40px 28px!important;min-height:280px!important;gap:14px!important;}\n"
    + "body .fb-modal.is-success .fb-success{display:flex!important;}\n"
    + "body .fb-success__icon{display:flex!important;align-items:center!important;justify-content:center!important;width:48px!important;height:48px!important;border-radius:50%!important;background:var(--st-success-bg)!important;color:var(--st-success)!important;}\n"
    + "body .fb-success__icon svg{width:24px!important;height:24px!important;display:block!important;}\n"
    + "body .fb-success__title{font-size:20px!important;font-weight:600!important;color:var(--st-text)!important;}\n"
    + "body .fb-success__desc{font-size:14px!important;line-height:22px!important;color:var(--st-text2)!important;max-width:360px!important;}\n"
    + "body .fb-success__btn{margin-top:6px!important;height:40px!important;border-radius:10px!important;padding:0 20px!important;background:var(--st-primary)!important;color:#FFFFFF!important;border:1px solid var(--st-primary)!important;font-size:14px!important;cursor:pointer!important;transition:background 150ms var(--ease)!important;}\n"
    + "body .fb-success__btn:hover{background:var(--st-primary-hover)!important;border-color:var(--st-primary-hover)!important;}\n"
    + "/* 反馈引导气泡（B方案：锚定左下角设置图，箭头向下指图；纯 DOM+CSS 绘制） */\n"
    + "body .fb-guide{position:fixed!important;z-index:3950!important;}\n"
    + "body .fb-guide__bubble{position:relative!important;display:flex!important;align-items:center!important;gap:12px!important;background:var(--st-surface,#FFFFFF)!important;border:2px solid var(--st-border,#EDE5DD)!important;border-radius:12px!important;box-shadow:var(--st-shadow-panel,0 8px 24px rgba(62,56,54,0.10))!important;padding:12px!important;animation:fbGuideIn 240ms var(--st-ease,cubic-bezier(0.4,0,0.2,1)) both!important;}\n"
    + "body .fb-guide__img{flex:0 0 auto!important;width:90px!important;height:90px!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:hidden!important;border-radius:12px!important;}\n"
    + "body .fb-guide__img img{width:78%!important;height:78%!important;object-fit:contain!important;display:block!important;animation:fbGuideImgBob 2.4s ease-in-out infinite!important;}\n"
    + "body .fb-guide__body{flex:1 1 auto!important;min-width:0!important;}\n"
    + "body .fb-guide__title{font-size:13px!important;line-height:20px!important;color:var(--st-text,#3E3836)!important;padding-right:18px!important;}\n"
    + "body .fb-guide__actions{display:flex!important;align-items:center!important;gap:10px!important;margin-top:10px!important;}\n"
    + "body .fb-guide__btn{height:32px!important;padding:0 12px!important;border-radius:8px!important;border:1px solid var(--st-border,#EDE5DD)!important;background:#FFFFFF!important;color:var(--st-text,#3E3836)!important;font-size:13px!important;cursor:pointer!important;transition:background 150ms var(--st-ease,cubic-bezier(0.4,0,0.2,1))!important;}\n"
    + "body .fb-guide__btn:hover{background:var(--st-hover,#FAF3EC)!important;}\n"
    + "body .fb-guide__btn--primary{background:var(--st-primary,#C7A18E)!important;color:#FFFFFF!important;border-color:var(--st-primary,#C7A18E)!important;}\n"
    + "body .fb-guide__btn--primary:hover{background:var(--st-primary-hover,#B98F7C)!important;border-color:var(--st-primary-hover,#B98F7C)!important;}\n"
    + "body .fb-guide__link{height:auto!important;padding:0!important;border:none!important;background:transparent!important;color:var(--st-text2,#6F6763)!important;font-size:10px!important;line-height:1!important;cursor:pointer!important;}\n"
    + "body .fb-guide__link:hover{color:var(--st-primary,#C7A18E)!important;text-decoration:underline!important;}\n"
    + "body .fb-guide__close{position:absolute!important;top:6px!important;right:8px!important;border:none!important;background:transparent!important;color:var(--st-text2,#6F6763)!important;font-size:18px!important;line-height:1!important;cursor:pointer!important;padding:2px!important;}\n"
    + "body .fb-guide__arrow{position:absolute!important;left:-7px!important;top:50%!important;width:14px!important;height:14px!important;background:var(--st-surface,#FFFFFF)!important;border-left:1px solid var(--st-border,#EDE5DD)!important;border-top:1px solid var(--st-border,#EDE5DD)!important;transform:translateY(-50%) rotate(45deg)!important;animation:fbArrowBounce 1.2s ease-in-out infinite!important;}\n"
    + "@keyframes fbGuideIn{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:translateX(0)}}\n"
    + "@keyframes fbArrowBounce{0%,100%{transform:translateY(-50%) translateX(0) rotate(45deg)}50%{transform:translateY(-50%) translateX(-4px) rotate(45deg)}}\n"
    + "@keyframes fbGuideImgBob{0%,100%{transform:translateY(-3px)}50%{transform:translateY(3px)}}\n"
    + "@keyframes stPanelIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}\n"
    + "@keyframes stPanelOut{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(6px)}}\n"
    + "@keyframes stToastIn{from{opacity:0;transform:translateX(100%)}to{opacity:1;transform:translateX(0)}}\n"
    + "@keyframes stToastOut{from{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(100%)}}\n"
    + "@keyframes stContentOut{from{opacity:1;transform:translateX(0)}to{opacity:0;transform:translateX(-10px)}}\n"
    + "@keyframes stContentIn{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:translateX(0)}}\n"
    + "</style>"
)


# ---------------------------------------------------------------------------
# 后端推理入口：通过 gr.HTML 的 server_functions 暴露给前端 JS
# ---------------------------------------------------------------------------
_pipeline = Pipeline()


def respond(
    user_input: str,
    context_entities: list[str] | None = None,
    backend: str = "local",
) -> dict:
    """执行一次推理，返回 JSON 友好的结果（含执行轨迹）。

    该函数通过 server_functions=[respond] 暴露给前端，JS 中以
    `await server.respond(text, contextEntities, backend)` 调用。
    context_entities 为上一轮成功解析的实体（上下文），供连续对话实体继承。
    backend 为本次查询使用的数据源（"local" / "neo4j"），默认本地；
    仅影响本次调用，不修改全局 GRAPH_BACKEND 配置。

    注意：Gradio 的 server_functions 在多参数调用时会把参数序列化为数组
    data=[user_input, context_entities, backend]，但后端 component_server 不展开该数组，
    导致第一个参数收到整个 list。这里手动拆分以兼容多参数调用。
    返回值必须是可 JSON 序列化的纯 dict。
    """
    if isinstance(user_input, list):
        # 多参数调用被压成单个数组，这里手动展开（用临时变量避免名称遮蔽导致索引错位）
        _args = user_input
        user_input = _args[0] if _args else user_input
        context_entities = _args[1] if len(_args) > 1 else None
        backend = _args[2] if len(_args) > 2 else "local"
    response, trace = _pipeline.run_with_trace(user_input, context_entities, backend=backend)
    return {
        "status": response.status.value,
        "summary": response.summary,
        "intent": response.intent.value if response.intent else None,
        "entities": response.entities,
        "boundary_hint": response.boundary_hint,
        "error_message": response.error_message,
        "clarify_options": [
            {"label": o.label, "value": o.value} for o in response.clarify_options
        ],
        "trace": {
            "user_input": trace.user_input,
            "input_type": trace.input_type,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_name": s.step_name,
                    "agent": s.agent,
                    "status": s.status,
                    "input_summary": s.input_summary,
                    "output_summary": s.output_summary,
                    "detail": s.detail,
                    "skip_reason": s.skip_reason,
                }
                for s in trace.steps
            ],
        },
    }


# ---------------------------------------------------------------------------
# 飞书日志 server_functions
#
# 由前端（_JS_EXEC 内 JS）通过 server.log_behavior / server.log_feedback 调用。
# 设计要点：
# - 前端只传一个 dict（规避 Gradio server_functions 多参数被压平的坑）；
#   IP / User-Agent 由 gr.Request 在服务端提取（优先 X-Forwarded-For / X-Real-IP），
#   不在前端传值，故即使 request 注入不可用也不抛异常（降级为空）。
# - 时间戳在服务端生成，确保同一事件（如反馈）的行为表与反馈表时间一致。
# - 写入在守护线程中异步进行（fire-and-forget），不阻塞主流程；
#   异常已在 FeishuLogger 内静默处理。
# ---------------------------------------------------------------------------
def _coerce_payload(payload):
    """server_functions 多参数调用时 Gradio 会把参数压成列表，这里统一规整为 dict。"""
    if isinstance(payload, list):
        if len(payload) == 1 and isinstance(payload[0], dict):
            payload = payload[0]
        else:
            return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _extract_request_meta(request):
    """从 gr.Request 提取客户端 IP 与 User-Agent；失败时返回空字符串（不抛异常）。"""
    ip_address = ""
    user_agent = ""
    if request is None:
        return ip_address, user_agent
    try:
        headers = getattr(request, "headers", None) or {}
        # 优先取代理透传的真实客户端 IP（反向代理 / ModelScope 网关场景）
        xff = headers.get("x-forwarded-for") or headers.get("X-Forwarded-For")
        if xff:
            ip_address = str(xff).split(",")[0].strip()
        if not ip_address:
            xri = headers.get("x-real-ip") or headers.get("X-Real-IP")
            if xri:
                ip_address = str(xri).strip()
        if not ip_address:
            client = getattr(request, "client", None)
            if client is not None:
                ip_address = getattr(client, "host", "") or ""
        user_agent = headers.get("user-agent") or headers.get("User-Agent") or ""
        if isinstance(user_agent, bytes):
            user_agent = user_agent.decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        pass
    return ip_address, user_agent


def log_behavior(payload: dict, request: gr.Request = None):
    """由前端调用：记录一次用户行为（page_view / question / feedback 等）。"""
    data = _coerce_payload(payload)
    user_id = str(data.get("user_id", ""))
    behavior_type = str(data.get("behavior_type", ""))
    behavior_value = str(data.get("behavior_value", ""))
    # 优先用服务端从 request 提取的 UA，前端可附带 navigator.userAgent 作为兜底
    ip_address, req_ua = _extract_request_meta(request)
    user_agent = req_ua or str(data.get("user_agent", ""))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threading.Thread(
        target=logger.log_behavior,
        args=(user_id, behavior_type, behavior_value, ip_address, user_agent, timestamp),
        daemon=True,
    ).start()


def log_feedback(payload: dict, request: gr.Request = None):
    """由前端调用：记录一次用户反馈（同时写入反馈表与行为流水表）。"""
    data = _coerce_payload(payload)
    user_id = str(data.get("user_id", ""))
    name = str(data.get("name", ""))
    source = str(data.get("source", ""))
    contact_type = str(data.get("contact_type", ""))
    contact = str(data.get("contact", ""))
    content = str(data.get("content", ""))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threading.Thread(
        target=logger.log_feedback,
        args=(user_id, name, source, contact_type, contact, content, timestamp),
        daemon=True,
    ).start()


def log_feedback_behavior(payload: dict, request: gr.Request = None):
    """由前端调用：反馈提交成功后，在行为流水表写入一条 feedback 行为。"""
    data = _coerce_payload(payload)
    user_id = str(data.get("user_id", ""))
    ip_address, req_ua = _extract_request_meta(request)
    user_agent = req_ua or str(data.get("user_agent", ""))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threading.Thread(
        target=logger.log_feedback_behavior,
        args=(user_id, ip_address, user_agent, timestamp),
        daemon=True,
    ).start()


def create_demo() -> gr.Blocks:
    """构建 Gradio 应用实例。"""
    with gr.Blocks(
        title="潘的宠医助手 · FIP知识推理系统",
    ) as demo:
        # 静态首页：所有内容通过 HTML 注入，便于完全控制布局与动效
        # 样式经 head 注入；交互 JS 经 js_on_load 注入（Gradio 官方保证执行，
        # head 中的内联 <script> 可能被前端以 innerHTML 方式插入而不执行）
        # server_functions 把 respond 暴露给 JS：await server.respond(text)
        gr.HTML(
            _HOME_HTML,
            # 全局 CSS 经 gr.HTML 的 head 注入（Gradio 6.x 会把它渲染进组件 body，
            # <style> 在 body 中同样生效）；favicon 不再放这里——body 里的
            # <link rel="icon"> 浏览器忽略，需走 launch(head=...) 注入真实 <head>。
            head=_STYLE_HTML,
            js_on_load=_JS_EXEC,
            server_functions=[respond, log_behavior, log_feedback, log_feedback_behavior],
        )
    return demo


# 注入 system_default 默认对话种子：读取 data/seed_conversations.json，base64 包裹后替换 JS_CODE 占位符，
# 避免破坏 JS_CODE 的三引号字符串或其中的特殊字符（如 U+2028 / 引号 / 反斜杠）。
import base64 as _b64, json as _json
_seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "seed_conversations.json")
try:
    with open(_seed_path, encoding="utf-8") as _f:
        _seed_obj = _json.load(_f)
    _seed_b64 = _b64.b64encode(_json.dumps(_seed_obj, ensure_ascii=False).encode("utf-8")).decode("ascii")
    # JS 的 atob 返回 Latin-1 二进制串，必须先把字节还原成 Uint8Array，再用 TextDecoder 按 UTF-8 解码，
    # 否则中文会被逐字节当 Unicode 码点解析 → JSON.parse 后标题/内容全部乱码。
    _seed_inline = '(function(){var b=atob("%s"),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return JSON.parse(new TextDecoder().decode(u));})()' % _seed_b64
except Exception:
    _seed_inline = "[]"
# 关键：launch 使用的是 _JS_EXEC（在 JS_CODE 基础上派生并替换了 graph/docs/design/style-demo 占位符），
# 种子占位符必须同时注入 _JS_EXEC，否则线上 __SEED_PLACEHOLDER__ 残留为裸标识符 → eval 期 ReferenceError 炸掉整段 JS。
JS_CODE = JS_CODE.replace("__SEED_PLACEHOLDER__", _seed_inline)
_JS_EXEC = _JS_EXEC.replace("__SEED_PLACEHOLDER__", _seed_inline)

demo = create_demo()


if __name__ == "__main__":
    # 端口可由环境变量 GRADIO_PORT 覆盖，方便绕过浏览器缓存（浏览器按 URL 缓存 HTML）：
    #   GRADIO_PORT=7862 python app.py
    _port = int(os.environ.get("GRADIO_PORT", "7860"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=_port,
        show_error=True,
        inbrowser=False,
        quiet=False,
        allowed_paths=["source/literature", "asset"],
        # favicon 真正生效的三道保险：
        # 1) launch(head=...) 把 <link rel="icon"> 注入真实 <head>（消除静态闪烁）；
        # 2) favicon_path 让 /favicon.ico 路由返回我们的 png（浏览器兜底）；
        # 3) js_on_load 中的强制保持逻辑（MutationObserver）压制 Gradio 运行时覆盖。
        head='<link rel="icon" type="image/png" href="/gradio_api/file=asset/favicon.png" />',
        favicon_path="asset/favicon.png",
    )
