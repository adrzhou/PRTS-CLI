# PRTS-CLI
一款用 Python3 编写，用 [Click][1] 辅助开发的明日方舟干员数据查询工具  

```
$ prts

Usage: prts [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  alias    设置或查询干员或材料别名
  plan     查询干员升级所需材料
  sync     将本地数据与prts.wiki同步
  track    追踪干员练度与仓库材料
  unalias  删除干员或材料别名
  untrack  停止追踪干员练度
  wiki     查询干员信息
```

## 移动端预览
![preview_harmony_os](https://user-images.githubusercontent.com/101899715/190879877-3f641677-590c-441f-88b3-8857da69dfc3.jpg)
![preview_mobile](https://user-images.githubusercontent.com/101899715/190879862-011d1d59-20f1-4915-8c29-c22ba4a42b93.jpg)



## 安装

您可以通过安装发行版本或运行源代码来使用本程序

### 发行版本

目前只推出了适用于`Windows 10` 64位操作系统，`GNU/Linux`，和`Termux`的发行版本  
请前往 [Releases][2] 页面下载压缩包  

### 源代码

任何安装了 Python 3.8+ 的设备都可以运行此程序  
除此之外，您还需要安装一下外部库  

| 名称 | 安装命令 |
|---|---|
|[click][1]| `pip install click` |
|[requests][4]| `pip install requests` |
|[tomli][5] 和 [tomli_w][6]| `pip install tomli tomli_w` |
|[bs4][7]| `pip install bs4` |
|[tabulate][8]| `pip install tabulate[widechars]` |

## 使用方式

### `sync`

本程序内置了解析 prts.wiki 干员页面源代码的功能，所以实装新干员和模组时，不需要来本页面下载新版本，可以直接通过 `sync` 命令更新本地数据库

```
# 示例：将新干员玛恩纳与但书添加至本地数据库
$ prts sync 玛恩纳 但书

# 输出结果
成功更新**玛恩纳**的干员信息
成功更新**但书**的干员信息
```

如果您想批量更新特定分支的干员的模组信息，则可以搭配 `-s` 或 `--subclass` 选项  

```
# 示例：更新所有<铁卫>的模组信息
$ prts sync -s 铁卫

# 输出结果
成功更新**泡泡**的干员信息
成功更新**星熊**的干员信息
成功更新**暴雨**的干员信息
...
```

### `alias` 与 `unalias`

本程序能识别所有干员的外文名和中文名，不过您可以通过给干员设定别名来节省打字时间

```
# 示例
$ prts alias 42=Surtr 水陈=假日威龙陈

# 示例：查询已定义的干员别名
$ prts alias

# 输出结果
alias 42=SURTR
alias 水陈=假日威龙陈

# 示例：删除别名
$ prts unalias 42 水陈
```

### `wiki`

您可以通过 `prts wiki 干员名` 这一行命令搭配各种选项来查询干员的属性，技能，升级材料等数据  

```
Usage: prts wiki [OPTIONS] [OPERATOR]

  查询干员信息

Options:
  -P, --pager                分页显示查询结果
  -g, --general              查询干员基本信息
  -a, --attr                 查询干员属性
  -t, --talent               查询干员天赋
  -p, --potential            查询干员潜能
  -s, --skill INTEGER        查询干员技能
  -r, --rank INTEGER         查询特定等级的技能
  -u, --upgrade              显示技能升级/精英化所需材料
  -U, --upgrade-only         仅显示技能升级/精英化所需材料
  -e, --elite INTEGER RANGE  查询干员精英化之后的属性数据  [0<=x<=2]
  -m, --module               查询干员模组
  --help                     Show this message and exit.
```

```
# 示例：查询基本信息
$ prts wiki Bison -g

# 查询天赋和潜能
$ prts wiki Ansel -t -p

# 查询干员专精三技能至专三所需材料
$ prts wiki Mizuki -s3 -r10 -U
```

### `track` 与 `untrack`

追踪干员练度，搭配 `plan` 命令来确认升级所需材料

```
# 示例：把晨曦格雷伊和至简加入待养成列表
$ prts track 晨曦格雷伊 Minimalist

# 输出结果 (实际控制台中的表格会比这里的美观）
| 承曦格雷伊   |   目前 |   目标 |
|--------------|--------|--------|
| 精英         |      0 |      2 |
| 一技能       |      1 |      7 |
| 二技能       |      1 |      7 |


| 至简   |   目前 |   目标 |
|--------|--------|--------|
| 精英   |      0 |      2 |
| 一技能 |      1 |      7 |
| 二技能 |      1 |      7 |

# 示例：将至简练度设定为精一各技能7级，目标设定为二技能专三
$ prts track Minimalist -r7
$ prts track Minimalist -g -s2 -r10

# 输出结果
| 至简   |   目前 |   目标 |
|--------|--------|--------|
| 精英   |      2 |      2 |
| 一技能 |      7 |      7 |
| 二技能 |      7 |     10 |

# 示例：停止追踪练度
$ prts untrack 承曦格雷伊
```

### `plan`

对正在追踪练度的干员，您可以通过 `plan` 命令来查看达成练度目标所需材料

```
# 示例
$ prts plan

# 输出结果
至简     |   总需 |   库存 |   还需
 精2      |        |        |
----------+--------+--------+--------
 晶体电路 |      6 |      0 |      6
 异铁组   |     12 |      0 |     12

 至简       |   总需 |   库存 |   还需
 二技能8    |        |        |
------------+--------+--------+--------
 异铁块     |      3 |      0 |      3
 半自然溶剂 |      1 |      0 |      1
...
```

通过搭配各种选项来调整输出结果

```
Options:
  -s, --synth      用合成所需材料代替蓝色品质以上的材料
  -o, --optimal    将待升级项目按材料收集进度排序
  -u, --up         设定当期活动概率UP的材料
  --clear          重置当期活动概率UP的材料
  -i, --inventory  查询或更新仓库内材料数量
  -c, --compact    将单个干员的所有项目合并
  --help           Show this message and exit.
```

### `remind` (Termux限定)

理智回满时，Termux 会推送通知

```
# 设定理智上限 （仅需设定一次）
$ prts remind --max 133

# 示例：输入剩余理智
$ prts remind 30

# prts 将会通过 Termux 在 （133 -30）* 6 = 618 分钟之后提醒您回罗德岛报到
```
![preview_remind](https://user-images.githubusercontent.com/101899715/190879888-93694b93-1bdd-4d4c-a6a4-f4308ad24570.jpg)


## 数据来源

本程序使用的所有干员数据均来自 [prts.wiki][3]


[1]: https://click.palletsprojects.com/en/8.1.x/ "Click"
[2]: https://github.com/adrzhou/PRTS-CLI/releases/
[3]: https://prts.wiki
[4]: https://pypi.org/project/requests/
[5]: https://github.com/hukkin/tomli
[6]: https://github.com/hukkin/tomli-w
[7]: https://www.crummy.com/software/BeautifulSoup/
[8]: https://github.com/astanin/python-tabulate
