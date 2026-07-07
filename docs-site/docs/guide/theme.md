# 主题样式 (Theme Styles)

MonkeyQt 内置了极其强大、丰富的**主题样式**。它包含 **68 种不同的 UI 设计风格**（包括极简亮色、极简瑞士风、新拟物化、玻璃拟态、粗野主义、赛博朋克、HUD 科幻、墨水屏风格等），并提供了全局一键切换和自动样式应用功能。

---

## 核心概念

MonkeyQt 的主题样式通过以下几个核心组件协同工作：

1. **`ThemeEngine`（风格引擎）**：全局唯一的单例，负责管理当前活跃主题 learnings / Design Tokens（颜色、圆角、边框、模糊度等）和构建应用级的全局样式表 (QSS)。
2. **自动应用机制 (`_ThemeAutoApplier`)**：当开启自动模式时，系统会实时检测新实例化的组件并自动为其涂装当前主题的对应样式，开发者无需手动进行二次配置。
3. **`Mk` 系列组件**：主题引擎与所有 `Mk` 核心组件天然整合，并内置主题自适应渲染与抗锯齿细节，以在不同主题下达到最佳的视觉效果。

---

## 基础用法

### 1. 全局启用并应用主题

推荐使用全局便捷入口函数 `use_theme`，它会自动监听新创建的组件并应用样式：

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from monkeyqt import use_theme, MkButton, MkInput

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 💡 在创建任何窗口前，指定全局主题
    # 选项例如："Glassmorphism" (玻璃拟态), "Neumorphism" (新拟物化), "Cyberpunk UI" (赛博朋克)
    use_theme("Glassmorphism")
    
    window = QWidget()
    window.setWindowTitle("主题应用示例")
    window.resize(320, 200)
    
    layout = QVBoxLayout(window)
    layout.addWidget(MkInput("用户名"))
    layout.addWidget(MkButton("确认", type="primary"))
    
    window.show()
    sys.exit(app.exec())
```

### 2. 运行时动态切换主题

如果需要在程序运行中（例如点击按钮时）切换主题，可以直接调用 `ThemeEngine.set_theme`：

```python
from monkeyqt import ThemeEngine

# 切换到赛博朋克风格
ThemeEngine.set_theme("Cyberpunk UI")

# 恢复默认样式（雅致亮色）
ThemeEngine.clear_theme()
```

---

## 高级定制 API

### 1. 局部重写铬黄/框架配色 (Chrome Override)

如果你想对当前主题的标题栏（TitleBar）和侧边栏（Sidebar）进行特别的外观颜色重写，可以使用 `set_theme_chrome`：

```python
from monkeyqt import set_theme_chrome

# 独立定制标题栏和侧边栏的背景色
set_theme_chrome(titlebar_bg="#1e1e2e", sidebar_bg="#181825")

# 还原到主题自带的默认分配色
from monkeyqt import clear_theme_chrome
clear_theme_chrome()
```

### 2. 排除或包含特定组件

如果有些特定的自定义组件您想**保持自己原本的样式表 (StyleSheet) 或绘图逻辑，不被全局主题机制所覆盖**，可以将其排除在外：

```python
from monkeyqt import exclude_from_theme, include_in_theme

# 将 my_widget 及其子组件排除在主题引擎的控制之外
exclude_from_theme(my_widget)

