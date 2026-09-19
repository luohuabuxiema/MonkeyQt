# monkeyqt-icons 

基于 `@phosphor-icons/core`  深度移植，包含 **1,512 个基础图标**、**6 种外观风格**（共 9,072 个矢量 SVG 图像），支持动态变色、Duotone 双色渲染、旋转、镜像翻转与 LRU 高级缓存。

---

## 安装

```bash
pip install monkeyqt-icons
```

---

##  快速上手

### 1. 直接导入图标类

支持链式调用直接生成 `QIcon`：

```python
from PySide6.QtWidgets import QApplication, QPushButton
from monkeyqt_icons import PhHouse, PhGear, PhUser

app = QApplication([])

btn1 = QPushButton("首页")
# 生成 24px 双色图标
btn1.setIcon(PhHouse.duotone(color="#3b82f6", secondary_color="#93c5fd", size=24))

btn2 = QPushButton("设置")
# 生成填充风格图标
btn2.setIcon(PhGear.fill(color="red", size=20))

btn3 = QPushButton("个人中心")
# 生成粗体风格图标
btn3.setIcon(PhUser.bold(color="#10b981"))

btn1.show()
app.exec()
```

### 2. 统一命名空间 

通过 `Ph` 命名空间访问所有图标：

```python
from monkeyqt_icons import Ph

# 极简调用
button.setIcon(Ph.House.fill(color="#007bff"))
label.setPixmap(Ph.Heart.duotone(color="red", size=32))
```

### 3. 动态字符串调用与元数据检索

```python
from monkeyqt_icons import Ph

# 1. 动态生成 QIcon
icon = Ph.icon("house", weight="duotone", color="#3b82f6", size=24)

# 2. 搜索图标
results = Ph.search("setting")  # 匹配名称、分类和搜索标签
print([r["pascal_name"] for r in results])

# 3. 获取图标详细元数据
info = Ph.get_info("house")
print(info["categories"], info["tags"])
```

### 4. 作为独立 QWidget 控件使用

内置 `PhIconWidget`，可直接作为 UI 布局中的交互控件：

```python
from monkeyqt_icons import PhHouse, PhIconWidget

# 方式 A：通过图标类创建 Widget
icon_widget = PhHouse.widget(size=32, color="#3b82f6", weight="duotone")
icon_widget.clicked.connect(lambda: print("Icon clicked!"))

# 方式 B：使用 PhIconWidget 构造
icon_widget2 = PhIconWidget(icon="heart", size=24, color="red", hover_color="darkred")
```

---

## 参数与风格

支持所有 Phosphor Icons 的 6 种外观风格：

* `regular` (常规) — `PhHouse.regular()`
* `bold` (加粗) — `PhHouse.bold()`
* `fill` (填充) — `PhHouse.fill()`
* `light` (细线) — `PhHouse.light()`
* `thin` (极细) — `PhHouse.thin()`
* `duotone` (双色图层) — `PhHouse.duotone(color="blue", secondary_color="lightblue")`

通用参数表：

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `size` | `int` | `24` | 图标宽高尺寸 (px) |
| `color` | `str / QColor` | `"currentColor"` | 主色调（支持 Hex、RGB、QColor） |
| `secondary_color`| `str / QColor` | `None` | Duotone 双色模式下的辅助底色 |
| `secondary_opacity` | `float` | `0.2` | Duotone 辅助底色透明度 (0.0~1.0) |
| `mirrored` | `bool` | `False` | 是否水平镜像翻转 |
| `rotation` | `int` | `0` | 旋转角度 (0, 90, 180, 270) |

---

---

##  图标索引与中文译名对照表

> 提示：可在 IDE 或浏览器中使用 `Ctrl+F` 快速查找需要的图标名称或中文含义。