# 重新将该组件加入主题受控范围
include_in_theme(my_widget)
```

### 3. 自定义组件的默认样式与免 QSS 配置说明

为了降低开发者的样式配置负担，所有 `Mk` 核心组件（如 `MkCheckBox` 复选框、`MkComboBox` 下拉框、`MkInput` 输入框等）都内置了完整且高清的样式与绘图资源（例如：复选框在各种操作系统及 Qt 环境下均可无缝渲染出高清 SVG 矢量打勾图标，且在高级数据表格 `MkDataTable` 中会自动完成完美对齐）。

* **无需额外重写 QSS**：无需像传统 PySide 开发那样在外部为主程序或组件书写复杂的边框、对齐、或者 `::indicator` 选中态图片样式，主题引擎在切换主题时会自动向这些内置组件应用最适配的视觉呈现。
* **避免样式覆盖冲突**：如果为内置组件自定义了特殊的样式表，请尽量使用特定的类选择器或局部覆盖，避免与主题引擎的 Design Tokens 产生冲突。

---

## 内置主题选择器 (`MkThemeSelector`)

MonkeyQt 提供了一个开箱即用的主题下拉选择器 `MkThemeSelector`，可直接拖放到标题栏或设置面板中，实现真正的全站主题热重载。

### 示例代码

```python
from monkeyqt import MkWindow, MkThemeSelector, MkButton
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout
import sys