| 序号 | 图标名称 (kebab-case) | 图标类名 (PascalCase) | 中文译名 / 说明 | 分类 (Categories) |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `acorn` | `PhAcorn` | 橡果 | finance, nature |
| 2 | `address-book` | `PhAddressBook` | 通讯录/地址簿 | communication |
| 3 | `address-book-tabs` | `PhAddressBookTabs` | 通讯录标签页 | communication |
| 4 | `air-traffic-control` | `PhAirTrafficControl` | 空中交通管制塔 | map |
| 5 | `airplane` | `PhAirplane` | 飞机 | map, objects |
| 6 | `airplane-in-flight` | `PhAirplaneInFlight` | 飞行中的飞机 | map, objects |
| 7 | `airplane-landing` | `PhAirplaneLanding` | 降落的飞机 | map, objects |
| 8 | `airplane-takeoff` | `PhAirplaneTakeoff` | 起飞的飞机 | map, objects |
| 9 | `airplane-taxiing` | `PhAirplaneTaxiing` | 滑行中的飞机 | map, objects |
| 10 | `airplane-tilt` | `PhAirplaneTilt` | 倾斜的飞机 | map, objects |
| 11 | `airplay` | `PhAirplay` | 隔空播放 (AirPlay) | media, system |
| 12 | `alarm` | `PhAlarm` | 闹钟 | system |
| 13 | `alien` | `PhAlien` | 外星人 | games |
| 14 | `align-bottom` | `PhAlignBottom` | 底部对齐 | design, editor |
| 15 | `align-bottom-simple` | `PhAlignBottomSimple` | 简易底部对齐 | design, editor |
| 16 | `align-center-horizontal` | `PhAlignCenterHorizontal` | 水平居中对齐 | design, editor |
| 17 | `align-center-horizontal-simple` | `PhAlignCenterHorizontalSimple` | 简易水平居中对齐 | design, editor |
| 18 | `align-center-vertical` | `PhAlignCenterVertical` | 垂直居中对齐 | design, editor |
| 19 | `align-center-vertical-simple` | `PhAlignCenterVerticalSimple` | 简易垂直居中对齐 | design, editor |
| 20 | `align-left` | `PhAlignLeft` | 左对齐 | design, editor |
| 21 | `align-left-simple` | `PhAlignLeftSimple` | 简易左对齐 | design, editor |
| 22 | `align-right` | `PhAlignRight` | 右对齐 | design, editor |
| 23 | `align-right-simple` | `PhAlignRightSimple` | 简易右对齐 | design, editor |
| 24 | `align-top` | `PhAlignTop` | 顶部对齐 | design, editor |
| 25 | `align-top-simple` | `PhAlignTopSimple` | 简易顶部对齐 | design, editor |
| 26 | `amazon-logo` | `PhAmazonLogo` | 亚马逊 Logo | brand |
| 27 | `ambulance` | `PhAmbulance` | 救护车 | health, map, objects |
| 28 | `anchor` | `PhAnchor` | 船锚 | communication, map, objects |
| 29 | `anchor-simple` | `PhAnchorSimple` | 简易船锚 | communication, map, objects |
| 30 | `android-logo` | `PhAndroidLogo` | 安卓 Logo | brand, development, system |
| 31 | `angle` | `PhAngle` | 角度/量角 | design, objects |
| 32 | `angular-logo` | `PhAngularLogo` | Angular 框架 Logo | brand, development |
| 33 | `aperture` | `PhAperture` | 光圈/相机光圈 | design, media |
| 34 | `app-store-logo` | `PhAppStoreLogo` | App Store 标识 | brand |
| 35 | `app-window` | `PhAppWindow` | 应用窗口 | communication, system |
| 36 | `apple-logo` | `PhAppleLogo` | 苹果 Logo | brand |
| 37 | `apple-podcasts-logo` | `PhApplePodcastsLogo` | Apple 播客 Logo | brand, media |
| 38 | `approximate-equals` | `PhApproximateEquals` | 约等于号 (≈) | finance, development |
| 39 | `archive` | `PhArchive` | 归档/存档 | office, system |
| 40 | `armchair` | `PhArmchair` | 扶手沙发椅 | objects, commerce |
| 41 | `arrow-arc-left` | `PhArrowArcLeft` | 左弧形箭头 | arrows |
| 42 | `arrow-arc-right` | `PhArrowArcRight` | 右弧形箭头 | arrows |
| 43 | `arrow-bend-double-up-left` | `PhArrowBendDoubleUpLeft` | 双弯曲右上箭头 (全部回复) | arrows |
| 44 | `arrow-bend-double-up-right` | `PhArrowBendDoubleUpRight` | 双弯曲右下箭头 | arrows |
| 45 | `arrow-bend-down-left` | `PhArrowBendDownLeft` | 下弯左箭头 | arrows |
| 46 | `arrow-bend-down-right` | `PhArrowBendDownRight` | 下弯右箭头 | arrows |
| 47 | `arrow-bend-left-down` | `PhArrowBendLeftDown` | 左弯下箭头 | arrows |
| 48 | `arrow-bend-left-up` | `PhArrowBendLeftUp` | 左弯上箭头 | arrows |
| 49 | `arrow-bend-right-down` | `PhArrowBendRightDown` | 右弯下箭头 | arrows |
| 50 | `arrow-bend-right-up` | `PhArrowBendRightUp` | 右弯上箭头 | arrows |
| 51 | `arrow-bend-up-left` | `PhArrowBendUpLeft` | 上弯左箭头 (回复) | arrows |
| 52 | `arrow-bend-up-right` | `PhArrowBendUpRight` | 上弯右箭头 (转发) | arrows |
| 53 | `arrow-circle-down` | `PhArrowCircleDown` | 下箭头圆圈 | arrows |
| 54 | `arrow-circle-down-left` | `PhArrowCircleDownLeft` | 左下箭头圆圈 | arrows |
| 55 | `arrow-circle-down-right` | `PhArrowCircleDownRight` | 右下箭头圆圈 | arrows |
| 56 | `arrow-circle-left` | `PhArrowCircleLeft` | 左箭头圆圈 | arrows |
| 57 | `arrow-circle-right` | `PhArrowCircleRight` | 右箭头圆圈 | arrows |
| 58 | `arrow-circle-up` | `PhArrowCircleUp` | 上箭头圆圈 | arrows |
| 59 | `arrow-circle-up-left` | `PhArrowCircleUpLeft` | 左上箭头圆圈 | arrows |
| 60 | `arrow-circle-up-right` | `PhArrowCircleUpRight` | 右上箭头圆圈 | arrows |
| 61 | `arrow-clockwise` | `PhArrowClockwise` | 顺时针旋转箭头 (重做) | arrows |
| 62 | `arrow-counter-clockwise` | `PhArrowCounterClockwise` | 逆时针旋转箭头 (撤销) | arrows |
| 63 | `arrow-down` | `PhArrowDown` | 下箭头 | arrows |
| 64 | `arrow-down-left` | `PhArrowDownLeft` | 左下箭头 | arrows |
| 65 | `arrow-down-right` | `PhArrowDownRight` | 右下箭头 | arrows |
| 66 | `arrow-elbow-down-left` | `PhArrowElbowDownLeft` | 下折左箭头 | arrows |
| 67 | `arrow-elbow-down-right` | `PhArrowElbowDownRight` | 下折右箭头 | arrows |
| 68 | `arrow-elbow-left` | `PhArrowElbowLeft` | 左折角箭头 | arrows |
| 69 | `arrow-elbow-left-down` | `PhArrowElbowLeftDown` | 左折下箭头 | arrows |
| 70 | `arrow-elbow-left-up` | `PhArrowElbowLeftUp` | 左折上箭头 | arrows |
| 71 | `arrow-elbow-right` | `PhArrowElbowRight` | 右折角箭头 | arrows |
| 72 | `arrow-elbow-right-down` | `PhArrowElbowRightDown` | 右折下箭头 | arrows |
| 73 | `arrow-elbow-right-up` | `PhArrowElbowRightUp` | 右折上箭头 | arrows |
| 74 | `arrow-elbow-up-left` | `PhArrowElbowUpLeft` | 上折左箭头 | arrows |
| 75 | `arrow-elbow-up-right` | `PhArrowElbowUpRight` | 上折右箭头 | arrows |
| 76 | `arrow-fat-down` | `PhArrowFatDown` | 粗体下箭头 | arrows |
| 77 | `arrow-fat-left` | `PhArrowFatLeft` | 粗体左箭头 | arrows |
| 78 | `arrow-fat-line-down` | `PhArrowFatLineDown` | 单线粗下箭头 | arrows |
| 79 | `arrow-fat-line-left` | `PhArrowFatLineLeft` | 单线粗左箭头 | arrows |
| 80 | `arrow-fat-line-right` | `PhArrowFatLineRight` | 单线粗右箭头 | arrows |
| 81 | `arrow-fat-line-up` | `PhArrowFatLineUp` | 单线粗上箭头 | arrows |
| 82 | `arrow-fat-lines-down` | `PhArrowFatLinesDown` | 线条粗下箭头 | arrows |
| 83 | `arrow-fat-lines-left` | `PhArrowFatLinesLeft` | 线条粗左箭头 | arrows |
| 84 | `arrow-fat-lines-right` | `PhArrowFatLinesRight` | 线条粗右箭头 | arrows |
| 85 | `arrow-fat-lines-up` | `PhArrowFatLinesUp` | 线条粗上箭头 | arrows |
| 86 | `arrow-fat-right` | `PhArrowFatRight` | 粗体右箭头 | arrows |
| 87 | `arrow-fat-up` | `PhArrowFatUp` | 粗体上箭头 | arrows |
| 88 | `arrow-left` | `PhArrowLeft` | 箭头 left | arrows |
| 89 | `arrow-line-down` | `PhArrowLineDown` | 到达底部/下划线箭头 | arrows |
| 90 | `arrow-line-down-left` | `PhArrowLineDownLeft` | 箭头 line-down-left | arrows |
| 91 | `arrow-line-down-right` | `PhArrowLineDownRight` | 箭头 line-down-right | arrows |
| 92 | `arrow-line-left` | `PhArrowLineLeft` | 到达左侧/左划线箭头 | arrows |
| 93 | `arrow-line-right` | `PhArrowLineRight` | 到达右侧/右划线箭头 | arrows |
| 94 | `arrow-line-up` | `PhArrowLineUp` | 到达顶部/上划线箭头 | arrows |
| 95 | `arrow-line-up-left` | `PhArrowLineUpLeft` | 箭头 line-up-left | arrows |
| 96 | `arrow-line-up-right` | `PhArrowLineUpRight` | 箭头 line-up-right | arrows |
| 97 | `arrow-right` | `PhArrowRight` | 右箭头 | arrows |
| 98 | `arrow-square-down` | `PhArrowSquareDown` | 方形下箭头 | arrows |
| 99 | `arrow-square-down-left` | `PhArrowSquareDownLeft` | 箭头 square-down-left | arrows |
| 100 | `arrow-square-down-right` | `PhArrowSquareDownRight` | 箭头 square-down-right | arrows |
| 101 | `arrow-square-in` | `PhArrowSquareIn` | 箭头 square-in | arrows |
| 102 | `arrow-square-left` | `PhArrowSquareLeft` | 方形左箭头 | arrows |
| 103 | `arrow-square-out` | `PhArrowSquareOut` | 箭头 square-out | arrows |
| 104 | `arrow-square-right` | `PhArrowSquareRight` | 方形右箭头 | arrows |
| 105 | `arrow-square-up` | `PhArrowSquareUp` | 方形上箭头 | arrows |
| 106 | `arrow-square-up-left` | `PhArrowSquareUpLeft` | 箭头 square-up-left | arrows |
| 107 | `arrow-square-up-right` | `PhArrowSquareUpRight` | 箭头 square-up-right | arrows |
| 108 | `arrow-u-down-left` | `PhArrowUDownLeft` | U型转向左下箭头 | arrows |
| 109 | `arrow-u-down-right` | `PhArrowUDownRight` | U型转向右下箭头 | arrows |
| 110 | `arrow-u-left-down` | `PhArrowULeftDown` | U型转向下左箭头 | arrows |
| 111 | `arrow-u-left-up` | `PhArrowULeftUp` | U型转向上左箭头 | arrows |
| 112 | `arrow-u-right-down` | `PhArrowURightDown` | U型转向下右箭头 | arrows |
| 113 | `arrow-u-right-up` | `PhArrowURightUp` | U型转向上右箭头 | arrows |
| 114 | `arrow-u-up-left` | `PhArrowUUpLeft` | U型转向左上箭头 | arrows |
| 115 | `arrow-u-up-right` | `PhArrowUUpRight` | U型转向右上箭头 | arrows |
| 116 | `arrow-up` | `PhArrowUp` | 上箭头 | arrows |
| 117 | `arrow-up-left` | `PhArrowUpLeft` | 左上箭头 | arrows |
| 118 | `arrow-up-right` | `PhArrowUpRight` | 右上箭头 | arrows |
| 119 | `arrows-clockwise` | `PhArrowsClockwise` | 双顺时针旋转箭头 (刷新) | arrows |
| 120 | `arrows-counter-clockwise` | `PhArrowsCounterClockwise` | 双逆时针旋转箭头 (刷新) | arrows |
| 121 | `arrows-down-up` | `PhArrowsDownUp` | 上下双向箭头 | arrows |
| 122 | `arrows-horizontal` | `PhArrowsHorizontal` | 水平双向箭头 | arrows |
| 123 | `arrows-in` | `PhArrowsIn` | 缩小/向内收缩箭头 | arrows |
| 124 | `arrows-in-cardinal` | `PhArrowsInCardinal` | 四向向内收缩箭头 | arrows |
| 125 | `arrows-in-line-horizontal` | `PhArrowsInLineHorizontal` | 水平向线收缩箭头 | arrows, design, editor |
| 126 | `arrows-in-line-vertical` | `PhArrowsInLineVertical` | 垂直向线收缩箭头 | arrows, design, editor |
| 127 | `arrows-in-simple` | `PhArrowsInSimple` | 简易缩小箭头 | arrows |
| 128 | `arrows-left-right` | `PhArrowsLeftRight` | 左右双向箭头 | arrows |
| 129 | `arrows-merge` | `PhArrowsMerge` | 合并箭头 | arrows |
| 130 | `arrows-out` | `PhArrowsOut` | 放大/向外扩展箭头 | arrows |
| 131 | `arrows-out-cardinal` | `PhArrowsOutCardinal` | 四向向外扩展箭头 | arrows |
| 132 | `arrows-out-line-horizontal` | `PhArrowsOutLineHorizontal` | 水平向外扩展箭头 | arrows, design, editor |
| 133 | `arrows-out-line-vertical` | `PhArrowsOutLineVertical` | 垂直向外扩展箭头 | arrows, design, editor |
| 134 | `arrows-out-simple` | `PhArrowsOutSimple` | 简易放大箭头 | arrows |
| 135 | `arrows-split` | `PhArrowsSplit` | 分流箭头 | arrows |
| 136 | `arrows-vertical` | `PhArrowsVertical` | 垂直双向箭头 | arrows |
| 137 | `article` | `PhArticle` | 文章/新闻稿 | media, objects |
| 138 | `article-medium` | `PhArticleMedium` | Medium 样式文章 | media, objects |
| 139 | `article-ny-times` | `PhArticleNyTimes` | 纽约时报样式文章 | media, objects |
| 140 | `asclepius` | `PhAsclepius` | asclepius | health |
| 141 | `asterisk` | `PhAsterisk` | 星号 (*) | communication |
| 142 | `asterisk-simple` | `PhAsteriskSimple` | 简易星号 | communication |
| 143 | `at` | `PhAt` | At 符号 (@) | communication |
| 144 | `atom` | `PhAtom` | 原子 | development, nature |
| 145 | `avocado` | `PhAvocado` | avocado | commerce, nature |
| 146 | `axe` | `PhAxe` | axe | commerce, objects |
| 147 | `baby` | `PhBaby` | 婴儿/宝宝 | people, health |
| 148 | `baby-carriage` | `PhBabyCarriage` | baby-carriage | commerce, people |
| 149 | `backpack` | `PhBackpack` | 双肩背包 | commerce, objects |
| 150 | `backspace` | `PhBackspace` | 退格键 | system |
| 151 | `bag` | `PhBag` | 手提包 | commerce, objects |
| 152 | `bag-simple` | `PhBagSimple` | 简易手提包 | commerce, objects |
| 153 | `balloon` | `PhBalloon` | 气球 | commerce, objects |
| 154 | `bandaids` | `PhBandaids` | 创口贴 | health |
| 155 | `bank` | `PhBank` | 银行大楼 | finance, map |
| 156 | `barbell` | `PhBarbell` | barbell | health |
| 157 | `barcode` | `PhBarcode` | 条形码 | commerce, system |
| 158 | `barn` | `PhBarn` | barn | commerce, map |
| 159 | `barricade` | `PhBarricade` | barricade | map, objects |
| 160 | `baseball` | `PhBaseball` | baseball | games, health, objects |
| 161 | `baseball-cap` | `PhBaseballCap` | baseball-cap | commerce, objects |
| 162 | `baseball-helmet` | `PhBaseballHelmet` | baseball-helmet | games, health, objects |
| 163 | `basket` | `PhBasket` | 购物篮 | commerce, objects |
| 164 | `basketball` | `PhBasketball` | 篮球 | games, health, objects |
| 165 | `bathtub` | `PhBathtub` | 浴缸 | objects |
| 166 | `battery-charging` | `PhBatteryCharging` | 充电中的电池 | system |
| 167 | `battery-charging-vertical` | `PhBatteryChargingVertical` | 充电中的电池 (垂直) | system |
| 168 | `battery-empty` | `PhBatteryEmpty` | 空电池 | system |
| 169 | `battery-full` | `PhBatteryFull` | 满电电池 | system |
| 170 | `battery-high` | `PhBatteryHigh` | 高电量电池 | system |
| 171 | `battery-low` | `PhBatteryLow` | 低电量电池 | system |
| 172 | `battery-medium` | `PhBatteryMedium` | 中电量电池 | system |
| 173 | `battery-plus` | `PhBatteryPlus` | battery-plus | system |
| 174 | `battery-plus-vertical` | `PhBatteryPlusVertical` | battery-plus-vertical | system |
| 175 | `battery-vertical-empty` | `PhBatteryVerticalEmpty` | battery-vertical-empty | system |
| 176 | `battery-vertical-full` | `PhBatteryVerticalFull` | battery-vertical-full | system |
| 177 | `battery-vertical-high` | `PhBatteryVerticalHigh` | battery-vertical-high | system |
| 178 | `battery-vertical-low` | `PhBatteryVerticalLow` | battery-vertical-low | system |
| 179 | `battery-vertical-medium` | `PhBatteryVerticalMedium` | battery-vertical-medium | system |
| 180 | `battery-warning` | `PhBatteryWarning` | 电量警告电池 | system |
| 181 | `battery-warning-vertical` | `PhBatteryWarningVertical` | battery-warning-vertical | system |
| 182 | `beach-ball` | `PhBeachBall` | 沙滩排球 | games, health, objects |
| 183 | `beanie` | `PhBeanie` | 针织帽 | commerce, objects |
| 184 | `bed` | `PhBed` | 床 | health, map, objects |
| 185 | `beer-bottle` | `PhBeerBottle` | 啤酒瓶 | commerce, map, objects |
| 186 | `beer-stein` | `PhBeerStein` | 啤酒扎杯 | commerce, map, objects |
| 187 | `behance-logo` | `PhBehanceLogo` | Behance 标志 | brand, design |
| 188 | `bell` | `PhBell` | 通知铃铛 | system, objects |
| 189 | `bell-ringing` | `PhBellRinging` | bell-ringing | system |
| 190 | `bell-simple` | `PhBellSimple` | 简易通知铃铛 | system, objects |
| 191 | `bell-simple-ringing` | `PhBellSimpleRinging` | bell简易-ringing | system |
| 192 | `bell-simple-slash` | `PhBellSimpleSlash` | bell简易-slash | system |
| 193 | `bell-simple-z` | `PhBellSimpleZ` | bell简易-z | system |
| 194 | `bell-slash` | `PhBellSlash` | 静音/关闭通知 | system |
| 195 | `bell-z` | `PhBellZ` | 免打扰/休眠通知 | system |
| 196 | `belt` | `PhBelt` | belt | commerce, objects |
| 197 | `bezier-curve` | `PhBezierCurve` | bezier-curve | design |
| 198 | `bicycle` | `PhBicycle` | bicycle | health, map, objects |
| 199 | `binary` | `PhBinary` | binary | development, system |
| 200 | `binoculars` | `PhBinoculars` | binoculars | nature, objects, map |
| 201 | `biohazard` | `PhBiohazard` | biohazard | health |
| 202 | `bird` | `PhBird` | 小鸟 | nature |
| 203 | `blueprint` | `PhBlueprint` | blueprint | commerce, design |
| 204 | `bluetooth` | `PhBluetooth` | 蓝牙 | system |
| 205 | `bluetooth-connected` | `PhBluetoothConnected` | 蓝牙已连接 | system |
| 206 | `bluetooth-slash` | `PhBluetoothSlash` | 蓝牙关闭 | system |
| 207 | `bluetooth-x` | `PhBluetoothX` | bluetooth-x | system |
| 208 | `boat` | `PhBoat` | boat | map, objects |
| 209 | `bomb` | `PhBomb` | bomb | games, objects |
| 210 | `bone` | `PhBone` | bone | nature, health |
| 211 | `book` | `PhBook` | 书籍 | office, media, objects |
| 212 | `book-bookmark` | `PhBookBookmark` | 带书签的书 | office, media, objects |
| 213 | `book-open` | `PhBookOpen` | 打开的书籍 | office, media, objects |
| 214 | `book-open-text` | `PhBookOpenText` | 打开的文本书 | office, media, objects, map |
| 215 | `book-open-user` | `PhBookOpenUser` | book-open-user | office, media, objects |
| 216 | `bookmark` | `PhBookmark` | 书签 | office, media, objects |
| 217 | `bookmark-simple` | `PhBookmarkSimple` | 简易书签 | office, media, objects |
| 218 | `bookmarks` | `PhBookmarks` | 多书签 | office, objects |
| 219 | `bookmarks-simple` | `PhBookmarksSimple` | bookmarks简易 | office, objects |
| 220 | `books` | `PhBooks` | 一堆书 | office, map, media, objects |
| 221 | `boot` | `PhBoot` | 靴子 | commerce, objects, health |
| 222 | `boules` | `PhBoules` | boules | games, health, objects |
| 223 | `bounding-box` | `PhBoundingBox` | 包围盒/定界框 | design |
| 224 | `bowl-food` | `PhBowlFood` | 一碗食物 | commerce, map, objects |
| 225 | `bowl-steam` | `PhBowlSteam` | 冒热气的碗 | commerce, objects, map |
| 226 | `bowling-ball` | `PhBowlingBall` | 保龄球 | games, health, objects |
| 227 | `box-arrow-down` | `PhBoxArrowDown` | 下箭头盒子 (收件箱) | office, system |
| 228 | `box-arrow-up` | `PhBoxArrowUp` | 上箭头盒子 (发件箱) | office, system |
| 229 | `boxing-glove` | `PhBoxingGlove` | 拳击手套 | games, health, objects |
| 230 | `brackets-angle` | `PhBracketsAngle` | 尖括号 (<>) | development, editor |
| 231 | `brackets-curly` | `PhBracketsCurly` | 大括号 ({}) | development, editor |
| 232 | `brackets-round` | `PhBracketsRound` | 圆括号 (()) | development, editor |
| 233 | `brackets-square` | `PhBracketsSquare` | 方括号 ([]) | development, editor |
| 234 | `brain` | `PhBrain` | 大脑/人工智能 | health, nature |
| 235 | `brandy` | `PhBrandy` | 白兰地酒杯 | commerce, map, objects |
| 236 | `bread` | `PhBread` | 面包 | commerce, map |
| 237 | `bridge` | `PhBridge` | 桥梁 | map, objects |
| 238 | `briefcase` | `PhBriefcase` | 公文包 | office, objects |
| 239 | `briefcase-metal` | `PhBriefcaseMetal` | 金属公文包 | office, objects |
| 240 | `broadcast` | `PhBroadcast` | 无线电广播 | communication, media, system |
| 241 | `broom` | `PhBroom` | 扫帚 | objects |
| 242 | `browser` | `PhBrowser` | 浏览器 | communication, system |
| 243 | `browsers` | `PhBrowsers` | 多浏览器窗口 | communication, system |
| 244 | `bug` | `PhBug` | Bug/程序错误/昆虫 | development, nature |
| 245 | `bug-beetle` | `PhBugBeetle` | 甲虫 Bug | development, nature |
| 246 | `bug-droid` | `PhBugDroid` | 安卓机器 Bug | development, nature |
| 247 | `building` | `PhBuilding` | 建筑大楼 | commerce, map |
| 248 | `building-apartment` | `PhBuildingApartment` | building-apartment | commerce, map |
| 249 | `building-office` | `PhBuildingOffice` | building-office | commerce, map |
| 250 | `buildings` | `PhBuildings` | 建筑群/城市 | commerce, map |
| 251 | `bulldozer` | `PhBulldozer` | 推土机 | commerce, objects |
| 252 | `bus` | `PhBus` | 公交车 | map, objects |
| 253 | `butterfly` | `PhButterfly` | 蝴蝶 | nature |
| 254 | `cable-car` | `PhCableCar` | cable-car | map, objects |
| 255 | `cactus` | `PhCactus` | 仙人掌 | nature |
| 256 | `cake` | `PhCake` | 蛋糕 | objects |
| 257 | `calculator` | `PhCalculator` | 计算器 | development, finance, office, objects |
| 258 | `calendar` | `PhCalendar` | 日历 | office, system |
| 259 | `calendar-blank` | `PhCalendarBlank` | 空白日历 | office, system |
| 260 | `calendar-check` | `PhCalendarCheck` | 已签到/已打卡日历 | office, system |
| 261 | `calendar-dot` | `PhCalendarDot` | calendar-dot | office, system |
| 262 | `calendar-dots` | `PhCalendarDots` | calendar-dots | office, system |
| 263 | `calendar-heart` | `PhCalendarHeart` | 约会/情人节日历 | office, system |
| 264 | `calendar-minus` | `PhCalendarMinus` | calendar-minus | office, system |
| 265 | `calendar-plus` | `PhCalendarPlus` | 新建日程日历 | office, system |
| 266 | `calendar-slash` | `PhCalendarSlash` | 无日程日历 | office, system |
| 267 | `calendar-star` | `PhCalendarStar` | 重要星标日历 | office, system |
| 268 | `calendar-x` | `PhCalendarX` | calendar-x | office, system |
| 269 | `call-bell` | `PhCallBell` | call-bell | map, objects |
| 270 | `camera` | `PhCamera` | 相机 | media, system, objects |
| 271 | `camera-plus` | `PhCameraPlus` | 添加照片/相机 | media, system |
| 272 | `camera-rotate` | `PhCameraRotate` | 翻转镜头 | media, system |
| 273 | `camera-slash` | `PhCameraSlash` | 禁用相机 | media, system |
| 274 | `campfire` | `PhCampfire` | 篝火 | nature |
| 275 | `car` | `PhCar` | 汽车 | map, objects |
| 276 | `car-battery` | `PhCarBattery` | car-battery | commerce, objects |
| 277 | `car-profile` | `PhCarProfile` | car-profile | map, objects |
| 278 | `car-simple` | `PhCarSimple` | car简易 | map, objects |
| 279 | `cardholder` | `PhCardholder` | cardholder | commerce, finance, objects |
| 280 | `cards` | `PhCards` | 扑克牌/卡片集 | design, system |
| 281 | `cards-three` | `PhCardsThree` | cards-three | design, system |
| 282 | `caret-circle-double-down` | `PhCaretCircleDoubleDown` | caret圆圈-double-down | arrows |
| 283 | `caret-circle-double-left` | `PhCaretCircleDoubleLeft` | caret圆圈-double-left | arrows |
| 284 | `caret-circle-double-right` | `PhCaretCircleDoubleRight` | caret圆圈-double-right | arrows |
| 285 | `caret-circle-double-up` | `PhCaretCircleDoubleUp` | caret圆圈-double-up | arrows |
| 286 | `caret-circle-down` | `PhCaretCircleDown` | 向下实心圆圈箭头 | arrows |
| 287 | `caret-circle-left` | `PhCaretCircleLeft` | 向左实心圆圈箭头 | arrows |
| 288 | `caret-circle-right` | `PhCaretCircleRight` | 向右实心圆圈箭头 | arrows |
| 289 | `caret-circle-up` | `PhCaretCircleUp` | 向上实心圆圈箭头 | arrows |
| 290 | `caret-circle-up-down` | `PhCaretCircleUpDown` | caret圆圈-up-down | arrows |
| 291 | `caret-double-down` | `PhCaretDoubleDown` | caret-double-down | arrows |
| 292 | `caret-double-left` | `PhCaretDoubleLeft` | caret-double-left | arrows |
| 293 | `caret-double-right` | `PhCaretDoubleRight` | caret-double-right | arrows |
| 294 | `caret-double-up` | `PhCaretDoubleUp` | caret-double-up | arrows |
| 295 | `caret-down` | `PhCaretDown` | 向下实心三角箭头 (下拉) | arrows |
| 296 | `caret-left` | `PhCaretLeft` | 向左实心三角箭头 | arrows |
| 297 | `caret-line-down` | `PhCaretLineDown` | caret-line-down | arrows |
| 298 | `caret-line-left` | `PhCaretLineLeft` | caret-line-left | arrows |
| 299 | `caret-line-right` | `PhCaretLineRight` | caret-line-right | arrows |
| 300 | `caret-line-up` | `PhCaretLineUp` | caret-line-up | arrows |
| 301 | `caret-right` | `PhCaretRight` | 向右实心三角箭头 | arrows |
| 302 | `caret-up` | `PhCaretUp` | 向上实心三角箭头 | arrows |
| 303 | `caret-up-down` | `PhCaretUpDown` | caret-up-down | arrows |
| 304 | `carrot` | `PhCarrot` | 胡萝卜 | commerce, nature |
| 305 | `cash-register` | `PhCashRegister` | 收银机 | commerce, objects |
| 306 | `cassette-tape` | `PhCassetteTape` | 卡带磁带 | media, objects |
| 307 | `castle-turret` | `PhCastleTurret` | 城堡塔楼 | map, objects, games |
| 308 | `cat` | `PhCat` | 猫咪 | nature |
| 309 | `cell-signal-full` | `PhCellSignalFull` | 满格手机信号 | system |
| 310 | `cell-signal-high` | `PhCellSignalHigh` | cell-signal-high | system |
| 311 | `cell-signal-low` | `PhCellSignalLow` | cell-signal-low | system |
| 312 | `cell-signal-medium` | `PhCellSignalMedium` | cell-signal-medium | system |
| 313 | `cell-signal-none` | `PhCellSignalNone` | cell-signal-none | system |
| 314 | `cell-signal-slash` | `PhCellSignalSlash` | cell-signal-slash | system |
| 315 | `cell-signal-x` | `PhCellSignalX` | cell-signal-x | system |
| 316 | `cell-tower` | `PhCellTower` | cell-tower | system |
| 317 | `certificate` | `PhCertificate` | 证书/凭证 | objects |
| 318 | `chair` | `PhChair` | 椅子 | objects, commerce |
| 319 | `chalkboard` | `PhChalkboard` | 黑板/教学板 | map, objects |
| 320 | `chalkboard-simple` | `PhChalkboardSimple` | 简易黑板 | map, objects |
| 321 | `chalkboard-teacher` | `PhChalkboardTeacher` | 教师黑板 | map, objects, people |
| 322 | `champagne` | `PhChampagne` | 香槟酒 | map, commerce, objects |
| 323 | `charging-station` | `PhChargingStation` | 充电桩 | map, objects |
| 324 | `chart-bar` | `PhChartBar` | 柱状图 | finance, office |
| 325 | `chart-bar-horizontal` | `PhChartBarHorizontal` | 水平柱状图 | finance, office |
| 326 | `chart-donut` | `PhChartDonut` | 甜甜圈环形图 | finance, office |
| 327 | `chart-line` | `PhChartLine` | 折线图 | finance, office |
| 328 | `chart-line-down` | `PhChartLineDown` | 下降折线图 | finance, office |
| 329 | `chart-line-up` | `PhChartLineUp` | 上升折线图 | finance, office |
| 330 | `chart-pie` | `PhChartPie` | 饼图 | finance, office |
| 331 | `chart-pie-slice` | `PhChartPieSlice` | 图表 pie-slice | finance, office |
| 332 | `chart-polar` | `PhChartPolar` | 极坐标图 | finance, office |
| 333 | `chart-scatter` | `PhChartScatter` | 散点图 | finance, office |
| 334 | `chat` | `PhChat` | 聊天对话 | communication |
| 335 | `chat-centered` | `PhChatCentered` | 居中聊天框 | communication |
| 336 | `chat-centered-dots` | `PhChatCenteredDots` | chat-centered-dots | communication |
| 337 | `chat-centered-slash` | `PhChatCenteredSlash` | chat-centered-slash | communication |
| 338 | `chat-centered-text` | `PhChatCenteredText` | chat-centered-text | communication |
| 339 | `chat-circle` | `PhChatCircle` | 圆形聊天框 | communication |
| 340 | `chat-circle-dots` | `PhChatCircleDots` | chat圆圈-dots | communication |
| 341 | `chat-circle-slash` | `PhChatCircleSlash` | chat圆圈-slash | communication |
| 342 | `chat-circle-text` | `PhChatCircleText` | chat圆圈-text | communication |
| 343 | `chat-dots` | `PhChatDots` | 正在输入聊天框 | communication |
| 344 | `chat-slash` | `PhChatSlash` | chat-slash | communication |
| 345 | `chat-teardrop` | `PhChatTeardrop` | 水滴形聊天框 | communication |
| 346 | `chat-teardrop-dots` | `PhChatTeardropDots` | chat-teardrop-dots | communication |
| 347 | `chat-teardrop-slash` | `PhChatTeardropSlash` | chat-teardrop-slash | communication |
| 348 | `chat-teardrop-text` | `PhChatTeardropText` | chat-teardrop-text | communication |
| 349 | `chat-text` | `PhChatText` | chat-text | communication |
| 350 | `chats` | `PhChats` | 多对话消息 | communication |
| 351 | `chats-circle` | `PhChatsCircle` | chats圆圈 | communication |
| 352 | `chats-teardrop` | `PhChatsTeardrop` | chats-teardrop | communication |
| 353 | `check` | `PhCheck` | 勾选/完成 (✓) | system |
| 354 | `check-circle` | `PhCheckCircle` | 圆圈勾选/完成 | system |
| 355 | `check-fat` | `PhCheckFat` | 粗体勾选 | system |
| 356 | `check-square` | `PhCheckSquare` | 方框勾选 | system |
| 357 | `check-square-offset` | `PhCheckSquareOffset` | 偏移方框勾选 | system |
| 358 | `checkerboard` | `PhCheckerboard` | 棋盘格 | games |
| 359 | `checks` | `PhChecks` | checks | system |
| 360 | `cheers` | `PhCheers` | cheers | commerce, map |
| 361 | `cheese` | `PhCheese` | 奶酪/芝士 | commerce |
| 362 | `chef-hat` | `PhChefHat` | 厨师帽 | commerce, objects |
| 363 | `cherries` | `PhCherries` | 樱桃 | nature, commerce |
| 364 | `church` | `PhChurch` | 教堂 | map |
| 365 | `cigarette` | `PhCigarette` | cigarette | commerce, health |
| 366 | `cigarette-slash` | `PhCigaretteSlash` | cigarette-slash | commerce, health |
| 367 | `circle` | `PhCircle` | 圆形 | design |
| 368 | `circle-dashed` | `PhCircleDashed` | 虚线圆圈 | design |
| 369 | `circle-half` | `PhCircleHalf` | 半圆 | design, editor |
| 370 | `circle-half-tilt` | `PhCircleHalfTilt` | circle-half-tilt | design, editor |
| 371 | `circle-notch` | `PhCircleNotch` | 缺口圆圈 (Loading) | system |
| 372 | `circles-four` | `PhCirclesFour` | 四圆阵列 | design |
| 373 | `circles-three` | `PhCirclesThree` | 三圆品字 | design |
| 374 | `circles-three-plus` | `PhCirclesThreePlus` | 三圆加号 | design |
| 375 | `circuitry` | `PhCircuitry` | circuitry | development |
| 376 | `city` | `PhCity` | city | map, commerce |
| 377 | `clipboard` | `PhClipboard` | 剪贴板 | office, editor, system |
| 378 | `clipboard-text` | `PhClipboardText` | 文本剪贴板 | office, editor, system |
| 379 | `clock` | `PhClock` | 时钟 | system, objects |
| 380 | `clock-afternoon` | `PhClockAfternoon` | 下午时钟 | system |
| 381 | `clock-clockwise` | `PhClockClockwise` | 顺时针时钟 | system |
| 382 | `clock-countdown` | `PhClockCountdown` | 倒计时时钟 | system |
| 383 | `clock-counter-clockwise` | `PhClockCounterClockwise` | 逆时针时钟 | system |
| 384 | `clock-user` | `PhClockUser` | clock-user | system |
| 385 | `closed-captioning` | `PhClosedCaptioning` | 隐藏字幕 (CC) | media |
| 386 | `cloud` | `PhCloud` | 云朵/云端 | system, weather |
| 387 | `cloud-arrow-down` | `PhCloudArrowDown` | 云端下载 | system |
| 388 | `cloud-arrow-up` | `PhCloudArrowUp` | 云端上传 | system |
| 389 | `cloud-check` | `PhCloudCheck` | 云同步完成 | system |
| 390 | `cloud-fog` | `PhCloudFog` | 雾气云 | weather |
| 391 | `cloud-lightning` | `PhCloudLightning` | 雷阵雨云 | weather |
| 392 | `cloud-moon` | `PhCloudMoon` | 夜间晴朗云 | weather |
| 393 | `cloud-rain` | `PhCloudRain` | 雨云 | weather |
| 394 | `cloud-slash` | `PhCloudSlash` | 断开云连接 | system |
| 395 | `cloud-snow` | `PhCloudSnow` | 雪云 | weather |
| 396 | `cloud-sun` | `PhCloudSun` | 白天多云 | weather |
| 397 | `cloud-warning` | `PhCloudWarning` | 云异常警告 | system |
| 398 | `cloud-x` | `PhCloudX` | cloud-x | system |
| 399 | `clover` | `PhClover` | 三叶草/幸运草 | nature |
| 400 | `club` | `PhClub` | 梅花 (扑克) | games |
| 401 | `coat-hanger` | `PhCoatHanger` | 衣架 | commerce, objects |
| 402 | `coda-logo` | `PhCodaLogo` | Coda Logo | brand |
| 403 | `code` | `PhCode` | 代码 (</>) | development, editor |
| 404 | `code-block` | `PhCodeBlock` | 代码块 | development, editor |
| 405 | `code-simple` | `PhCodeSimple` | 简易代码符号 | development, editor |
| 406 | `codepen-logo` | `PhCodepenLogo` | CodePen Logo | brand, development |
| 407 | `codesandbox-logo` | `PhCodesandboxLogo` | CodeSandbox Logo | brand, development |
| 408 | `coffee` | `PhCoffee` | 咖啡杯 | commerce, objects, map |
| 409 | `coffee-bean` | `PhCoffeeBean` | coffee-bean | commerce, map, nature |
| 410 | `coin` | `PhCoin` | 硬币/金币 | commerce, finance |
| 411 | `coin-vertical` | `PhCoinVertical` | coin-vertical | commerce, finance |
| 412 | `coins` | `PhCoins` | 堆叠金币 | commerce, finance |
| 413 | `columns` | `PhColumns` | 多列布局 | design |
| 414 | `columns-plus-left` | `PhColumnsPlusLeft` | columns-plus-left | design |
| 415 | `columns-plus-right` | `PhColumnsPlusRight` | columns-plus-right | design |
| 416 | `command` | `PhCommand` | Command 键 (⌘) | editor, system |
| 417 | `compass` | `PhCompass` | 指南针 | map, objects |
| 418 | `compass-rose` | `PhCompassRose` | compass-rose | map, objects |
| 419 | `compass-tool` | `PhCompassTool` | 圆规工具 | design, objects |
| 420 | `computer-tower` | `PhComputerTower` | 电脑主机箱 | development, objects |
| 421 | `confetti` | `PhConfetti` | 五彩纸屑/庆祝 | communication |
| 422 | `contactless-payment` | `PhContactlessPayment` | 感应支付/刷卡 | commerce |
| 423 | `control` | `PhControl` | control | system |
| 424 | `cookie` | `PhCookie` | 曲奇饼干 | map, objects, development |
| 425 | `cooking-pot` | `PhCookingPot` | 烹饪锅 | objects, commerce |
| 426 | `copy` | `PhCopy` | 复制 | editor, system |
| 427 | `copy-simple` | `PhCopySimple` | 简易复制 | editor, system |
| 428 | `copyleft` | `PhCopyleft` | 著佐权 (Copyleft) | commerce, media |
| 429 | `copyright` | `PhCopyright` | 版权所有 (©) | commerce, media |
| 430 | `corners-in` | `PhCornersIn` | 向内缩放角 | system |
| 431 | `corners-out` | `PhCornersOut` | 全屏/向外全屏角 | system |
| 432 | `couch` | `PhCouch` | couch | objects, commerce |
| 433 | `court-basketball` | `PhCourtBasketball` | court-basketball | games, health, map |
| 434 | `cow` | `PhCow` | cow | commerce, nature |
| 435 | `cowboy-hat` | `PhCowboyHat` | cowboy-hat | commerce, objects |
| 436 | `cpu` | `PhCpu` | CPU 芯片 | development |
| 437 | `crane` | `PhCrane` | crane | commerce, development |
| 438 | `crane-tower` | `PhCraneTower` | crane-tower | commerce, development |
| 439 | `credit-card` | `PhCreditCard` | 信用卡 | commerce, finance |
| 440 | `cricket` | `PhCricket` | cricket | games, health |
| 441 | `crop` | `PhCrop` | 裁剪工具 | design, editor |
| 442 | `cross` | `PhCross` | 十字架 | design, communication |
| 443 | `crosshair` | `PhCrosshair` | 准星/瞄准器 | map, system |
| 444 | `crosshair-simple` | `PhCrosshairSimple` | crosshair简易 | map, system |
| 445 | `crown` | `PhCrown` | 皇冠/VIP | games, objects |
| 446 | `crown-cross` | `PhCrownCross` | crown-cross | games, objects |
| 447 | `crown-simple` | `PhCrownSimple` | 简易皇冠 | games, objects |
| 448 | `cube` | `PhCube` | 立方体/三维体 | design, games, objects |
| 449 | `cube-focus` | `PhCubeFocus` | cube-focus | games, objects |
| 450 | `cube-transparent` | `PhCubeTransparent` | cube-transparent | design, games, objects |
| 451 | `currency-btc` | `PhCurrencyBtc` | 比特币符号 (₿) | commerce, finance |
| 452 | `currency-circle-dollar` | `PhCurrencyCircleDollar` | currency圆圈-dollar | commerce, finance |
| 453 | `currency-cny` | `PhCurrencyCny` | 人民币符号 (¥) | commerce, finance |
| 454 | `currency-dollar` | `PhCurrencyDollar` | 美元符号 ($) | commerce, finance |
| 455 | `currency-dollar-simple` | `PhCurrencyDollarSimple` | currency-dollar简易 | commerce, finance |
| 456 | `currency-eth` | `PhCurrencyEth` | 以太坊符号 (Ξ) | commerce, finance |
| 457 | `currency-eur` | `PhCurrencyEur` | 欧元符号 (€) | commerce, finance |
| 458 | `currency-gbp` | `PhCurrencyGbp` | 英镑符号 (£) | commerce, finance |
| 459 | `currency-inr` | `PhCurrencyInr` | 印度卢比符号 (₹) | commerce, finance |
| 460 | `currency-jpy` | `PhCurrencyJpy` | 日元符号 (¥) | commerce, finance |
| 461 | `currency-krw` | `PhCurrencyKrw` | 韩元符号 (₩) | commerce, finance |
| 462 | `currency-kzt` | `PhCurrencyKzt` | currency-kzt | commerce, finance |
| 463 | `currency-ngn` | `PhCurrencyNgn` | currency-ngn | commerce, finance |
| 464 | `currency-rub` | `PhCurrencyRub` | 卢布符号 (₽) | commerce, finance |
| 465 | `cursor` | `PhCursor` | 鼠标光标 | design, system |
| 466 | `cursor-click` | `PhCursorClick` | 鼠标点击光标 | design, system |
| 467 | `cursor-text` | `PhCursorText` | 文本输入光标 (I型) | editor, system |
| 468 | `cylinder` | `PhCylinder` | 圆柱体 | design |
| 469 | `database` | `PhDatabase` | 数据库 | development, system |
| 470 | `desk` | `PhDesk` | desk | commerce, objects, office |
| 471 | `desktop` | `PhDesktop` | 台式电脑/显示器 | development, objects |
| 472 | `desktop-tower` | `PhDesktopTower` | desktop-tower | development, objects |
| 473 | `detective` | `PhDetective` | detective | people, system |
| 474 | `dev-to-logo` | `PhDevToLogo` | dev-to 标志 | brand, development |
| 475 | `device-mobile` | `PhDeviceMobile` | 移动手机 | objects |
| 476 | `device-mobile-camera` | `PhDeviceMobileCamera` | device-mobile-camera | objects |
| 477 | `device-mobile-slash` | `PhDeviceMobileSlash` | device-mobile-slash | objects, system |
| 478 | `device-mobile-speaker` | `PhDeviceMobileSpeaker` | device-mobile-speaker | objects |
| 479 | `device-rotate` | `PhDeviceRotate` | device-rotate | objects, system |
| 480 | `device-tablet` | `PhDeviceTablet` | 平板电脑 | objects |
| 481 | `device-tablet-camera` | `PhDeviceTabletCamera` | device-tablet-camera | objects |
| 482 | `device-tablet-speaker` | `PhDeviceTabletSpeaker` | device-tablet-speaker | objects |
| 483 | `devices` | `PhDevices` | 多设备终端 | objects |
| 484 | `diamond` | `PhDiamond` | diamond | design, games |
| 485 | `diamonds-four` | `PhDiamondsFour` | diamonds-four | design |
| 486 | `dice-five` | `PhDiceFive` | 骰子 5 点 | games, objects |
| 487 | `dice-four` | `PhDiceFour` | 骰子 4 点 | games, objects |
| 488 | `dice-one` | `PhDiceOne` | 骰子 1 点 | games, objects |
| 489 | `dice-six` | `PhDiceSix` | 骰子 6 点 | games, objects |
| 490 | `dice-three` | `PhDiceThree` | 骰子 3 点 | games, objects |
| 491 | `dice-two` | `PhDiceTwo` | 骰子 2 点 | games, objects |
| 492 | `disc` | `PhDisc` | 光盘/唱片 | development, media, objects |
| 493 | `disco-ball` | `PhDiscoBall` | disco-ball | games, map, objects |
| 494 | `discord-logo` | `PhDiscordLogo` | Discord 标识 | brand, communication |
| 495 | `divide` | `PhDivide` | 除号 (÷) | development, finance |
| 496 | `dna` | `PhDna` | DNA 基因链 | health, nature |
| 497 | `dog` | `PhDog` | 狗 | nature |
| 498 | `door` | `PhDoor` | 门 | objects |
| 499 | `door-open` | `PhDoorOpen` | 打开的门 | objects |
| 500 | `dot` | `PhDot` | dot | system |
| 501 | `dot-outline` | `PhDotOutline` | dot-outline | system |
| 502 | `dots-nine` | `PhDotsNine` | dots-nine | design |
| 503 | `dots-six` | `PhDotsSix` | dots-six | system |
| 504 | `dots-six-vertical` | `PhDotsSixVertical` | dots-six-vertical | system |
| 505 | `dots-three` | `PhDotsThree` | 三点菜单 (省略号) | system |
| 506 | `dots-three-circle` | `PhDotsThreeCircle` | 圆圈三点菜单 | system |
| 507 | `dots-three-circle-vertical` | `PhDotsThreeCircleVertical` | dots-three圆圈-vertical | system |
| 508 | `dots-three-outline` | `PhDotsThreeOutline` | 轮廓三点 | system |
| 509 | `dots-three-outline-vertical` | `PhDotsThreeOutlineVertical` | dots-three-outline-vertical | system |
| 510 | `dots-three-vertical` | `PhDotsThreeVertical` | 垂直三点菜单 | system |
| 511 | `download` | `PhDownload` | 下载 | system |
| 512 | `download-simple` | `PhDownloadSimple` | 简易下载 | system |
| 513 | `dress` | `PhDress` | 连衣裙 | commerce, objects |
| 514 | `dresser` | `PhDresser` | dresser | commerce, objects |
| 515 | `dribbble-logo` | `PhDribbbleLogo` | Dribbble 标志 | brand, design |
| 516 | `drone` | `PhDrone` | drone | games, objects, development |
| 517 | `drop` | `PhDrop` | 水滴/滴管 | nature, weather |
| 518 | `drop-half` | `PhDropHalf` | 半水滴 | design, editor, nature, weather |
| 519 | `drop-half-bottom` | `PhDropHalfBottom` | 下半水滴 | design, editor, nature, weather |
| 520 | `drop-simple` | `PhDropSimple` | drop简易 | design, editor, nature, weather |
| 521 | `drop-slash` | `PhDropSlash` | drop-slash | design, editor, nature, weather |
| 522 | `dropbox-logo` | `PhDropboxLogo` | dropbox 标志 | brand |
| 523 | `ear` | `PhEar` | 耳朵 | media, system |
| 524 | `ear-slash` | `PhEarSlash` | 助听/静音耳 | media, system |
| 525 | `egg` | `PhEgg` | 鸡蛋 | commerce, nature |
| 526 | `egg-crack` | `PhEggCrack` | 破壳鸡蛋 | commerce, nature |
| 527 | `eject` | `PhEject` | 弹出光盘 | media |
| 528 | `eject-simple` | `PhEjectSimple` | eject简易 | media |
| 529 | `elevator` | `PhElevator` | elevator | objects, map |
| 530 | `empty` | `PhEmpty` | empty | finance, development |
| 531 | `engine` | `PhEngine` | engine | map, objects |
| 532 | `envelope` | `PhEnvelope` | 信封/邮件 | communication |
| 533 | `envelope-open` | `PhEnvelopeOpen` | 打开的信封 | communication |
| 534 | `envelope-simple` | `PhEnvelopeSimple` | 简易信封 | communication |
| 535 | `envelope-simple-open` | `PhEnvelopeSimpleOpen` | 简易打开信封 | communication |
| 536 | `equalizer` | `PhEqualizer` | equalizer | media, system |
| 537 | `equals` | `PhEquals` | equals | development, finance |
| 538 | `eraser` | `PhEraser` | 橡皮擦 | design, editor |
| 539 | `escalator-down` | `PhEscalatorDown` | escalator-down | map, objects |
| 540 | `escalator-up` | `PhEscalatorUp` | escalator-up | map, objects |
| 541 | `exam` | `PhExam` | exam | objects |
| 542 | `exclamation-mark` | `PhExclamationMark` | exclamation-mark | system |
| 543 | `exclude` | `PhExclude` | exclude | design, editor |
| 544 | `exclude-square` | `PhExcludeSquare` | exclude方形 | design, editor |
| 545 | `export` | `PhExport` | export | communication, system |
| 546 | `eye` | `PhEye` | 眼睛/显示/预览 | design, editor |
| 547 | `eye-closed` | `PhEyeClosed` | 闭眼 | design, editor |
| 548 | `eye-slash` | `PhEyeSlash` | 隐藏/不可见 | design, editor |
| 549 | `eyedropper` | `PhEyedropper` | 吸管/取色器 | design, editor, objects |
| 550 | `eyedropper-sample` | `PhEyedropperSample` | eyedropper-sample | design, editor, objects |
| 551 | `eyeglasses` | `PhEyeglasses` | eyeglasses | health, objects |
| 552 | `eyes` | `PhEyes` | eyes | people |
| 553 | `face-mask` | `PhFaceMask` | 口罩 | health |
| 554 | `facebook-logo` | `PhFacebookLogo` | Facebook 标志 | brand, communication |
| 555 | `factory` | `PhFactory` | 工厂/车间 | commerce, map |
| 556 | `faders` | `PhFaders` | faders | media, system |
| 557 | `faders-horizontal` | `PhFadersHorizontal` | faders-horizontal | media, system |
| 558 | `fallout-shelter` | `PhFalloutShelter` | fallout-shelter | health |
| 559 | `fan` | `PhFan` | fan | commerce, objects |
| 560 | `farm` | `PhFarm` | farm | commerce, nature, map |
| 561 | `fast-forward` | `PhFastForward` | fast-forward | media, system |
| 562 | `fast-forward-circle` | `PhFastForwardCircle` | fast-forward圆圈 | media, system |
| 563 | `feather` | `PhFeather` | feather | nature, objects |
| 564 | `fediverse-logo` | `PhFediverseLogo` | fediverse 标志 | brand, communication |
| 565 | `figma-logo` | `PhFigmaLogo` | Figma 标志 | brand, design |
| 566 | `file` | `PhFile` | 文件 | office, editor |
| 567 | `file-archive` | `PhFileArchive` | 文件 archive | system, office, editor |
| 568 | `file-arrow-down` | `PhFileArrowDown` | 下载文件 | office, editor |
| 569 | `file-arrow-up` | `PhFileArrowUp` | 上传文件 | office, editor |
| 570 | `file-audio` | `PhFileAudio` | 音频文件 | office, editor, media |
| 571 | `file-c` | `PhFileC` | C语言源码文件 | office, editor, development |
| 572 | `file-c-sharp` | `PhFileCSharp` | C# 源码文件 | office, editor, development |
| 573 | `file-cloud` | `PhFileCloud` | 文件 cloud | office, editor, system |
| 574 | `file-code` | `PhFileCode` | 代码文件 | office, editor, development |
| 575 | `file-cpp` | `PhFileCpp` | C++ 源码文件 | office, editor, development |
| 576 | `file-css` | `PhFileCss` | CSS 样式表文件 | office, editor, development |
| 577 | `file-csv` | `PhFileCsv` | CSV 表格文件 | office, editor |
| 578 | `file-dashed` | `PhFileDashed` | 文件 dashed | office, editor |
| 579 | `file-doc` | `PhFileDoc` | Word 文档文件 | office, editor |
| 580 | `file-html` | `PhFileHtml` | HTML 网页文件 | office, editor, development |
| 581 | `file-image` | `PhFileImage` | 图片文件 | office, editor, media |
| 582 | `file-ini` | `PhFileIni` | 文件 ini | office, editor, development |
| 583 | `file-jpg` | `PhFileJpg` | JPG 图片文件 | office, editor, media |
| 584 | `file-js` | `PhFileJs` | JS 脚本文件 | office, editor, development |
| 585 | `file-jsx` | `PhFileJsx` | JSX 组件文件 | office, editor, development |
| 586 | `file-lock` | `PhFileLock` | 加密文件 | office, editor, system |
| 587 | `file-magnifying-glass` | `PhFileMagnifyingGlass` | 文件 magnifying-glass | office, editor |
| 588 | `file-md` | `PhFileMd` | 文件 md | office, editor, development |
| 589 | `file-minus` | `PhFileMinus` | 删除/减少文件 | office, editor |
| 590 | `file-pdf` | `PhFilePdf` | PDF 文档 | office, editor |
| 591 | `file-plus` | `PhFilePlus` | 新建/添加文件 | office, editor |
| 592 | `file-png` | `PhFilePng` | PNG 图片文件 | office, editor, media |
| 593 | `file-ppt` | `PhFilePpt` | PPT 演示文稿 | office, editor |
| 594 | `file-py` | `PhFilePy` | Python 脚本文件 | office, editor, development |
| 595 | `file-rs` | `PhFileRs` | 文件 rs | office, editor, development |
| 596 | `file-sql` | `PhFileSql` | 文件 sql | system, development |
| 597 | `file-svg` | `PhFileSvg` | 文件 svg | system, media |
| 598 | `file-text` | `PhFileText` | 文本文件 | office, editor |
| 599 | `file-ts` | `PhFileTs` | TypeScript 文件 | office, editor, development |
| 600 | `file-tsx` | `PhFileTsx` | TSX 组件文件 | office, editor, development |
| 601 | `file-txt` | `PhFileTxt` | 文件 txt | office, editor, development |
| 602 | `file-video` | `PhFileVideo` | 视频文件 | office, editor, media |
| 603 | `file-vue` | `PhFileVue` | 文件 vue | office, editor, development |
| 604 | `file-x` | `PhFileX` | 文件 x | office, editor |
| 605 | `file-xls` | `PhFileXls` | 文件 xls | office, editor |
| 606 | `file-zip` | `PhFileZip` | 压缩包文件 | office, editor, system |
| 607 | `files` | `PhFiles` | 多文件 | office, editor |
| 608 | `film-reel` | `PhFilmReel` | 胶卷拷贝 | media, objects |
| 609 | `film-script` | `PhFilmScript` | 电影剧本 | office, media |
| 610 | `film-slate` | `PhFilmSlate` | 场记板 | media, objects |
| 611 | `film-strip` | `PhFilmStrip` | film-strip | media |
| 612 | `fingerprint` | `PhFingerprint` | 指纹 | system |
| 613 | `fingerprint-simple` | `PhFingerprintSimple` | fingerprint简易 | system |
| 614 | `finn-the-human` | `PhFinnTheHuman` | finn-the-human | games |
| 615 | `fire` | `PhFire` | 火焰/热门 | nature, weather |
| 616 | `fire-extinguisher` | `PhFireExtinguisher` | 灭火器 | objects |
| 617 | `fire-simple` | `PhFireSimple` | fire简易 | nature, weather |
| 618 | `fire-truck` | `PhFireTruck` | fire-truck | health |
| 619 | `first-aid` | `PhFirstAid` | 急救箱 | health |
| 620 | `first-aid-kit` | `PhFirstAidKit` | 急救包 | health |
| 621 | `fish` | `PhFish` | 鱼 | nature, commerce |
| 622 | `fish-simple` | `PhFishSimple` | 简易鱼 | nature, commerce |
| 623 | `flag` | `PhFlag` | 旗帜 | objects, map, system |
| 624 | `flag-banner` | `PhFlagBanner` | 横幅旗 | objects, map, system |
| 625 | `flag-banner-fold` | `PhFlagBannerFold` | flag-banner-fold | objects, map, system |
| 626 | `flag-checkered` | `PhFlagCheckered` | 终点格仔旗 | map, objects, games |
| 627 | `flag-pennant` | `PhFlagPennant` | flag-pennant | objects, map, system, games |
| 628 | `flame` | `PhFlame` | 火苗 | nature, weather |
| 629 | `flashlight` | `PhFlashlight` | 手电筒 | system, objects |
| 630 | `flask` | `PhFlask` | 实验烧瓶 | development, nature, objects |
| 631 | `flip-horizontal` | `PhFlipHorizontal` | flip-horizontal | design, editor |
| 632 | `flip-vertical` | `PhFlipVertical` | flip-vertical | design, editor |
| 633 | `floppy-disk` | `PhFloppyDisk` | 软盘/保存 | office, editor, system |
| 634 | `floppy-disk-back` | `PhFloppyDiskBack` | 软盘背面 | office, editor, system |
| 635 | `flow-arrow` | `PhFlowArrow` | flow-arrow | arrows, design, office |
| 636 | `flower` | `PhFlower` | 花朵 | nature |
| 637 | `flower-lotus` | `PhFlowerLotus` | 莲花 | nature |
| 638 | `flower-tulip` | `PhFlowerTulip` | 郁金香 | nature |
| 639 | `flying-saucer` | `PhFlyingSaucer` | flying-saucer | games, objects |
| 640 | `folder` | `PhFolder` | 文件夹 | office, editor, system |
| 641 | `folder-dashed` | `PhFolderDashed` | 虚线文件夹 | office, editor, system |
| 642 | `folder-lock` | `PhFolderLock` | 加密文件夹 | office, editor, system |
| 643 | `folder-minus` | `PhFolderMinus` | 删除文件夹 | office, editor, system |
| 644 | `folder-open` | `PhFolderOpen` | 打开的文件夹 | office, editor, system |
| 645 | `folder-plus` | `PhFolderPlus` | 新建文件夹 | office, editor, system |
| 646 | `folder-simple` | `PhFolderSimple` | 简易文件夹 | office, editor, system |
| 647 | `folder-simple-dashed` | `PhFolderSimpleDashed` | folder简易-dashed | office, editor, system |
| 648 | `folder-simple-lock` | `PhFolderSimpleLock` | folder简易-lock | office, editor, system |
| 649 | `folder-simple-minus` | `PhFolderSimpleMinus` | folder简易-minus | office, editor, system |
| 650 | `folder-simple-plus` | `PhFolderSimplePlus` | folder简易-plus | office, editor, system |
| 651 | `folder-simple-star` | `PhFolderSimpleStar` | folder简易-star | office, editor, system |
| 652 | `folder-simple-user` | `PhFolderSimpleUser` | folder简易-user | office, editor, system |
| 653 | `folder-star` | `PhFolderStar` | folder-star | office, editor, system |
| 654 | `folder-user` | `PhFolderUser` | 用户文件夹 | office, editor, system |
| 655 | `folders` | `PhFolders` | 多文件夹 | office, editor, system |
| 656 | `football` | `PhFootball` | 橄榄球 | games, health, objects |
| 657 | `football-helmet` | `PhFootballHelmet` | football-helmet | games, health, objects |
| 658 | `footprints` | `PhFootprints` | footprints | health, map |
| 659 | `fork-knife` | `PhForkKnife` | 刀叉/餐饮 | commerce, map, objects |
| 660 | `four-k` | `PhFourK` | four-k | media |
| 661 | `frame-corners` | `PhFrameCorners` | 框架四角 | system |
| 662 | `framer-logo` | `PhFramerLogo` | Framer 标志 | brand, design |
| 663 | `function` | `PhFunction` | function | development |
| 664 | `funnel` | `PhFunnel` | 漏斗/筛选 | editor, objects |
| 665 | `funnel-simple` | `PhFunnelSimple` | funnel简易 | editor, objects |
| 666 | `funnel-simple-x` | `PhFunnelSimpleX` | funnel简易-x | editor, objects |
| 667 | `funnel-x` | `PhFunnelX` | funnel-x | editor, objects |
| 668 | `game-controller` | `PhGameController` | 游戏手柄 | games, media, objects |
| 669 | `garage` | `PhGarage` | 车库 | commerce, map |
| 670 | `gas-can` | `PhGasCan` | gas-can | map, objects |
| 671 | `gas-pump` | `PhGasPump` | 加油机 | map, objects |
| 672 | `gauge` | `PhGauge` | 仪表盘 | development, objects, system |
| 673 | `gavel` | `PhGavel` | gavel | commerce, objects |
| 674 | `gear` | `PhGear` | 设置/齿轮 | system |
| 675 | `gear-fine` | `PhGearFine` | 精细齿轮 | system |
| 676 | `gear-six` | `PhGearSix` | 六齿齿轮 | system |
| 677 | `gender-female` | `PhGenderFemale` | 女性符号 (♀) | people |
| 678 | `gender-intersex` | `PhGenderIntersex` | gender-intersex | people |
| 679 | `gender-male` | `PhGenderMale` | 男性符号 (♂) | people |
| 680 | `gender-neuter` | `PhGenderNeuter` | gender-neuter | people |
| 681 | `gender-nonbinary` | `PhGenderNonbinary` | gender-nonbinary | people |
| 682 | `gender-transgender` | `PhGenderTransgender` | gender-transgender | people |
| 683 | `ghost` | `PhGhost` | 幽灵/鬼魂 | games, objects |
| 684 | `gif` | `PhGif` | GIF 动图标识 | media |
| 685 | `gift` | `PhGift` | 礼物盒 | commerce, objects |
| 686 | `git-branch` | `PhGitBranch` | Git 分支 | development |
| 687 | `git-commit` | `PhGitCommit` | Git 提交 | development |
| 688 | `git-diff` | `PhGitDiff` | git-diff | development |
| 689 | `git-fork` | `PhGitFork` | Git Fork 分线 | development |
| 690 | `git-merge` | `PhGitMerge` | Git 合并 | development |
| 691 | `git-pull-request` | `PhGitPullRequest` | Git PR 拉取请求 | development |
| 692 | `github-logo` | `PhGithubLogo` | GitHub 标志 | development, brand |
| 693 | `gitlab-logo` | `PhGitlabLogo` | GitLab 标志 | brand, development |
| 694 | `gitlab-logo-simple` | `PhGitlabLogoSimple` | gitlab 标志简易 | brand, development |
| 695 | `globe` | `PhGlobe` | 地球仪/网络 | map |
| 696 | `globe-hemisphere-east` | `PhGlobeHemisphereEast` | 东半球 | map |
| 697 | `globe-hemisphere-west` | `PhGlobeHemisphereWest` | 西半球 | map |
| 698 | `globe-simple` | `PhGlobeSimple` | globe简易 | map |
| 699 | `globe-simple-x` | `PhGlobeSimpleX` | globe简易-x | map |
| 700 | `globe-stand` | `PhGlobeStand` | 台式地球仪 | map |
| 701 | `globe-x` | `PhGlobeX` | globe-x | map |
| 702 | `goggles` | `PhGoggles` | 护目镜/泳镜 | health, objects |
| 703 | `golf` | `PhGolf` | golf | games, health, objects |
| 704 | `goodreads-logo` | `PhGoodreadsLogo` | Goodreads 标志 | brand |
| 705 | `google-cardboard-logo` | `PhGoogleCardboardLogo` | google-cardboard 标志 | brand |
| 706 | `google-chrome-logo` | `PhGoogleChromeLogo` | Chrome 浏览器 Logo | brand |
| 707 | `google-drive-logo` | `PhGoogleDriveLogo` | 谷歌云盘 Logo | brand |
| 708 | `google-logo` | `PhGoogleLogo` | 谷歌 Logo | brand |
| 709 | `google-photos-logo` | `PhGooglePhotosLogo` | 谷歌相册 Logo | brand, media |
| 710 | `google-play-logo` | `PhGooglePlayLogo` | Google Play 商店 Logo | brand, system, media |
| 711 | `google-podcasts-logo` | `PhGooglePodcastsLogo` | 谷歌播客 Logo | brand, media |
| 712 | `gps` | `PhGps` | gps | map, system |
| 713 | `gps-fix` | `PhGpsFix` | gps-fix | map, system |
| 714 | `gps-slash` | `PhGpsSlash` | gps-slash | map, system |
| 715 | `gradient` | `PhGradient` | 渐变 | design |
| 716 | `graduation-cap` | `PhGraduationCap` | 学士帽/毕业 | map, objects |
| 717 | `grains` | `PhGrains` | grains | commerce, nature |
| 718 | `grains-slash` | `PhGrainsSlash` | grains-slash | commerce |
| 719 | `graph` | `PhGraph` | 统计图表 | office, development |
| 720 | `graphics-card` | `PhGraphicsCard` | graphics-card | development |
| 721 | `greater-than` | `PhGreaterThan` | greater-than | finance, development |
| 722 | `greater-than-or-equal` | `PhGreaterThanOrEqual` | greater-than-or-equal | finance, development |
| 723 | `grid-four` | `PhGridFour` | 四宫格 | design, system |
| 724 | `grid-nine` | `PhGridNine` | 九宫格 | design, system |
| 725 | `guitar` | `PhGuitar` | 吉他 | media, objects |
| 726 | `hair-dryer` | `PhHairDryer` | hair-dryer | commerce, objects |
| 727 | `hamburger` | `PhHamburger` | 汉堡包 | commerce, map |
| 728 | `hammer` | `PhHammer` | 锤子 | objects, system, commerce |
| 729 | `hand` | `PhHand` | 手掌 | system, people |
| 730 | `hand-arrow-down` | `PhHandArrowDown` | hand-箭头 down | people, commerce, finance |
| 731 | `hand-arrow-up` | `PhHandArrowUp` | hand-箭头 up | people, commerce, finance |
| 732 | `hand-coins` | `PhHandCoins` | 手托硬币 (理财) | people, commerce, finance |
| 733 | `hand-deposit` | `PhHandDeposit` | hand-deposit | people, commerce, finance |
| 734 | `hand-eye` | `PhHandEye` | hand-eye | people |
| 735 | `hand-fist` | `PhHandFist` | hand-fist | people |
| 736 | `hand-grabbing` | `PhHandGrabbing` | hand-grabbing | system, people |
| 737 | `hand-heart` | `PhHandHeart` | 手托爱心 (爱心捐赠) | people |
| 738 | `hand-palm` | `PhHandPalm` | hand-palm | system, people |
| 739 | `hand-peace` | `PhHandPeace` | hand-peace | people, communication |
| 740 | `hand-pointing` | `PhHandPointing` | 手指点击 | system, people |
| 741 | `hand-soap` | `PhHandSoap` | hand-soap | health, objects |
| 742 | `hand-swipe-left` | `PhHandSwipeLeft` | hand-swipe-left | people, system |
| 743 | `hand-swipe-right` | `PhHandSwipeRight` | hand-swipe-right | people, system |
| 744 | `hand-tap` | `PhHandTap` | hand-tap | people, system |
| 745 | `hand-waving` | `PhHandWaving` | hand-waving | system, people |
| 746 | `hand-withdraw` | `PhHandWithdraw` | hand-withdraw | people, commerce, finance |
| 747 | `handbag` | `PhHandbag` | handbag | commerce, objects |
| 748 | `handbag-simple` | `PhHandbagSimple` | handbag简易 | commerce, objects |
| 749 | `hands-clapping` | `PhHandsClapping` | hands-clapping | system, people |
| 750 | `hands-praying` | `PhHandsPraying` | hands-praying | people |
| 751 | `handshake` | `PhHandshake` | 握手 (合作) | people, commerce |
| 752 | `hard-drive` | `PhHardDrive` | 硬盘 | system |
| 753 | `hard-drives` | `PhHardDrives` | 硬盘阵列/服务器 | system |
| 754 | `hard-hat` | `PhHardHat` | hard-hat | commerce, objects, development |
| 755 | `hash` | `PhHash` | 井号/标签 (#) | communication |
| 756 | `hash-straight` | `PhHashStraight` | hash-straight | communication |
| 757 | `head-circuit` | `PhHeadCircuit` | head-circuit | development |
| 758 | `headlights` | `PhHeadlights` | headlights | map, objects |
| 759 | `headphones` | `PhHeadphones` | 耳机 | media, objects |
| 760 | `headset` | `PhHeadset` | 客服头戴耳机 | media, games, objects |
| 761 | `heart` | `PhHeart` | 爱心/收藏 | communication, games, health |
| 762 | `heart-break` | `PhHeartBreak` | 心碎 | communication |
| 763 | `heart-half` | `PhHeartHalf` | heart-half | communication, games, health |
| 764 | `heart-straight` | `PhHeartStraight` | 直边爱心 | communication, games, health |
| 765 | `heart-straight-break` | `PhHeartStraightBreak` | heart-straight-break | communication |
| 766 | `heartbeat` | `PhHeartbeat` | 心率脉搏 | health, system |
| 767 | `hexagon` | `PhHexagon` | 六边形 | design |
| 768 | `high-definition` | `PhHighDefinition` | high-definition | media |
| 769 | `high-heel` | `PhHighHeel` | 高跟鞋 | commerce, objects |
| 770 | `highlighter` | `PhHighlighter` | highlighter | design, editor, office |
| 771 | `highlighter-circle` | `PhHighlighterCircle` | 荧光高亮笔 | design, editor, office |
| 772 | `hockey` | `PhHockey` | 冰球 | games, health, objects |
| 773 | `hoodie` | `PhHoodie` | 连帽衫 | commerce, objects |
| 774 | `horse` | `PhHorse` | 马 | games, health, nature |
| 775 | `hospital` | `PhHospital` | 医院 | map, health |
| 776 | `hourglass` | `PhHourglass` | 沙漏 | system, objects |
| 777 | `hourglass-high` | `PhHourglassHigh` | hourglass-high | system, objects |
| 778 | `hourglass-low` | `PhHourglassLow` | hourglass-low | system, objects |
| 779 | `hourglass-medium` | `PhHourglassMedium` | hourglass-medium | system, objects |
| 780 | `hourglass-simple` | `PhHourglassSimple` | hourglass简易 | system, objects |
| 781 | `hourglass-simple-high` | `PhHourglassSimpleHigh` | hourglass简易-high | system, objects |
| 782 | `hourglass-simple-low` | `PhHourglassSimpleLow` | hourglass简易-low | system, objects |
| 783 | `hourglass-simple-medium` | `PhHourglassSimpleMedium` | hourglass简易-medium | system, objects |
| 784 | `house` | `PhHouse` | 首页/房屋 | map, system |
| 785 | `house-line` | `PhHouseLine` | 线条房屋 | map, system |
| 786 | `house-simple` | `PhHouseSimple` | 简易房屋 | map, system |
| 787 | `hurricane` | `PhHurricane` | hurricane | weather |
| 788 | `ice-cream` | `PhIceCream` | 冰淇淋 | commerce, map, objects |
| 789 | `identification-badge` | `PhIdentificationBadge` | 工作证/识别牌 | people |
| 790 | `identification-card` | `PhIdentificationCard` | 身份证件卡 | people |
| 791 | `image` | `PhImage` | 图片 | media, system |
| 792 | `image-broken` | `PhImageBroken` | image-broken | media, system |
| 793 | `image-square` | `PhImageSquare` | 方形图片 | media, system |
| 794 | `images` | `PhImages` | 多张图片 | media, system |
| 795 | `images-square` | `PhImagesSquare` | 多张方形图片 | media, system |
| 796 | `infinity` | `PhInfinity` | 无限符号 (∞) | development, finance |
| 797 | `info` | `PhInfo` | 信息提示 (i) | system |
| 798 | `instagram-logo` | `PhInstagramLogo` | Instagram 标志 | brand, communication |
| 799 | `intersect` | `PhIntersect` | 相交/交集 | design, editor |
| 800 | `intersect-square` | `PhIntersectSquare` | intersect方形 | design, editor |
| 801 | `intersect-three` | `PhIntersectThree` | intersect-three | people, design, editor |
| 802 | `intersection` | `PhIntersection` | intersection | finance, development |
| 803 | `invoice` | `PhInvoice` | invoice | commerce, finance, office |
| 804 | `island` | `PhIsland` | island | map, nature |
| 805 | `jar` | `PhJar` | jar | commerce, objects |
| 806 | `jar-label` | `PhJarLabel` | jar-label | commerce, objects |
| 807 | `jeep` | `PhJeep` | 越野吉普车 | map, objects |
| 808 | `joystick` | `PhJoystick` | joystick | games, media, objects |
| 809 | `kanban` | `PhKanban` | kanban | office |
| 810 | `key` | `PhKey` | 钥匙 | objects, system |
| 811 | `key-return` | `PhKeyReturn` | key-return | system |
| 812 | `keyboard` | `PhKeyboard` | 键盘 | system |
| 813 | `keyhole` | `PhKeyhole` | 锁孔 | objects, system |
| 814 | `knife` | `PhKnife` | 餐刀 | commerce, objects |
| 815 | `ladder` | `PhLadder` | 梯子 | objects |
| 816 | `ladder-simple` | `PhLadderSimple` | ladder简易 | objects |
| 817 | `lamp` | `PhLamp` | lamp | objects, commerce |
| 818 | `lamp-pendant` | `PhLampPendant` | lamp-pendant | commerce, objects |
| 819 | `laptop` | `PhLaptop` | 笔记本电脑 | development, objects |
| 820 | `lasso` | `PhLasso` | lasso | design, objects |
| 821 | `lastfm-logo` | `PhLastfmLogo` | lastfm 标志 | brand, media |
| 822 | `layout` | `PhLayout` | 页面布局 | design, editor |
| 823 | `leaf` | `PhLeaf` | 树叶 | nature |
| 824 | `lectern` | `PhLectern` | lectern | objects, finance, office |
| 825 | `lego` | `PhLego` | lego | games |
| 826 | `lego-smiley` | `PhLegoSmiley` | lego-smiley | games, communication, people |
| 827 | `less-than` | `PhLessThan` | less-than | finance, development |
| 828 | `less-than-or-equal` | `PhLessThanOrEqual` | less-than-or-equal | finance, development |
| 829 | `letter-circle-h` | `PhLetterCircleH` | letter圆圈-h | editor, map, design |
| 830 | `letter-circle-p` | `PhLetterCircleP` | letter圆圈-p | editor, map, design |
| 831 | `letter-circle-v` | `PhLetterCircleV` | letter圆圈-v | editor, design, commerce |
| 832 | `lifebuoy` | `PhLifebuoy` | 救生圈 | health, objects, system |
| 833 | `lightbulb` | `PhLightbulb` | 电灯泡/灵感 | system, objects |
| 834 | `lightbulb-filament` | `PhLightbulbFilament` | lightbulb-filament | system, objects |
| 835 | `lighthouse` | `PhLighthouse` | lighthouse | map |
| 836 | `lightning` | `PhLightning` | 闪电/快速 | weather, system |
| 837 | `lightning-a` | `PhLightningA` | lightning-a | system |
| 838 | `lightning-slash` | `PhLightningSlash` | lightning-slash | system |
| 839 | `line-segment` | `PhLineSegment` | line-segment | design |
| 840 | `line-segments` | `PhLineSegments` | line-segments | design |
| 841 | `line-vertical` | `PhLineVertical` | line-vertical | design, development |
| 842 | `link` | `PhLink` | 链接 | communication, objects |
| 843 | `link-break` | `PhLinkBreak` | 断开链接 | communication, objects |
| 844 | `link-simple` | `PhLinkSimple` | link简易 | communication, objects |
| 845 | `link-simple-break` | `PhLinkSimpleBreak` | link简易-break | communication, objects |
| 846 | `link-simple-horizontal` | `PhLinkSimpleHorizontal` | link简易-horizontal | communication, objects |
| 847 | `link-simple-horizontal-break` | `PhLinkSimpleHorizontalBreak` | link简易-horizontal-break | communication, objects |
| 848 | `linkedin-logo` | `PhLinkedinLogo` | 领英 Logo | brand, communication |
| 849 | `linktree-logo` | `PhLinktreeLogo` | linktree 标志 | brand, communication |
| 850 | `linux-logo` | `PhLinuxLogo` | Linux 企鹅 Logo | brand, development |
| 851 | `list` | `PhList` | 列表 | system, editor |
| 852 | `list-bullets` | `PhListBullets` | 无序列表 | editor |
| 853 | `list-checks` | `PhListChecks` | 任务清单列表 | office, editor |
| 854 | `list-dashes` | `PhListDashes` | list-dashes | editor |
| 855 | `list-heart` | `PhListHeart` | list-heart | editor, system |
| 856 | `list-magnifying-glass` | `PhListMagnifyingGlass` | list-magnifying-glass | editor, system |
| 857 | `list-numbers` | `PhListNumbers` | 有序列表 | editor |
| 858 | `list-plus` | `PhListPlus` | list-plus | editor |
| 859 | `list-star` | `PhListStar` | list-star | editor, system |
| 860 | `lock` | `PhLock` | 锁定/锁 | objects, system |
| 861 | `lock-key` | `PhLockKey` | 钥匙锁 | objects, system |
| 862 | `lock-key-open` | `PhLockKeyOpen` | lock-key-open | objects, system |
| 863 | `lock-laminated` | `PhLockLaminated` | lock-laminated | objects, system |
| 864 | `lock-laminated-open` | `PhLockLaminatedOpen` | lock-laminated-open | objects, system |
| 865 | `lock-open` | `PhLockOpen` | 解锁 | objects, system |
| 866 | `lock-simple` | `PhLockSimple` | lock简易 | objects, system |
| 867 | `lock-simple-open` | `PhLockSimpleOpen` | lock简易-open | objects, system |
| 868 | `lockers` | `PhLockers` | lockers | map |
| 869 | `log` | `PhLog` | log | nature |
| 870 | `magic-wand` | `PhMagicWand` | 魔棒/AI魔法 | design, games, objects |
| 871 | `magnet` | `PhMagnet` | 磁铁/吸附 | development, objects |
| 872 | `magnet-straight` | `PhMagnetStraight` | magnet-straight | development, objects |
| 873 | `magnifying-glass` | `PhMagnifyingGlass` | 搜索/放大镜 | editor, system |
| 874 | `magnifying-glass-minus` | `PhMagnifyingGlassMinus` | magnifying-glass-minus | editor, system |
| 875 | `magnifying-glass-plus` | `PhMagnifyingGlassPlus` | magnifying-glass-plus | editor, system |
| 876 | `mailbox` | `PhMailbox` | mailbox | communication, objects, map |
| 877 | `map-pin` | `PhMapPin` | 地图定位大头针 | map |
| 878 | `map-pin-area` | `PhMapPinArea` | map-pin-area | map |
| 879 | `map-pin-line` | `PhMapPinLine` | map-pin-line | map |
| 880 | `map-pin-plus` | `PhMapPinPlus` | map-pin-plus | map |
| 881 | `map-pin-simple` | `PhMapPinSimple` | map-pin简易 | map |
| 882 | `map-pin-simple-area` | `PhMapPinSimpleArea` | map-pin简易-area | map |
| 883 | `map-pin-simple-line` | `PhMapPinSimpleLine` | map-pin简易-line | map |
| 884 | `map-trifold` | `PhMapTrifold` | map-trifold | map |
| 885 | `markdown-logo` | `PhMarkdownLogo` | Markdown 标志 | development, office, media, brand |
| 886 | `marker-circle` | `PhMarkerCircle` | marker圆圈 | design, editor, office |
| 887 | `martini` | `PhMartini` | martini | commerce, map, objects |
| 888 | `mask-happy` | `PhMaskHappy` | mask-happy | communication, games |
| 889 | `mask-sad` | `PhMaskSad` | mask-sad | communication, games |
| 890 | `mastodon-logo` | `PhMastodonLogo` | mastodon 标志 | brand, communication |
| 891 | `math-operations` | `PhMathOperations` | 数学运算符 | development, finance |
| 892 | `matrix-logo` | `PhMatrixLogo` | matrix 标志 | brand, communication |
| 893 | `medal` | `PhMedal` | 奖牌/勋章 | objects, games |
| 894 | `medal-military` | `PhMedalMilitary` | medal-military | objects, games |
| 895 | `medium-logo` | `PhMediumLogo` | Medium 标志 | brand |
| 896 | `megaphone` | `PhMegaphone` | 扩音器/喇叭 | communication, objects |
| 897 | `megaphone-simple` | `PhMegaphoneSimple` | megaphone简易 | communication, objects |
| 898 | `member-of` | `PhMemberOf` | member-of | finance, development |
| 899 | `memory` | `PhMemory` | memory | development |
| 900 | `messenger-logo` | `PhMessengerLogo` | messenger 标志 | brand, communication |
| 901 | `meta-logo` | `PhMetaLogo` | Meta 标志 | brand |
| 902 | `meteor` | `PhMeteor` | meteor | weather, nature |
| 903 | `metronome` | `PhMetronome` | metronome | objects, media |
| 904 | `microphone` | `PhMicrophone` | 麦克风 | communication, media, system |
| 905 | `microphone-slash` | `PhMicrophoneSlash` | microphone-slash | communication, media, system |
| 906 | `microphone-stage` | `PhMicrophoneStage` | microphone-stage | communication, media, system |
| 907 | `microscope` | `PhMicroscope` | microscope | nature, development, objects, health |
| 908 | `microsoft-excel-logo` | `PhMicrosoftExcelLogo` | Excel 标志 | brand, office |
| 909 | `microsoft-outlook-logo` | `PhMicrosoftOutlookLogo` | microsoft-outlook 标志 | brand, communication, office |
| 910 | `microsoft-powerpoint-logo` | `PhMicrosoftPowerpointLogo` | microsoft-powerpoint 标志 | brand, office |
| 911 | `microsoft-teams-logo` | `PhMicrosoftTeamsLogo` | Teams 标志 | brand, communication |
| 912 | `microsoft-word-logo` | `PhMicrosoftWordLogo` | Word 标志 | brand, editor, office |
| 913 | `minus` | `PhMinus` | 减号 (-) | development, finance, system |
| 914 | `minus-circle` | `PhMinusCircle` | minus圆圈 | development, finance, system |
| 915 | `minus-square` | `PhMinusSquare` | minus方形 | finance, system |
| 916 | `money` | `PhMoney` | 纸币/现金 | commerce, finance |
| 917 | `money-wavy` | `PhMoneyWavy` | money-wavy | finance, commerce |
| 918 | `monitor` | `PhMonitor` | 电脑显示器 | system |
| 919 | `monitor-arrow-up` | `PhMonitorArrowUp` | monitor-箭头 up | system, media |
| 920 | `monitor-play` | `PhMonitorPlay` | monitor-play | system, media |
| 921 | `moon` | `PhMoon` | 月亮/夜间模式 | nature, system, weather |
| 922 | `moon-stars` | `PhMoonStars` | moon-stars | nature, weather |
| 923 | `moped` | `PhMoped` | moped | map, objects |
| 924 | `moped-front` | `PhMopedFront` | moped-front | map, objects |
| 925 | `mosque` | `PhMosque` | mosque | map |
| 926 | `motorcycle` | `PhMotorcycle` | motorcycle | map, objects |
| 927 | `mountains` | `PhMountains` | mountains | nature, map |
| 928 | `mouse` | `PhMouse` | mouse | system |
| 929 | `mouse-left-click` | `PhMouseLeftClick` | mouse-left-click | system |
| 930 | `mouse-middle-click` | `PhMouseMiddleClick` | mouse-middle-click | system |
| 931 | `mouse-right-click` | `PhMouseRightClick` | mouse-right-click | system |
| 932 | `mouse-scroll` | `PhMouseScroll` | mouse-scroll | system |
| 933 | `mouse-simple` | `PhMouseSimple` | mouse简易 | system |
| 934 | `music-note` | `PhMusicNote` | 音符 | media |
| 935 | `music-note-simple` | `PhMusicNoteSimple` | music-note简易 | media |
| 936 | `music-notes` | `PhMusicNotes` | music-notes | media |
| 937 | `music-notes-minus` | `PhMusicNotesMinus` | music-notes-minus | media |
| 938 | `music-notes-plus` | `PhMusicNotesPlus` | music-notes-plus | media |
| 939 | `music-notes-simple` | `PhMusicNotesSimple` | music-notes简易 | media |
| 940 | `navigation-arrow` | `PhNavigationArrow` | 导航箭头 | map |
| 941 | `needle` | `PhNeedle` | needle | objects, commerce |
| 942 | `network` | `PhNetwork` | network | system |
| 943 | `network-slash` | `PhNetworkSlash` | network-slash | system |
| 944 | `network-x` | `PhNetworkX` | network-x | system |
| 945 | `newspaper` | `PhNewspaper` | 报纸 | media, objects |
| 946 | `newspaper-clipping` | `PhNewspaperClipping` | newspaper-clipping | media, objects |
| 947 | `not-equals` | `PhNotEquals` | not-equals | finance, development |
| 948 | `not-member-of` | `PhNotMemberOf` | not-member-of | finance, development |
| 949 | `not-subset-of` | `PhNotSubsetOf` | not-subset-of | finance, development |
| 950 | `not-superset-of` | `PhNotSupersetOf` | not-superset-of | finance, development |
| 951 | `notches` | `PhNotches` | notches | system, editor |
| 952 | `note` | `PhNote` | 便签/笔记 | office, editor |
| 953 | `note-blank` | `PhNoteBlank` | note-blank | office, editor |
| 954 | `note-pencil` | `PhNotePencil` | note-pencil | office, editor |
| 955 | `notebook` | `PhNotebook` | 笔记本 | office, editor |
| 956 | `notepad` | `PhNotepad` | 记事本 | office, editor |
| 957 | `notification` | `PhNotification` | notification | system |
| 958 | `notion-logo` | `PhNotionLogo` | notion 标志 | brand |
| 959 | `nuclear-plant` | `PhNuclearPlant` | nuclear-plant | commerce, objects |
| 960 | `number-circle-eight` | `PhNumberCircleEight` | 数字 8 圆圈 | finance |
| 961 | `number-circle-five` | `PhNumberCircleFive` | 数字 5 圆圈 | finance |
| 962 | `number-circle-four` | `PhNumberCircleFour` | 数字 4 圆圈 | finance |
| 963 | `number-circle-nine` | `PhNumberCircleNine` | 数字 9 圆圈 | finance |
| 964 | `number-circle-one` | `PhNumberCircleOne` | 数字 1 圆圈 | finance |
| 965 | `number-circle-seven` | `PhNumberCircleSeven` | 数字 7 圆圈 | finance |
| 966 | `number-circle-six` | `PhNumberCircleSix` | 数字 6 圆圈 | finance |
| 967 | `number-circle-three` | `PhNumberCircleThree` | 数字 3 圆圈 | finance |
| 968 | `number-circle-two` | `PhNumberCircleTwo` | 数字 2 圆圈 | finance |
| 969 | `number-circle-zero` | `PhNumberCircleZero` | 数字 0 圆圈 | finance |
| 970 | `number-eight` | `PhNumberEight` | number-eight | finance |
| 971 | `number-five` | `PhNumberFive` | number-five | finance |
| 972 | `number-four` | `PhNumberFour` | number-four | finance |
| 973 | `number-nine` | `PhNumberNine` | number-nine | finance |
| 974 | `number-one` | `PhNumberOne` | number-one | finance |
| 975 | `number-seven` | `PhNumberSeven` | number-seven | finance |
| 976 | `number-six` | `PhNumberSix` | number-six | finance |
| 977 | `number-square-eight` | `PhNumberSquareEight` | number方形-eight | finance |
| 978 | `number-square-five` | `PhNumberSquareFive` | number方形-five | finance |
| 979 | `number-square-four` | `PhNumberSquareFour` | number方形-four | finance |
| 980 | `number-square-nine` | `PhNumberSquareNine` | number方形-nine | finance |
| 981 | `number-square-one` | `PhNumberSquareOne` | number方形-one | finance |
| 982 | `number-square-seven` | `PhNumberSquareSeven` | number方形-seven | finance |
| 983 | `number-square-six` | `PhNumberSquareSix` | number方形-six | finance |
| 984 | `number-square-three` | `PhNumberSquareThree` | number方形-three | finance |
| 985 | `number-square-two` | `PhNumberSquareTwo` | number方形-two | finance |
| 986 | `number-square-zero` | `PhNumberSquareZero` | number方形-zero | finance |
| 987 | `number-three` | `PhNumberThree` | number-three | finance |
| 988 | `number-two` | `PhNumberTwo` | number-two | finance |
| 989 | `number-zero` | `PhNumberZero` | number-zero | finance |
| 990 | `numpad` | `PhNumpad` | numpad | communication, system |
| 991 | `nut` | `PhNut` | nut | objects, system |
| 992 | `ny-times-logo` | `PhNyTimesLogo` | ny-times 标志 | brand |
| 993 | `octagon` | `PhOctagon` | octagon | design |
| 994 | `office-chair` | `PhOfficeChair` | office-chair | objects, commerce |
| 995 | `onigiri` | `PhOnigiri` | onigiri | commerce, map |
| 996 | `open-ai-logo` | `PhOpenAiLogo` | open-ai 标志 | development, brand |
| 997 | `option` | `PhOption` | option | system, editor |
| 998 | `orange` | `PhOrange` | orange | commerce, nature |
| 999 | `orange-slice` | `PhOrangeSlice` | orange-slice | map, commerce, nature |
| 1000 | `oven` | `PhOven` | oven | commerce, objects |
| 1001 | `package` | `PhPackage` | 包裹/物流 | development, objects |
| 1002 | `paint-brush` | `PhPaintBrush` | 画笔 | design, editor, objects |
| 1003 | `paint-brush-broad` | `PhPaintBrushBroad` | paint-brush-broad | design, editor, objects |
| 1004 | `paint-brush-household` | `PhPaintBrushHousehold` | paint-brush-household | design, editor, objects |
| 1005 | `paint-bucket` | `PhPaintBucket` | 油漆桶 | design, editor, objects |
| 1006 | `paint-roller` | `PhPaintRoller` | paint-roller | design, editor, objects |
| 1007 | `palette` | `PhPalette` | 调色板/主题 | design, editor, objects |
| 1008 | `panorama` | `PhPanorama` | panorama | media |
| 1009 | `pants` | `PhPants` | pants | commerce, objects |
| 1010 | `paper-plane` | `PhPaperPlane` | 纸飞机/发送 | communication, map, objects |
| 1011 | `paper-plane-right` | `PhPaperPlaneRight` | paper-plane-right | communication, map, objects |
| 1012 | `paper-plane-tilt` | `PhPaperPlaneTilt` | paper-plane-tilt | communication, map, objects |
| 1013 | `paperclip` | `PhPaperclip` | 回形针/附件 | communication, editor, office, objects |
| 1014 | `paperclip-horizontal` | `PhPaperclipHorizontal` | paperclip-horizontal | communication, editor, office, objects |
| 1015 | `parachute` | `PhParachute` | parachute | objects, development |
| 1016 | `paragraph` | `PhParagraph` | paragraph | editor |
| 1017 | `parallelogram` | `PhParallelogram` | parallelogram | brand, media, design |
| 1018 | `park` | `PhPark` | park | map, nature |
| 1019 | `password` | `PhPassword` | password | system |
| 1020 | `path` | `PhPath` | path | design, map |
| 1021 | `patreon-logo` | `PhPatreonLogo` | patreon 标志 | brand |
| 1022 | `pause` | `PhPause` | 暂停 | media, system |
| 1023 | `pause-circle` | `PhPauseCircle` | pause圆圈 | media, system |
| 1024 | `paw-print` | `PhPawPrint` | paw-print | nature, commerce, health |
| 1025 | `paypal-logo` | `PhPaypalLogo` | PayPal 标识 | brand, finance, commerce |
| 1026 | `peace` | `PhPeace` | peace | communication |
| 1027 | `pen` | `PhPen` | 钢笔 | design, editor, office |
| 1028 | `pen-nib` | `PhPenNib` | pen-nib | design, editor, office |
| 1029 | `pen-nib-straight` | `PhPenNibStraight` | pen-nib-straight | design, editor, office |
| 1030 | `pencil` | `PhPencil` | 铅笔 | design, editor, office |
| 1031 | `pencil-circle` | `PhPencilCircle` | pencil圆圈 | design, editor, office |
| 1032 | `pencil-line` | `PhPencilLine` | pencil-line | design, editor, office |
| 1033 | `pencil-ruler` | `PhPencilRuler` | pencil-ruler | design, editor, office |
| 1034 | `pencil-simple` | `PhPencilSimple` | pencil简易 | design, editor, office |
| 1035 | `pencil-simple-line` | `PhPencilSimpleLine` | pencil简易-line | design, editor, office |
| 1036 | `pencil-simple-slash` | `PhPencilSimpleSlash` | pencil简易-slash | design, editor, office |
| 1037 | `pencil-slash` | `PhPencilSlash` | pencil-slash | design, editor, office |
| 1038 | `pentagon` | `PhPentagon` | pentagon | design |
| 1039 | `pentagram` | `PhPentagram` | pentagram | games, design |
| 1040 | `pepper` | `PhPepper` | pepper | commerce, nature |
| 1041 | `percent` | `PhPercent` | percent | development, finance |
| 1042 | `person` | `PhPerson` | person | map, people |
| 1043 | `person-arms-spread` | `PhPersonArmsSpread` | person-arms-spread | health, map, people |
| 1044 | `person-simple` | `PhPersonSimple` | person简易 | map, people, health |
| 1045 | `person-simple-bike` | `PhPersonSimpleBike` | person简易-bike | map, people, health |
| 1046 | `person-simple-circle` | `PhPersonSimpleCircle` | person简易圆圈 | people |
| 1047 | `person-simple-hike` | `PhPersonSimpleHike` | person简易-hike | nature, health, map, people |
| 1048 | `person-simple-run` | `PhPersonSimpleRun` | person简易-run | map, people, health |
| 1049 | `person-simple-ski` | `PhPersonSimpleSki` | person简易-ski | games, health |
| 1050 | `person-simple-snowboard` | `PhPersonSimpleSnowboard` | person简易-snowboard | games, health |
| 1051 | `person-simple-swim` | `PhPersonSimpleSwim` | person简易-swim | map, people, health |
| 1052 | `person-simple-tai-chi` | `PhPersonSimpleTaiChi` | person简易-tai-chi | health, map, people |
| 1053 | `person-simple-throw` | `PhPersonSimpleThrow` | person简易-throw | map, people, health |
| 1054 | `person-simple-walk` | `PhPersonSimpleWalk` | person简易-walk | map, people, health |
| 1055 | `perspective` | `PhPerspective` | perspective | design, editor |
| 1056 | `phone` | `PhPhone` | 电话 | communication, system |
| 1057 | `phone-call` | `PhPhoneCall` | 通话中 | communication, system |
| 1058 | `phone-disconnect` | `PhPhoneDisconnect` | phone-disconnect | communication, system |
| 1059 | `phone-incoming` | `PhPhoneIncoming` | 呼入电话 | communication, system |
| 1060 | `phone-list` | `PhPhoneList` | phone-list | communication, system |
| 1061 | `phone-outgoing` | `PhPhoneOutgoing` | 呼出电话 | communication, system |
| 1062 | `phone-pause` | `PhPhonePause` | phone-pause | communication, system |
| 1063 | `phone-plus` | `PhPhonePlus` | phone-plus | communication, system |
| 1064 | `phone-slash` | `PhPhoneSlash` | 挂断电话 | communication, system |
| 1065 | `phone-transfer` | `PhPhoneTransfer` | phone-transfer | communication, system |
| 1066 | `phone-x` | `PhPhoneX` | phone-x | communication, system |
| 1067 | `phosphor-logo` | `PhPhosphorLogo` | Phosphor 官方标识 | brand |
| 1068 | `pi` | `PhPi` | pi | finance, development |
| 1069 | `piano-keys` | `PhPianoKeys` | 钢琴琴键 | media, objects |
| 1070 | `picnic-table` | `PhPicnicTable` | picnic-table | map, nature |
| 1071 | `picture-in-picture` | `PhPictureInPicture` | 画中画 | media, system |
| 1072 | `piggy-bank` | `PhPiggyBank` | 储蓄罐 | finance, objects |
| 1073 | `pill` | `PhPill` | 药丸 | health |
| 1074 | `ping-pong` | `PhPingPong` | ping-pong | games, health, objects |
| 1075 | `pint-glass` | `PhPintGlass` | pint-glass | commerce, health, objects |
| 1076 | `pinterest-logo` | `PhPinterestLogo` | Pinterest 标志 | brand, communication |
| 1077 | `pinwheel` | `PhPinwheel` | 风车 | games, objects |
| 1078 | `pipe` | `PhPipe` | pipe | commerce, objects |
| 1079 | `pipe-wrench` | `PhPipeWrench` | pipe-wrench | commerce, objects |
| 1080 | `pix-logo` | `PhPixLogo` | pix 标志 | commerce, finance |
| 1081 | `pizza` | `PhPizza` | 披萨 | commerce, map |
| 1082 | `placeholder` | `PhPlaceholder` | placeholder | design, editor |
| 1083 | `planet` | `PhPlanet` | 行星/星球 | nature |
| 1084 | `plant` | `PhPlant` | plant | commerce, nature |
| 1085 | `play` | `PhPlay` | 播放 | media, system |
| 1086 | `play-circle` | `PhPlayCircle` | play圆圈 | media, system |
| 1087 | `play-pause` | `PhPlayPause` | play-pause | media, system |
| 1088 | `playlist` | `PhPlaylist` | 播放列表 | media, system |
| 1089 | `plug` | `PhPlug` | 电源插头 | system, objects |
| 1090 | `plug-charging` | `PhPlugCharging` | plug-charging | system, objects |
| 1091 | `plugs` | `PhPlugs` | plugs | system, objects |
| 1092 | `plugs-connected` | `PhPlugsConnected` | plugs-connected | system, objects |
| 1093 | `plus` | `PhPlus` | 加号 (+) | development, finance, system |
| 1094 | `plus-circle` | `PhPlusCircle` | plus圆圈 | development, finance, system |
| 1095 | `plus-minus` | `PhPlusMinus` | plus-minus | development, finance |
| 1096 | `plus-square` | `PhPlusSquare` | plus方形 | finance, development, system |
| 1097 | `poker-chip` | `PhPokerChip` | poker-chip | games |
| 1098 | `police-car` | `PhPoliceCar` | police-car | map, objects |
| 1099 | `polygon` | `PhPolygon` | polygon | design |
| 1100 | `popcorn` | `PhPopcorn` | popcorn | map, commerce |
| 1101 | `popsicle` | `PhPopsicle` | popsicle | commerce, map |
| 1102 | `potted-plant` | `PhPottedPlant` | potted-plant | commerce, nature |
| 1103 | `power` | `PhPower` | 电源开关 | system |
| 1104 | `prescription` | `PhPrescription` | prescription | health |
| 1105 | `presentation` | `PhPresentation` | presentation | finance, office |
| 1106 | `presentation-chart` | `PhPresentationChart` | presentation-chart | finance, office |
| 1107 | `printer` | `PhPrinter` | 打印机 | editor, office |
| 1108 | `prohibit` | `PhProhibit` | prohibit | map, system |
| 1109 | `prohibit-inset` | `PhProhibitInset` | prohibit-inset | map, system |
| 1110 | `projector-screen` | `PhProjectorScreen` | projector-screen | finance, media, office |
| 1111 | `projector-screen-chart` | `PhProjectorScreenChart` | projector-screen-chart | finance, office |
| 1112 | `pulse` | `PhPulse` | pulse | health |
| 1113 | `push-pin` | `PhPushPin` | 图钉 | office, map, objects |
| 1114 | `push-pin-simple` | `PhPushPinSimple` | push-pin简易 | office, map, objects |
| 1115 | `push-pin-simple-slash` | `PhPushPinSimpleSlash` | push-pin简易-slash | office, map, objects |
| 1116 | `push-pin-slash` | `PhPushPinSlash` | push-pin-slash | office, map, objects |
| 1117 | `puzzle-piece` | `PhPuzzlePiece` | puzzle-piece | games, development |
| 1118 | `qr-code` | `PhQrCode` | 二维码 | system |
| 1119 | `question` | `PhQuestion` | 问号 (?) | system |
| 1120 | `question-mark` | `PhQuestionMark` | question-mark | system |
| 1121 | `queue` | `PhQueue` | queue | media, system |
| 1122 | `quotes` | `PhQuotes` | 双引号 | communication, editor, media |
| 1123 | `rabbit` | `PhRabbit` | rabbit | nature |
| 1124 | `racquet` | `PhRacquet` | racquet | games, health, objects |
| 1125 | `radical` | `PhRadical` | radical | development, finance |
| 1126 | `radio` | `PhRadio` | 收音机 | communication, media, objects |
| 1127 | `radio-button` | `PhRadioButton` | radio-button | system |
| 1128 | `radioactive` | `PhRadioactive` | radioactive | nature, health |
| 1129 | `rainbow` | `PhRainbow` | 彩虹 | weather |
| 1130 | `rainbow-cloud` | `PhRainbowCloud` | rainbow-cloud | weather |
| 1131 | `ranking` | `PhRanking` | ranking | games, objects |
| 1132 | `read-cv-logo` | `PhReadCvLogo` | read-cv 标志 | brand |
| 1133 | `receipt` | `PhReceipt` | 收据/小票 | commerce, finance |
| 1134 | `receipt-x` | `PhReceiptX` | receipt-x | commerce, finance |
| 1135 | `record` | `PhRecord` | 录音/录制 | media, system |
| 1136 | `rectangle` | `PhRectangle` | 矩形 | design |
| 1137 | `rectangle-dashed` | `PhRectangleDashed` | rectangle-dashed | design |
| 1138 | `recycle` | `PhRecycle` | 循环回收 | arrows, nature |
| 1139 | `reddit-logo` | `PhRedditLogo` | reddit 标志 | brand, communication |
| 1140 | `repeat` | `PhRepeat` | 重复循环 | media, system |
| 1141 | `repeat-once` | `PhRepeatOnce` | repeat-once | media, system |
| 1142 | `replit-logo` | `PhReplitLogo` | replit 标志 | brand, development |
| 1143 | `resize` | `PhResize` | resize | design, editor |
| 1144 | `rewind` | `PhRewind` | rewind | media, system |
| 1145 | `rewind-circle` | `PhRewindCircle` | rewind圆圈 | media, system |
| 1146 | `road-horizon` | `PhRoadHorizon` | road-horizon | map |
| 1147 | `robot` | `PhRobot` | robot | development, objects |
| 1148 | `rocket` | `PhRocket` | 火箭/发射 | development, map, objects |
| 1149 | `rocket-launch` | `PhRocketLaunch` | rocket-launch | development, map, objects |
| 1150 | `rows` | `PhRows` | rows | design |
| 1151 | `rows-plus-bottom` | `PhRowsPlusBottom` | rows-plus-bottom | design |
| 1152 | `rows-plus-top` | `PhRowsPlusTop` | rows-plus-top | design |
| 1153 | `rss` | `PhRss` | rss | communication |
| 1154 | `rss-simple` | `PhRssSimple` | rss简易 | communication |
| 1155 | `rug` | `PhRug` | rug | objects |
| 1156 | `ruler` | `PhRuler` | 直尺 | design, editor, objects |
| 1157 | `sailboat` | `PhSailboat` | sailboat | map, objects |
| 1158 | `scales` | `PhScales` | scales | commerce, map, objects |
| 1159 | `scan` | `PhScan` | 扫描 | system |
| 1160 | `scan-smiley` | `PhScanSmiley` | scan-smiley | system, people |
| 1161 | `scissors` | `PhScissors` | 剪刀 | design, editor, office, system |
| 1162 | `scooter` | `PhScooter` | 滑板车 | map, health |
| 1163 | `screencast` | `PhScreencast` | 投屏 | media, system |
| 1164 | `screwdriver` | `PhScrewdriver` | screwdriver | commerce, objects |
| 1165 | `scribble` | `PhScribble` | scribble | design |
| 1166 | `scribble-loop` | `PhScribbleLoop` | 涂鸦圈 | design |
| 1167 | `scroll` | `PhScroll` | scroll | games, objects |
| 1168 | `seal` | `PhSeal` | seal | design |
| 1169 | `seal-check` | `PhSealCheck` | seal-check | design |
| 1170 | `seal-percent` | `PhSealPercent` | seal-percent | design |
| 1171 | `seal-question` | `PhSealQuestion` | seal-question | design |
| 1172 | `seal-warning` | `PhSealWarning` | seal-warning | design |
| 1173 | `seat` | `PhSeat` | seat | map, objects |
| 1174 | `seatbelt` | `PhSeatbelt` | seatbelt | commerce, objects |
| 1175 | `security-camera` | `PhSecurityCamera` | security-camera | objects, system |
| 1176 | `selection` | `PhSelection` | selection | design, editor |
| 1177 | `selection-all` | `PhSelectionAll` | selection-all | design, editor |
| 1178 | `selection-background` | `PhSelectionBackground` | selection-background | design, editor |
| 1179 | `selection-foreground` | `PhSelectionForeground` | selection-foreground | design, editor |
| 1180 | `selection-inverse` | `PhSelectionInverse` | selection-inverse | design, editor |
| 1181 | `selection-plus` | `PhSelectionPlus` | selection-plus | design, editor |
| 1182 | `selection-slash` | `PhSelectionSlash` | selection-slash | design, editor |
| 1183 | `shapes` | `PhShapes` | shapes | design |
| 1184 | `share` | `PhShare` | 分享 | communication, system |
| 1185 | `share-fat` | `PhShareFat` | share-fat | arrows, system, communication |
| 1186 | `share-network` | `PhShareNetwork` | share-network | communication, system |
| 1187 | `shield` | `PhShield` | 盾牌/安全 | system, objects |
| 1188 | `shield-check` | `PhShieldCheck` | 安全验证通过 | system, objects |
| 1189 | `shield-checkered` | `PhShieldCheckered` | shield-checkered | system, objects |
| 1190 | `shield-chevron` | `PhShieldChevron` | shield-chevron | system, objects |
| 1191 | `shield-plus` | `PhShieldPlus` | shield-plus | system, objects |
| 1192 | `shield-slash` | `PhShieldSlash` | shield-slash | system, objects |
| 1193 | `shield-star` | `PhShieldStar` | shield-star | objects, system |
| 1194 | `shield-warning` | `PhShieldWarning` | 安全警告 | system, objects |
| 1195 | `shipping-container` | `PhShippingContainer` | shipping-container | map, objects, commerce |
| 1196 | `shirt-folded` | `PhShirtFolded` | shirt-folded | commerce, objects |
| 1197 | `shooting-star` | `PhShootingStar` | shooting-star | nature |
| 1198 | `shopping-bag` | `PhShoppingBag` | 购物袋 | commerce, map, objects |
| 1199 | `shopping-bag-open` | `PhShoppingBagOpen` | shopping-bag-open | commerce, map, objects |
| 1200 | `shopping-cart` | `PhShoppingCart` | 购物车 | commerce, map, objects |
| 1201 | `shopping-cart-simple` | `PhShoppingCartSimple` | shopping-cart简易 | commerce, map, objects |
| 1202 | `shovel` | `PhShovel` | shovel | commerce, objects |
| 1203 | `shower` | `PhShower` | shower | objects |
| 1204 | `shrimp` | `PhShrimp` | shrimp | commerce, nature |
| 1205 | `shuffle` | `PhShuffle` | shuffle | media, arrows, system |
| 1206 | `shuffle-angular` | `PhShuffleAngular` | shuffle-angular | media, arrows, system |
| 1207 | `shuffle-simple` | `PhShuffleSimple` | shuffle简易 | media, arrows, system |
| 1208 | `sidebar` | `PhSidebar` | sidebar | design, editor |
| 1209 | `sidebar-simple` | `PhSidebarSimple` | sidebar简易 | design, editor |
| 1210 | `sigma` | `PhSigma` | sigma | finance, development |
| 1211 | `sign-in` | `PhSignIn` | sign-in | system |
| 1212 | `sign-out` | `PhSignOut` | sign-out | system |
| 1213 | `signature` | `PhSignature` | signature | communication, office |
| 1214 | `signpost` | `PhSignpost` | 路标指示牌 | map |
| 1215 | `sim-card` | `PhSimCard` | SIM 卡 | communication, system |
| 1216 | `siren` | `PhSiren` | siren | objects, map |
| 1217 | `sketch-logo` | `PhSketchLogo` | Sketch 标志 | design |
| 1218 | `skip-back` | `PhSkipBack` | 上一曲/后退 | media, system |
| 1219 | `skip-back-circle` | `PhSkipBackCircle` | skip-back圆圈 | media, system |
| 1220 | `skip-forward` | `PhSkipForward` | 下一曲/前进 | media, system |
| 1221 | `skip-forward-circle` | `PhSkipForwardCircle` | skip-forward圆圈 | media, system |
| 1222 | `skull` | `PhSkull` | skull | games |
| 1223 | `skype-logo` | `PhSkypeLogo` | skype 标志 | brand, communication |
| 1224 | `slack-logo` | `PhSlackLogo` | Slack 标志 | brand, communication |
| 1225 | `sliders` | `PhSliders` | 调节滑块 | media, system |
| 1226 | `sliders-horizontal` | `PhSlidersHorizontal` | sliders-horizontal | media, system |
| 1227 | `slideshow` | `PhSlideshow` | slideshow | media, system |
| 1228 | `smiley` | `PhSmiley` | 笑脸/表情 | communication, people |
| 1229 | `smiley-angry` | `PhSmileyAngry` | smiley-angry | communication, people |
| 1230 | `smiley-blank` | `PhSmileyBlank` | smiley-blank | communication, people |
| 1231 | `smiley-meh` | `PhSmileyMeh` | smiley-meh | communication, people |
| 1232 | `smiley-melting` | `PhSmileyMelting` | smiley-melting | communication, people |
| 1233 | `smiley-nervous` | `PhSmileyNervous` | smiley-nervous | communication, people |
| 1234 | `smiley-sad` | `PhSmileySad` | smiley-sad | communication, people |
| 1235 | `smiley-sticker` | `PhSmileySticker` | smiley-sticker | communication, people |
| 1236 | `smiley-wink` | `PhSmileyWink` | smiley-wink | communication, people |
| 1237 | `smiley-x-eyes` | `PhSmileyXEyes` | smiley-x-eyes | communication, people |
| 1238 | `snapchat-logo` | `PhSnapchatLogo` | Snapchat 标志 | brand, communication |
| 1239 | `sneaker` | `PhSneaker` | sneaker | commerce, objects, health |
| 1240 | `sneaker-move` | `PhSneakerMove` | sneaker-move | commerce, objects, health |
| 1241 | `snowflake` | `PhSnowflake` | 雪花 | weather |
| 1242 | `soccer-ball` | `PhSoccerBall` | 足球 | games, health, objects |
| 1243 | `sock` | `PhSock` | sock | commerce, objects |
| 1244 | `solar-panel` | `PhSolarPanel` | solar-panel | commerce, objects |
| 1245 | `solar-roof` | `PhSolarRoof` | solar-roof | commerce, objects |
| 1246 | `sort-ascending` | `PhSortAscending` | 升序排列 | editor |
| 1247 | `sort-descending` | `PhSortDescending` | 降序排列 | editor |
| 1248 | `soundcloud-logo` | `PhSoundcloudLogo` | soundcloud 标志 | brand, media |
| 1249 | `spade` | `PhSpade` | spade | games |
| 1250 | `sparkle` | `PhSparkle` | 闪烁火花 | communication, nature |
| 1251 | `speaker-hifi` | `PhSpeakerHifi` | speaker-hifi | media, objects |
| 1252 | `speaker-high` | `PhSpeakerHigh` | 高音量扬声器 | media, system |
| 1253 | `speaker-low` | `PhSpeakerLow` | 低音量扬声器 | media, system |
| 1254 | `speaker-none` | `PhSpeakerNone` | 静音扬声器 | media, system |
| 1255 | `speaker-simple-high` | `PhSpeakerSimpleHigh` | speaker简易-high | media, system |
| 1256 | `speaker-simple-low` | `PhSpeakerSimpleLow` | speaker简易-low | media, system |
| 1257 | `speaker-simple-none` | `PhSpeakerSimpleNone` | speaker简易-none | media, system |
| 1258 | `speaker-simple-slash` | `PhSpeakerSimpleSlash` | speaker简易-slash | media, system |
| 1259 | `speaker-simple-x` | `PhSpeakerSimpleX` | speaker简易-x | media, system |
| 1260 | `speaker-slash` | `PhSpeakerSlash` | speaker-slash | media, system |
| 1261 | `speaker-x` | `PhSpeakerX` | speaker-x | media, system |
| 1262 | `speedometer` | `PhSpeedometer` | speedometer | development, objects, system |
| 1263 | `sphere` | `PhSphere` | sphere | design |
| 1264 | `spinner` | `PhSpinner` | spinner | system |
| 1265 | `spinner-ball` | `PhSpinnerBall` | spinner-ball | system |
| 1266 | `spinner-gap` | `PhSpinnerGap` | spinner-gap | system |
| 1267 | `spiral` | `PhSpiral` | spiral | communication, design |
| 1268 | `split-horizontal` | `PhSplitHorizontal` | split-horizontal | arrows, design, editor |
| 1269 | `split-vertical` | `PhSplitVertical` | split-vertical | arrows, design, editor |
| 1270 | `spotify-logo` | `PhSpotifyLogo` | Spotify 标志 | brand, media |
| 1271 | `spray-bottle` | `PhSprayBottle` | spray-bottle | objects, health |
| 1272 | `square` | `PhSquare` | 正方形 | design |
| 1273 | `square-half` | `PhSquareHalf` | square-half | design |
| 1274 | `square-half-bottom` | `PhSquareHalfBottom` | square-half-bottom | design |
| 1275 | `square-logo` | `PhSquareLogo` | square 标志 | brand, commerce, finance |
| 1276 | `square-split-horizontal` | `PhSquareSplitHorizontal` | square-split-horizontal | design, editor |
| 1277 | `square-split-vertical` | `PhSquareSplitVertical` | square-split-vertical | design, editor |
| 1278 | `squares-four` | `PhSquaresFour` | squares-four | design, system |
| 1279 | `stack` | `PhStack` | 堆栈/图层堆叠 | design, office, editor |
| 1280 | `stack-minus` | `PhStackMinus` | stack-minus | design, office, editor |
| 1281 | `stack-overflow-logo` | `PhStackOverflowLogo` | stack-overflow 标志 | brand, development |
| 1282 | `stack-plus` | `PhStackPlus` | stack-plus | design, office, editor |
| 1283 | `stack-simple` | `PhStackSimple` | stack简易 | design, office, editor |
| 1284 | `stairs` | `PhStairs` | stairs | commerce, objects |
| 1285 | `stamp` | `PhStamp` | stamp | design, objects |
| 1286 | `standard-definition` | `PhStandardDefinition` | standard-definition | media |
| 1287 | `star` | `PhStar` | 星星/收藏 | communication, map, nature |
| 1288 | `star-and-crescent` | `PhStarAndCrescent` | star-and-crescent | communication, people |
| 1289 | `star-four` | `PhStarFour` | star-four | communication, nature |
| 1290 | `star-half` | `PhStarHalf` | star-half | communication |
| 1291 | `star-of-david` | `PhStarOfDavid` | star-of-david | communication, people |
| 1292 | `steam-logo` | `PhSteamLogo` | steam 标志 | brand, games |
| 1293 | `steering-wheel` | `PhSteeringWheel` | steering-wheel | map, objects |
| 1294 | `steps` | `PhSteps` | steps | commerce, objects |
| 1295 | `stethoscope` | `PhStethoscope` | stethoscope | health, objects |
| 1296 | `sticker` | `PhSticker` | sticker | communication |
| 1297 | `stool` | `PhStool` | stool | objects, commerce |
| 1298 | `stop` | `PhStop` | 停止/结束 | media, system |
| 1299 | `stop-circle` | `PhStopCircle` | stop圆圈 | media, system |
| 1300 | `storefront` | `PhStorefront` | storefront | commerce, map |
| 1301 | `strategy` | `PhStrategy` | strategy | games, finance |
| 1302 | `stripe-logo` | `PhStripeLogo` | stripe 标志 | brand, commerce, finance |
| 1303 | `student` | `PhStudent` | 学生 | people |
| 1304 | `subset-of` | `PhSubsetOf` | subset-of | finance, development |
| 1305 | `subset-proper-of` | `PhSubsetProperOf` | subset-proper-of | finance, development |
| 1306 | `subtitles` | `PhSubtitles` | subtitles | media |
| 1307 | `subtitles-slash` | `PhSubtitlesSlash` | subtitles-slash | media |
| 1308 | `subtract` | `PhSubtract` | subtract | design, editor |
| 1309 | `subtract-square` | `PhSubtractSquare` | subtract方形 | design, editor |
| 1310 | `subway` | `PhSubway` | subway | map, objects |
| 1311 | `suitcase` | `PhSuitcase` | suitcase | office, objects |
| 1312 | `suitcase-rolling` | `PhSuitcaseRolling` | suitcase-rolling | map, objects |
| 1313 | `suitcase-simple` | `PhSuitcaseSimple` | suitcase简易 | office, objects |
| 1314 | `sun` | `PhSun` | 太阳/白天模式 | nature, system, weather |
| 1315 | `sun-dim` | `PhSunDim` | sun-dim | nature, system, weather |
| 1316 | `sun-horizon` | `PhSunHorizon` | sun-horizon | nature, weather |
| 1317 | `sunglasses` | `PhSunglasses` | 太阳镜 | health, objects |
| 1318 | `superset-of` | `PhSupersetOf` | superset-of | finance, development |
| 1319 | `superset-proper-of` | `PhSupersetProperOf` | superset-proper-of | finance, development |
| 1320 | `swap` | `PhSwap` | 交换/对调 | design, editor |
| 1321 | `swatches` | `PhSwatches` | swatches | design, editor, objects |
| 1322 | `swimming-pool` | `PhSwimmingPool` | 游泳池 | health, map, games |
| 1323 | `sword` | `PhSword` | 剑/武器 | games, objects |
| 1324 | `synagogue` | `PhSynagogue` | 犹太会堂 | map |
| 1325 | `syringe` | `PhSyringe` | 注射器 | health |
| 1326 | `t-shirt` | `PhTShirt` | T恤短袖 | objects, commerce |
| 1327 | `table` | `PhTable` | 表格 | finance, office, editor |
| 1328 | `tabs` | `PhTabs` | tabs | system |
| 1329 | `tag` | `PhTag` | 标签 | commerce, development, objects |
| 1330 | `tag-chevron` | `PhTagChevron` | tag-chevron | commerce, development, objects |
| 1331 | `tag-simple` | `PhTagSimple` | tag简易 | commerce, development, objects |
| 1332 | `target` | `PhTarget` | 靶心/目标 | map, objects |
| 1333 | `taxi` | `PhTaxi` | 出租车 | map, objects |
| 1334 | `tea-bag` | `PhTeaBag` | tea-bag | commerce, map, objects |
| 1335 | `telegram-logo` | `PhTelegramLogo` | Telegram 标志 | brand, communication |
| 1336 | `television` | `PhTelevision` | 电视机 | system, objects |
| 1337 | `television-simple` | `PhTelevisionSimple` | television简易 | system, objects |
| 1338 | `tennis-ball` | `PhTennisBall` | tennis-ball | games, health, objects |
| 1339 | `tent` | `PhTent` | tent | health, objects, nature, map |
| 1340 | `terminal` | `PhTerminal` | 命令行终端 | development, system |
| 1341 | `terminal-window` | `PhTerminalWindow` | terminal-window | development, system |
| 1342 | `test-tube` | `PhTestTube` | test-tube | development, nature, health, objects |
| 1343 | `text-a-underline` | `PhTextAUnderline` | text-a-underline | design, editor |
| 1344 | `text-aa` | `PhTextAa` | text-aa | design, editor |
| 1345 | `text-align-center` | `PhTextAlignCenter` | text-align-center | design, editor |
| 1346 | `text-align-justify` | `PhTextAlignJustify` | text-align-justify | design, editor |
| 1347 | `text-align-left` | `PhTextAlignLeft` | text-align-left | design, editor |
| 1348 | `text-align-right` | `PhTextAlignRight` | text-align-right | design, editor |
| 1349 | `text-b` | `PhTextB` | text-b | design, editor |
| 1350 | `text-columns` | `PhTextColumns` | text-columns | design, editor |
| 1351 | `text-h` | `PhTextH` | text-h | design, editor |
| 1352 | `text-h-five` | `PhTextHFive` | text-h-five | design, editor |
| 1353 | `text-h-four` | `PhTextHFour` | text-h-four | design, editor |
| 1354 | `text-h-one` | `PhTextHOne` | text-h-one | design, editor |
| 1355 | `text-h-six` | `PhTextHSix` | text-h-six | design, editor |
| 1356 | `text-h-three` | `PhTextHThree` | text-h-three | design, editor |
| 1357 | `text-h-two` | `PhTextHTwo` | text-h-two | design, editor |
| 1358 | `text-indent` | `PhTextIndent` | text-indent | design, editor |
| 1359 | `text-italic` | `PhTextItalic` | text-italic | design, editor |
| 1360 | `text-outdent` | `PhTextOutdent` | text-outdent | design, editor |
| 1361 | `text-strikethrough` | `PhTextStrikethrough` | text-strikethrough | design, editor |
| 1362 | `text-subscript` | `PhTextSubscript` | text-subscript | design, editor, finance |
| 1363 | `text-superscript` | `PhTextSuperscript` | text-superscript | design, editor, finance |
| 1364 | `text-t` | `PhTextT` | text-t | design, editor |
| 1365 | `text-t-slash` | `PhTextTSlash` | text-t-slash | design, editor |
| 1366 | `text-underline` | `PhTextUnderline` | text-underline | design, editor |
| 1367 | `textbox` | `PhTextbox` | textbox | editor, system |
| 1368 | `thermometer` | `PhThermometer` | 温度计 | weather, health, objects |
| 1369 | `thermometer-cold` | `PhThermometerCold` | thermometer-cold | weather, health, objects |
| 1370 | `thermometer-hot` | `PhThermometerHot` | thermometer-hot | weather, health, objects |
| 1371 | `thermometer-simple` | `PhThermometerSimple` | thermometer简易 | weather, health, objects |
| 1372 | `threads-logo` | `PhThreadsLogo` | threads 标志 | brand, communication |
| 1373 | `three-d` | `PhThreeD` | three-d | media, development |
| 1374 | `thumbs-down` | `PhThumbsDown` | 踩/不赞成 | communication, people |
| 1375 | `thumbs-up` | `PhThumbsUp` | 赞/点赞 | communication, people |
| 1376 | `ticket` | `PhTicket` | 门票/车票 | commerce, map, objects |
| 1377 | `tidal-logo` | `PhTidalLogo` | tidal 标志 | brand, media |
| 1378 | `tiktok-logo` | `PhTiktokLogo` | TikTok 标志 | brand, communication |
| 1379 | `tilde` | `PhTilde` | tilde | finance, development |
| 1380 | `timer` | `PhTimer` | 定时器 | system, objects |
| 1381 | `tip-jar` | `PhTipJar` | tip-jar | commerce, finance, objects |
| 1382 | `tipi` | `PhTipi` | tipi | nature, objects, map |
| 1383 | `tire` | `PhTire` | tire | commerce, objects |
| 1384 | `toggle-left` | `PhToggleLeft` | 开关向左 (关闭) | system |
| 1385 | `toggle-right` | `PhToggleRight` | 开关向右 (开启) | system |
| 1386 | `toilet` | `PhToilet` | 马桶 | health, objects |
| 1387 | `toilet-paper` | `PhToiletPaper` | toilet-paper | health, objects |
| 1388 | `toolbox` | `PhToolbox` | toolbox | objects, system, commerce |
| 1389 | `tooth` | `PhTooth` | tooth | health |
| 1390 | `tornado` | `PhTornado` | tornado | weather |
| 1391 | `tote` | `PhTote` | 托特包 | commerce, objects |
| 1392 | `tote-simple` | `PhToteSimple` | tote简易 | commerce, objects |
| 1393 | `towel` | `PhTowel` | towel | commerce, objects |
| 1394 | `tractor` | `PhTractor` | tractor | commerce, objects |
| 1395 | `trademark` | `PhTrademark` | trademark | commerce |
| 1396 | `trademark-registered` | `PhTrademarkRegistered` | trademark-registered | commerce |
| 1397 | `traffic-cone` | `PhTrafficCone` | traffic-cone | map |
| 1398 | `traffic-sign` | `PhTrafficSign` | traffic-sign | map |
| 1399 | `traffic-signal` | `PhTrafficSignal` | traffic-signal | map |
| 1400 | `train` | `PhTrain` | train | map, objects |
| 1401 | `train-regional` | `PhTrainRegional` | train-regional | map, objects |
| 1402 | `train-simple` | `PhTrainSimple` | train简易 | map, objects |
| 1403 | `tram` | `PhTram` | tram | map, objects |
| 1404 | `translate` | `PhTranslate` | translate | communication, system |
| 1405 | `trash` | `PhTrash` | 垃圾桶/删除 | office, system |
| 1406 | `trash-simple` | `PhTrashSimple` | trash简易 | office, system |
| 1407 | `tray` | `PhTray` | tray | office, communication, system |
| 1408 | `tray-arrow-down` | `PhTrayArrowDown` | tray-箭头 down | office, system |
| 1409 | `tray-arrow-up` | `PhTrayArrowUp` | tray-箭头 up | office, system |
| 1410 | `treasure-chest` | `PhTreasureChest` | treasure-chest | games, objects |
| 1411 | `tree` | `PhTree` | 大树 | nature |
| 1412 | `tree-evergreen` | `PhTreeEvergreen` | tree-evergreen | nature |
| 1413 | `tree-palm` | `PhTreePalm` | tree-palm | nature |
| 1414 | `tree-structure` | `PhTreeStructure` | tree-structure | development, office |
| 1415 | `tree-view` | `PhTreeView` | tree-view | system |
| 1416 | `trend-down` | `PhTrendDown` | 趋势下滑 | finance, office |
| 1417 | `trend-up` | `PhTrendUp` | 趋势上升 | finance, office |
| 1418 | `triangle` | `PhTriangle` | triangle | design |
| 1419 | `triangle-dashed` | `PhTriangleDashed` | triangle-dashed | design |
| 1420 | `trolley` | `PhTrolley` | trolley | office, objects |
| 1421 | `trolley-suitcase` | `PhTrolleySuitcase` | trolley-suitcase | office, objects |
| 1422 | `trophy` | `PhTrophy` | 奖杯 | games, objects |
| 1423 | `truck` | `PhTruck` | 卡车 | commerce, map, objects |
| 1424 | `truck-trailer` | `PhTruckTrailer` | truck-trailer | commerce, map, objects |
| 1425 | `tumblr-logo` | `PhTumblrLogo` | tumblr 标志 | brand, communication |
| 1426 | `twitch-logo` | `PhTwitchLogo` | Twitch 标志 | brand, communication, games |
| 1427 | `twitter-logo` | `PhTwitterLogo` | Twitter 标志 | brand, communication |
| 1428 | `umbrella` | `PhUmbrella` | 雨伞 | objects, weather |
| 1429 | `umbrella-simple` | `PhUmbrellaSimple` | umbrella简易 | objects, weather |
| 1430 | `union` | `PhUnion` | union | finance, development |
| 1431 | `unite` | `PhUnite` | unite | design, editor |
| 1432 | `unite-square` | `PhUniteSquare` | unite方形 | design, editor |
| 1433 | `upload` | `PhUpload` | 上传 | system |
| 1434 | `upload-simple` | `PhUploadSimple` | upload简易 | system |
| 1435 | `usb` | `PhUsb` | usb | objects, system |
| 1436 | `user` | `PhUser` | 用户 | people |
| 1437 | `user-check` | `PhUserCheck` | 用户已验证 | people |
| 1438 | `user-circle` | `PhUserCircle` | user圆圈 | people |
| 1439 | `user-circle-check` | `PhUserCircleCheck` | user圆圈-check | people |
| 1440 | `user-circle-dashed` | `PhUserCircleDashed` | user圆圈-dashed | people |
| 1441 | `user-circle-gear` | `PhUserCircleGear` | user圆圈-gear | people |
| 1442 | `user-circle-minus` | `PhUserCircleMinus` | user圆圈-minus | people |
| 1443 | `user-circle-plus` | `PhUserCirclePlus` | user圆圈-plus | people |
| 1444 | `user-focus` | `PhUserFocus` | user-focus | people |
| 1445 | `user-gear` | `PhUserGear` | user-gear | people |
| 1446 | `user-list` | `PhUserList` | user-list | people |
| 1447 | `user-minus` | `PhUserMinus` | 删除用户 | people |
| 1448 | `user-plus` | `PhUserPlus` | 添加用户 | people |
| 1449 | `user-rectangle` | `PhUserRectangle` | user-rectangle | people |
| 1450 | `user-sound` | `PhUserSound` | user-sound | people |
| 1451 | `user-square` | `PhUserSquare` | user方形 | people |
| 1452 | `user-switch` | `PhUserSwitch` | user-switch | people |
| 1453 | `users` | `PhUsers` | 用户群体/多用户 | people |
| 1454 | `users-four` | `PhUsersFour` | users-four | people |
| 1455 | `users-three` | `PhUsersThree` | users-three | people |
| 1456 | `van` | `PhVan` | van | map, objects |
| 1457 | `vault` | `PhVault` | vault | objects, system, finance |
| 1458 | `vector-three` | `PhVectorThree` | vector-three | arrows, development, design |
| 1459 | `vector-two` | `PhVectorTwo` | vector-two | arrows, development, design |
| 1460 | `vibrate` | `PhVibrate` | vibrate | system |
| 1461 | `video` | `PhVideo` | 摄像机/视频 | people |
| 1462 | `video-camera` | `PhVideoCamera` | video-camera | media, system, objects |
| 1463 | `video-camera-slash` | `PhVideoCameraSlash` | video-camera-slash | media, system |
| 1464 | `video-conference` | `PhVideoConference` | video-conference | media, system, communication |
| 1465 | `vignette` | `PhVignette` | vignette | design |
| 1466 | `vinyl-record` | `PhVinylRecord` | vinyl-record | media, office |
| 1467 | `virtual-reality` | `PhVirtualReality` | virtual-reality | games, media |
| 1468 | `virus` | `PhVirus` | virus | health |
| 1469 | `visor` | `PhVisor` | visor | development, media, objects |
| 1470 | `voicemail` | `PhVoicemail` | 语音信箱 | system |
| 1471 | `volleyball` | `PhVolleyball` | 排球 | games, health, objects |
| 1472 | `wall` | `PhWall` | wall | objects, system |
| 1473 | `wallet` | `PhWallet` | 钱包 | commerce, finance, objects |
| 1474 | `warehouse` | `PhWarehouse` | warehouse | commerce, map |
| 1475 | `warning` | `PhWarning` | 警告提示 (!) | system |
| 1476 | `warning-circle` | `PhWarningCircle` | warning圆圈 | system |
| 1477 | `warning-diamond` | `PhWarningDiamond` | warning-diamond | system |
| 1478 | `warning-octagon` | `PhWarningOctagon` | warning-octagon | system |
| 1479 | `washing-machine` | `PhWashingMachine` | washing-machine | commerce, map, objects |
| 1480 | `watch` | `PhWatch` | 手表 | system, objects |
| 1481 | `wave-sawtooth` | `PhWaveSawtooth` | wave-sawtooth | media |
| 1482 | `wave-sine` | `PhWaveSine` | wave-sine | media |
| 1483 | `wave-square` | `PhWaveSquare` | wave方形 | media |
| 1484 | `wave-triangle` | `PhWaveTriangle` | wave-triangle | media |
| 1485 | `waveform` | `PhWaveform` | waveform | media |
| 1486 | `waveform-slash` | `PhWaveformSlash` | waveform-slash | media |
| 1487 | `waves` | `PhWaves` | 水波/声波 | nature, weather |
| 1488 | `webcam` | `PhWebcam` | 网络摄像头 | objects, system, communication |
| 1489 | `webcam-slash` | `PhWebcamSlash` | webcam-slash | communication, objects, system |
| 1490 | `webhooks-logo` | `PhWebhooksLogo` | webhooks 标志 | development, brand |
| 1491 | `wechat-logo` | `PhWechatLogo` | 微信 Logo | brand |
| 1492 | `whatsapp-logo` | `PhWhatsappLogo` | WhatsApp 标志 | brand, communication |
| 1493 | `wheelchair` | `PhWheelchair` | 轮椅 | health, map, people |
| 1494 | `wheelchair-motion` | `PhWheelchairMotion` | wheelchair-motion | health, map, people |
| 1495 | `wifi-high` | `PhWifiHigh` | 强 WiFi 信号 | system |
| 1496 | `wifi-low` | `PhWifiLow` | wifi-low | system |
| 1497 | `wifi-medium` | `PhWifiMedium` | wifi-medium | system |
| 1498 | `wifi-none` | `PhWifiNone` | wifi-none | system |
| 1499 | `wifi-slash` | `PhWifiSlash` | 断开 WiFi | system |
| 1500 | `wifi-x` | `PhWifiX` | wifi-x | system |
| 1501 | `wind` | `PhWind` | 风 | weather |
| 1502 | `windmill` | `PhWindmill` | windmill | commerce |
| 1503 | `windows-logo` | `PhWindowsLogo` | Windows Logo | brand, development |
| 1504 | `wine` | `PhWine` | 葡萄酒/红酒杯 | commerce, map, objects |
| 1505 | `wrench` | `PhWrench` | 扳手/工具 | system, objects, commerce |
| 1506 | `x` | `PhX` | 关闭/清除 (X) | development, finance, system |
| 1507 | `x-circle` | `PhXCircle` | x圆圈 | system |
| 1508 | `x-logo` | `PhXLogo` | x 标志 | brand, communication |
| 1509 | `x-square` | `PhXSquare` | x方形 | system |
| 1510 | `yarn` | `PhYarn` | yarn | games, commerce |
| 1511 | `yin-yang` | `PhYinYang` | yin-yang | communication |
| 1512 | `youtube-logo` | `PhYoutubeLogo` | YouTube 标志 | brand, communication, media |


---

## 📄 License

MIT © MonkeyQt Team / Phosphor Icons