class ThemeSelectorDemo(MkWindow):
    def __init__(self):
        super().__init__(use_custom_title_bar=True, preset="default")
        self.setWindowTitle("主题切换控制台")
        self.resize(600, 400)
        
        # 1. 实例化主题选择器并将其加入自定义标题栏中
        self.selector = MkThemeSelector()
        self.titlebar.center_layout.addWidget(self.selector)
        
        # 2. 页面主体内容
        content = QFrame()
        layout = QVBoxLayout(content)
        layout.addWidget(MkButton("主题测试按钮", type="primary"))
        self.setCentralWidget(content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThemeSelectorDemo()
    window.show()
    sys.exit(app.exec())
```

---

## 风格视觉预览 (Style Previews)

以下是几款代表性主题在 MonkeyQt 组件演示大厅 (MainGallery) 下的实时渲染截图预览（点击下方小圆点可自由滑动切换）：

<div class="theme-carousel">
  <input type="radio" name="slider" id="slide1" checked>
  <input type="radio" name="slider" id="slide2">
  <input type="radio" name="slider" id="slide3">
  <input type="radio" name="slider" id="slide4">
  <input type="radio" name="slider" id="slide5">
  <input type="radio" name="slider" id="slide6">
  <input type="radio" name="slider" id="slide7">
  <input type="radio" name="slider" id="slide8">
  <input type="radio" name="slider" id="slide9">
  <input type="radio" name="slider" id="slide10">
  <input type="radio" name="slider" id="slide11">
  <input type="radio" name="slider" id="slide12">
  <input type="radio" name="slider" id="slide13">
  <input type="radio" name="slider" id="slide14">
  <input type="radio" name="slider" id="slide15">
  <input type="radio" name="slider" id="slide16">
  <input type="radio" name="slider" id="slide17">
  <input type="radio" name="slider" id="slide18">
  <input type="radio" name="slider" id="slide19">
  <input type="radio" name="slider" id="slide20">
  <input type="radio" name="slider" id="slide21">
  <input type="radio" name="slider" id="slide22">
  <input type="radio" name="slider" id="slide23">
  <input type="radio" name="slider" id="slide24">
  <input type="radio" name="slider" id="slide25">
  
  <div class="slides">
    <div class="slide slide-1">
      <div class="slide-content">
        <label for="slide25" class="prev-zone" title="上一张"></label>
        <label for="slide2" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_glassmorphism.png" alt="Glassmorphism">
      </div>
      <div class="slide-caption">1. 玻璃拟态 (Glassmorphism) - 按钮组件</div>
    </div>
    <div class="slide slide-2">
      <div class="slide-content">
        <label for="slide1" class="prev-zone" title="上一张"></label>
        <label for="slide3" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_neumorphism.png" alt="Neumorphism">
      </div>
      <div class="slide-caption">2. 新拟物化 (Neumorphism) - 表单录入</div>
    </div>
    <div class="slide slide-3">
      <div class="slide-content">
        <label for="slide2" class="prev-zone" title="上一张"></label>
        <label for="slide4" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_cyberpunk.png" alt="Cyberpunk UI">
      </div>
      <div class="slide-caption">3. 赛博朋克 (Cyberpunk UI) - 反馈提示</div>
    </div>
    <div class="slide slide-4">
      <div class="slide-content">
        <label for="slide3" class="prev-zone" title="上一张"></label>
        <label for="slide5" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_brutalism.png" alt="Brutalism">
      </div>
      <div class="slide-caption">4. 粗野主义 (Brutalism) - 基础数据</div>
    </div>
    <div class="slide slide-5">
      <div class="slide-content">
        <label for="slide4" class="prev-zone" title="上一张"></label>
        <label for="slide6" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_e_ink.png" alt="E-Ink / Paper">
      </div>
      <div class="slide-caption">5. 电子墨水屏 (E-Ink / Paper) - 高级数据表格</div>
    </div>
    <div class="slide slide-6">
      <div class="slide-content">
        <label for="slide5" class="prev-zone" title="上一张"></label>
        <label for="slide7" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_hud_scifi.png" alt="HUD / Sci-Fi FUI">
      </div>
      <div class="slide-caption">6. HUD 科幻界面 (HUD / Sci-Fi FUI) - 自定义窗口</div>
    </div>
    <div class="slide slide-7">
      <div class="slide-content">
        <label for="slide6" class="prev-zone" title="上一张"></label>
        <label for="slide8" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_claymorphism.png" alt="Claymorphism">
      </div>
      <div class="slide-caption">7. 黏土拟态 (Claymorphism) - 登录与注册授权</div>
    </div>
    <div class="slide slide-8">
      <div class="slide-content">
        <label for="slide7" class="prev-zone" title="上一张"></label>
        <label for="slide9" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_aurora.png" alt="Aurora UI">
      </div>
      <div class="slide-caption">8. 极光 UI (Aurora UI) - 标签页与分页器</div>
    </div>
    <div class="slide slide-9">
      <div class="slide-content">
        <label for="slide8" class="prev-zone" title="上一张"></label>
        <label for="slide10" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_vaporwave.png" alt="Vaporwave">
      </div>
      <div class="slide-caption">9. 蒸汽波 (Vaporwave) - 双图对比</div>
    </div>
    <div class="slide slide-10">
      <div class="slide-content">
        <label for="slide9" class="prev-zone" title="上一张"></label>
        <label for="slide11" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_bento.png" alt="Bento Box Grid">
      </div>
      <div class="slide-caption">10. 便当盒网格 (Bento Box Grid) - 文件上传</div>
    </div>
    <div class="slide slide-11">
      <div class="slide-content">
        <label for="slide10" class="prev-zone" title="上一张"></label>
        <label for="slide12" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_minimalism.png" alt="Minimalism & Swiss Style">
      </div>
      <div class="slide-caption">11. 极简瑞士风格 (Minimalism & Swiss Style) - 按钮组件</div>
    </div>
    <div class="slide slide-12">
      <div class="slide-content">
        <label for="slide11" class="prev-zone" title="上一张"></label>
        <label for="slide13" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_hyperrealism.png" alt="3D & Hyperrealism">
      </div>
      <div class="slide-caption">12. 3D与超现实 (3D & Hyperrealism) - 自定义窗口</div>
    </div>
    <div class="slide slide-13">
      <div class="slide-content">
        <label for="slide12" class="prev-zone" title="上一张"></label>
        <label for="slide14" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_vibrant.png" alt="Vibrant & Block-based">
      </div>
      <div class="slide-caption">13. 活力方块 (Vibrant & Block-based) - 信息提示与进度</div>
    </div>
    <div class="slide slide-14">
      <div class="slide-content">
        <label for="slide13" class="prev-zone" title="上一张"></label>
        <label for="slide15" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_oled.png" alt="Dark Mode (OLED)">
      </div>
      <div class="slide-caption">14. 深色 OLED (Dark Mode (OLED)) - 高级数据表格</div>
    </div>
    <div class="slide slide-15">
      <div class="slide-content">
        <label for="slide14" class="prev-zone" title="上一张"></label>
        <label for="slide16" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_accessible.png" alt="Accessible & Ethical">
      </div>
      <div class="slide-caption">15. 无障碍友好 (Accessible & Ethical) - 表单录入</div>
    </div>
    <div class="slide slide-16">
      <div class="slide-content">
        <label for="slide15" class="prev-zone" title="上一张"></label>
        <label for="slide17" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_retro_futurism.png" alt="Retro-Futurism">
      </div>
      <div class="slide-caption">16. 复古未来主义 (Retro-Futurism) - 登录与注册授权</div>
    </div>
    <div class="slide slide-17">
      <div class="slide-content">
        <label for="slide16" class="prev-zone" title="上一张"></label>
        <label for="slide18" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_flat.png" alt="Flat Design">
      </div>
      <div class="slide-caption">17. 扁平化设计 (Flat Design) - 面包屑与标签页等</div>
    </div>
    <div class="slide slide-18">
      <div class="slide-content">
        <label for="slide17" class="prev-zone" title="上一张"></label>
        <label for="slide19" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_skeuomorphism.png" alt="Skeuomorphism">
      </div>
      <div class="slide-caption">18. 拟物化风格 (Skeuomorphism) - 头像与表格</div>
    </div>
    <div class="slide slide-19">
      <div class="slide-content">
        <label for="slide18" class="prev-zone" title="上一张"></label>
        <label for="slide20" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_liquid_glass.png" alt="Liquid Glass">
      </div>
      <div class="slide-caption">19. 流态玻璃 (Liquid Glass) - 图像对比</div>
    </div>
    <div class="slide slide-20">
      <div class="slide-content">
        <label for="slide19" class="prev-zone" title="上一张"></label>
        <label for="slide21" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_y2k.png" alt="Y2K Aesthetic">
      </div>
      <div class="slide-caption">20. Y2K 潮酷美学 (Y2K Aesthetic) - 文件上传</div>
    </div>
    <div class="slide slide-21">
      <div class="slide-content">
        <label for="slide20" class="prev-zone" title="上一张"></label>
        <label for="slide22" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_ai_native.png" alt="AI-Native UI">
      </div>
      <div class="slide-caption">21. AI 原生界面 (AI-Native UI) - 按钮组件</div>
    </div>
    <div class="slide slide-22">
      <div class="slide-content">
        <label for="slide21" class="prev-zone" title="上一张"></label>
        <label for="slide23" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_memphis.png" alt="Memphis Design">
      </div>
      <div class="slide-caption">22. 孟菲斯设计 (Memphis Design) - 开关、滑块与日期</div>
    </div>
    <div class="slide slide-23">
      <div class="slide-content">
        <label for="slide22" class="prev-zone" title="上一张"></label>
        <label for="slide24" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_pixel.png" alt="Pixel Art">
      </div>
      <div class="slide-caption">23. 像素艺术 (Pixel Art) - 面包屑与标签页等</div>
    </div>
    <div class="slide slide-24">
      <div class="slide-content">
        <label for="slide23" class="prev-zone" title="上一张"></label>
        <label for="slide25" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_spatial.png" alt="Spatial UI (VisionOS)">
      </div>
      <div class="slide-caption">24. 空间 UI (Spatial UI (VisionOS)) - 图像分屏</div>
    </div>
    <div class="slide slide-25">
      <div class="slide-content">
        <label for="slide24" class="prev-zone" title="上一张"></label>
        <label for="slide1" class="next-zone" title="下一张"></label>
        <img src="../../assets/images/theme_vintage.png" alt="Vintage Analog / Retro Film">
      </div>
      <div class="slide-caption">25. 复古胶片 (Vintage Analog / Retro Film) - 复选框</div>
    </div>
  </div>
  
  <div class="carousel-nav">
    <div class="controls">
      <label for="slide1" class="dot"></label>
      <label for="slide2" class="dot"></label>
      <label for="slide3" class="dot"></label>
      <label for="slide4" class="dot"></label>
      <label for="slide5" class="dot"></label>
      <label for="slide6" class="dot"></label>
      <label for="slide7" class="dot"></label>
      <label for="slide8" class="dot"></label>
      <label for="slide9" class="dot"></label>
      <label for="slide10" class="dot"></label>
      <label for="slide11" class="dot"></label>
      <label for="slide12" class="dot"></label>
      <label for="slide13" class="dot"></label>
      <label for="slide14" class="dot"></label>
      <label for="slide15" class="dot"></label>
      <label for="slide16" class="dot"></label>
      <label for="slide17" class="dot"></label>
      <label for="slide18" class="dot"></label>
      <label for="slide19" class="dot"></label>
      <label for="slide20" class="dot"></label>
      <label for="slide21" class="dot"></label>
      <label for="slide22" class="dot"></label>
      <label for="slide23" class="dot"></label>
      <label for="slide24" class="dot"></label>
      <label for="slide25" class="dot"></label>
    </div>
  </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {
  const carousel = document.querySelector(".theme-carousel");
  if (!carousel) return;
  
  const inputs = Array.from(carousel.querySelectorAll("input[type='radio']"));
  let timer = null;
  
  function getCheckedIndex() {
    return inputs.findIndex(input => input.checked);
  }
  
  function nextSlide() {
    let currentIndex = getCheckedIndex();
    currentIndex = (currentIndex + 1) % inputs.length;
    inputs[currentIndex].checked = true;
  }
  
  function startAutoplay() {
    stopAutoplay();
    timer = setInterval(nextSlide, 4000); // 4秒自动播放
  }
  
  function stopAutoplay() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }
  
  startAutoplay();
  
  carousel.addEventListener("click", function(e) {
    if (e.target.tagName === "LABEL" || e.target.classList.contains("dot") || e.target.classList.contains("prev-zone") || e.target.classList.contains("next-zone")) {
      setTimeout(startAutoplay, 100);
    }
  });
});
</script>

<style>
.theme-carousel {
  position: relative;
  width: 100%;
  max-width: 850px;
  margin: 24px auto;
  overflow: hidden;
  border: 1px solid var(--md-typeset-table-color, #e4e4e7);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  background-color: var(--md-code-bg-color, #f8fafc);
}
.theme-carousel input[type="radio"] {
  display: none;
}
.slide-content {
  position: relative;
  width: 100%;
  display: flex;
}
.prev-zone, .next-zone {
  position: absolute;
  top: 0;
  height: 100%;
  width: 50%;
  z-index: 5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.prev-zone {
  left: 0;
}
.next-zone {
  right: 0;
}
.prev-zone::after {
  content: '❮';
  position: absolute;
  left: 20px;
  font-size: 24px;
  color: rgba(255, 255, 255, 0.85);
  background-color: rgba(0, 0, 0, 0.45);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.25s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.prev-zone:hover::after {
  opacity: 1;
}
.next-zone::after {
  content: '❯';
  position: absolute;
  right: 20px;
  font-size: 24px;
  color: rgba(255, 255, 255, 0.85);
  background-color: rgba(0, 0, 0, 0.45);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.25s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.next-zone:hover::after {
  opacity: 1;
}
.slides {
  display: flex;
  width: 2500%;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide {
  width: 4%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.slide img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 8px 8px 0 0;
}
.slide-caption {
  padding: 12px 8px;
  width: 100%;
  text-align: center;
  font-weight: bold;
  background-color: var(--md-code-bg-color, rgba(0, 0, 0, 0.02));
  border-top: 1px solid var(--md-typeset-table-color, #e2e8f0);
  color: var(--md-typeset-color, #1e293b);
  font-size: 14px;
}
.carousel-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 0;
  background-color: var(--md-code-bg-color, rgba(0, 0, 0, 0.02));
  border-top: 1px dashed var(--md-typeset-table-color, #e2e8f0);
}
.controls {
  display: flex;
  gap: 12px;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: var(--md-typeset-table-color, #cbd5e1);
  cursor: pointer;
  transition: all 0.3s ease;
}
.dot:hover {
  background-color: #409eff;
  transform: scale(1.2);
}
#slide1:checked ~ .slides { transform: translateX(0); }
#slide2:checked ~ .slides { transform: translateX(-4%); }
#slide3:checked ~ .slides { transform: translateX(-8%); }
#slide4:checked ~ .slides { transform: translateX(-12%); }
#slide5:checked ~ .slides { transform: translateX(-16%); }
#slide6:checked ~ .slides { transform: translateX(-20%); }
#slide7:checked ~ .slides { transform: translateX(-24%); }
#slide8:checked ~ .slides { transform: translateX(-28%); }
#slide9:checked ~ .slides { transform: translateX(-32%); }
#slide10:checked ~ .slides { transform: translateX(-36%); }
#slide11:checked ~ .slides { transform: translateX(-40%); }
#slide12:checked ~ .slides { transform: translateX(-44%); }
#slide13:checked ~ .slides { transform: translateX(-48%); }
#slide14:checked ~ .slides { transform: translateX(-52%); }
#slide15:checked ~ .slides { transform: translateX(-56%); }
#slide16:checked ~ .slides { transform: translateX(-60%); }
#slide17:checked ~ .slides { transform: translateX(-64%); }
#slide18:checked ~ .slides { transform: translateX(-68%); }
#slide19:checked ~ .slides { transform: translateX(-72%); }
#slide20:checked ~ .slides { transform: translateX(-76%); }
#slide21:checked ~ .slides { transform: translateX(-80%); }
#slide22:checked ~ .slides { transform: translateX(-84%); }
#slide23:checked ~ .slides { transform: translateX(-88%); }
#slide24:checked ~ .slides { transform: translateX(-92%); }
#slide25:checked ~ .slides { transform: translateX(-96%); }

#slide1:checked ~ .carousel-nav label[for="slide1"] { background-color: #409eff; transform: scale(1.2); }
#slide2:checked ~ .carousel-nav label[for="slide2"] { background-color: #409eff; transform: scale(1.2); }
#slide3:checked ~ .carousel-nav label[for="slide3"] { background-color: #409eff; transform: scale(1.2); }
#slide4:checked ~ .carousel-nav label[for="slide4"] { background-color: #409eff; transform: scale(1.2); }
#slide5:checked ~ .carousel-nav label[for="slide5"] { background-color: #409eff; transform: scale(1.2); }
#slide6:checked ~ .carousel-nav label[for="slide6"] { background-color: #409eff; transform: scale(1.2); }
#slide7:checked ~ .carousel-nav label[for="slide7"] { background-color: #409eff; transform: scale(1.2); }
#slide8:checked ~ .carousel-nav label[for="slide8"] { background-color: #409eff; transform: scale(1.2); }
#slide9:checked ~ .carousel-nav label[for="slide9"] { background-color: #409eff; transform: scale(1.2); }
#slide10:checked ~ .carousel-nav label[for="slide10"] { background-color: #409eff; transform: scale(1.2); }
#slide11:checked ~ .carousel-nav label[for="slide11"] { background-color: #409eff; transform: scale(1.2); }
#slide12:checked ~ .carousel-nav label[for="slide12"] { background-color: #409eff; transform: scale(1.2); }
#slide13:checked ~ .carousel-nav label[for="slide13"] { background-color: #409eff; transform: scale(1.2); }
#slide14:checked ~ .carousel-nav label[for="slide14"] { background-color: #409eff; transform: scale(1.2); }
#slide15:checked ~ .carousel-nav label[for="slide15"] { background-color: #409eff; transform: scale(1.2); }
#slide16:checked ~ .carousel-nav label[for="slide16"] { background-color: #409eff; transform: scale(1.2); }
#slide17:checked ~ .carousel-nav label[for="slide17"] { background-color: #409eff; transform: scale(1.2); }
#slide18:checked ~ .carousel-nav label[for="slide18"] { background-color: #409eff; transform: scale(1.2); }
#slide19:checked ~ .carousel-nav label[for="slide19"] { background-color: #409eff; transform: scale(1.2); }
#slide20:checked ~ .carousel-nav label[for="slide20"] { background-color: #409eff; transform: scale(1.2); }
#slide21:checked ~ .carousel-nav label[for="slide21"] { background-color: #409eff; transform: scale(1.2); }
#slide22:checked ~ .carousel-nav label[for="slide22"] { background-color: #409eff; transform: scale(1.2); }
#slide23:checked ~ .carousel-nav label[for="slide23"] { background-color: #409eff; transform: scale(1.2); }
#slide24:checked ~ .carousel-nav label[for="slide24"] { background-color: #409eff; transform: scale(1.2); }
#slide25:checked ~ .carousel-nav label[for="slide25"] { background-color: #409eff; transform: scale(1.2); }
</style>

---

## 常用主题列表 (68 种内置设计风格)

以下是部分极具代表性的内置主题英文标识名与其中文显示名称：

| 英文标识键名 (Style Name) | 中文显示名称 | 视觉特征分类 |
| :--- | :--- | :--- |
| `"Elegant Light"` | 雅致亮色 | 极简亮色/高对比设计，标题栏与侧边栏分明 |
| `"Minimalism & Swiss Style"` | 极简瑞士风格 | 扁平/经典设计 |
| `"Neumorphism"` | 新拟物化 | 软 UI (Soft UI) / 黏土拟态 |
| `"Glassmorphism"` | 玻璃拟态 | 毛玻璃/背景模糊 (Spatial UI) |
| `"Brutalism"` | 粗野主义 | 高对比度/纯黑粗边框 (New Brutalism) |
| `"Cyberpunk UI"` | 赛博朋克 UI | 霓虹发光/高饱和度暗调 |
| `"HUD / Sci-Fi FUI"` | HUD 科幻界面 | 暗蓝色调/荧光线条 |
| `"E-Ink / Paper"` | 电子墨水屏与纸质 | 黑白双色/极高文字可读性 |
| `"Dark Mode (OLED)"` | 深色模式 OLED | 极致省电全黑模式 |
| `"Claymorphism"` | 黏土拟态 | 立体充气感/高亮阴影对比 |
| `"Aurora UI"` | 极光 UI | 极光梦幻渐变色调 |
| `"3D & Hyperrealism"` | 3D与超现实 | 立体材质/光影细节 |
| `"Vibrant & Block-based"` | 活力方块设计 | 大面积色块/高饱和色彩 |
| `"Accessible & Ethical"` | 无障碍友好设计 | 高对比度/符合 WCAG AAA 标准 |
| `"Retro-Futurism"` | 复古未来主义 | 80年代霓虹/CRT扫描线效果 |
| `"Flat Design"` | 经典扁平化 | 去除投影与高亮渐变，极致扁平 |
| `"Skeuomorphism"` | 拟物化风格 | 质感逼真/还原真实物体 |
| `"Liquid Glass"` | 流态玻璃 | 液体流动感/毛玻璃混合效果 |
| `"Y2K Aesthetic"` | Y2K 潮酷美学 | 千禧年科技感/金属反光与复古酸性 |
| `"AI-Native UI"` | AI 原生界面 | 面向智能交互的动态布局与卡片 |
| `"Memphis Design"` | 孟菲斯风格 | 乱中有序的几何图形与撞色搭配 |
| `"Pixel Art"` | 像素艺术 | 怀旧像素游戏风/极简粗犷线条 |
| `"Spatial UI (VisionOS)"` | 空间 UI (VisionOS) | 悬浮透光/三维层级深度感 |
| `"Vintage Analog / Retro Film"` | 复古胶片色调 | 暖色噪点/拍立得与老唱片质感 |

*可以在代码中使用 `ThemeEngine.list_themes()` 检索出全部 68+ 款可用主题的英文标识键名。*
