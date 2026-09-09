// Reviewed supplemental definitions; supporting evidence is retained locally.
import type { DocSection } from './types';
export const SUPPLEMENT_DATA: DocSection[] = [
  {
    "id": "supplement-project",
    "title": "project · verified additions",
    "subtitle": "7z 增补 / 结构核验",
    "description": "以 ReaperDoc 为基准。以下新条目已验证出现位置与一个实际参数布局；明确标有实机核验的字段另已验证API映射。其余含义、默认值及其他版本布局未独立证实。支持资料与实验记录仅保留在本地。",
    "entries": [
      {
        "name": "GROUPOVERRIDE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：GROUPOVERRIDE 1 0 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 4",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "ENVATTACH",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：ENVATTACH 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "POOLEDENVATTACH",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：POOLEDENVATTACH 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "FEEDBACK",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：FEEDBACK 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "PROJOFFS",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：PROJOFFS 0 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "MAXPROJLEN",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：MAXPROJLEN 0 600",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "GRID",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：GRID 3455 8 1 8 1 0 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 4",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 5",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 6",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 7",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 8",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "VIDEO_CONFIG",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：VIDEO_CONFIG 0 0 256",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "ZOOM",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：ZOOM 6.44004969 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "LOOPGRAN",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：LOOPGRAN 0 4",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "LOCK",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：LOCK 64",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "ITEMMIX",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：ITEMMIX 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "TIMELOCKMODE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：TIMELOCKMODE 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "TEMPOENVLOCKMODE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：TEMPOENVLOCKMODE 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "DEFPITCHMODE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：DEFPITCHMODE 589824 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "TAKELANE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：TAKELANE 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "USE_REC_CFG",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：USE_REC_CFG 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "SAMPLERATE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：SAMPLERATE 44100 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "工程采样率，单位Hz；由第2参数控制是否强制使用。 已通过实机两值核验：PROJECT_SRATE"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "是否使用工程采样率，0/1。 已通过实机两值核验：PROJECT_SRATE_USE"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "MIDIEDITOR",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：MIDIEDITOR 4 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "float",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "GLOBAL_AUTO",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：GLOBAL_AUTO -1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "RENDER_FILE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_FILE \"\"",
        "fields": [
          {
            "label": "field 1",
            "type": "string",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "RENDER_1X",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_1X 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "RENDER_RANGE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_RANGE 1 0 0 18 1000",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "渲染范围选择模式。 已通过实机两值核验：RENDER_BOUNDSFLAG"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "自定义渲染起点，单位秒。 已通过实机两值核验：RENDER_STARTPOS"
          },
          {
            "label": "field 3",
            "type": "float",
            "description": "自定义渲染终点，单位秒。 已通过实机两值核验：RENDER_ENDPOS"
          },
          {
            "label": "field 4",
            "type": "int",
            "description": "在哪些渲染范围模式下应用尾音的位域。 已通过实机两值核验：RENDER_TAILFLAG"
          },
          {
            "label": "field 5",
            "type": "int",
            "description": "渲染尾音长度，单位毫秒；由范围与尾音选项决定是否生效。 已通过实机两值核验：RENDER_TAILMS"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "RENDER_RESAMPLE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_RESAMPLE 9 0 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 2",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          },
          {
            "label": "field 3",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      },
      {
        "name": "RENDER_ADDTOPROJ",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_ADDTOPROJ 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "渲染后处理位域：包含加回工程、跳过可能静音文件等选项；不是单一布尔值。 已通过实机两值核验：RENDER_ADDTOPROJ"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "RENDER_STEMS",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_STEMS 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "渲染源/输出选项位域；对应 API RENDER_SETTINGS。 已通过实机两值核验：RENDER_SETTINGS"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "RENDER_DITHER",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_DITHER 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "抖动与噪声整形选项位域。 已通过实机两值核验：RENDER_DITHER"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "RENDER_NORMALIZE",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_NORMALIZE 1 0.063096 1 0 0 1 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "归一化、限制、淡化与裁剪等渲染后处理的开关/模式位域。 已通过实机两值核验：RENDER_NORMALIZE"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "归一化目标，线性增益刻度；需要启用归一化。 已通过实机两值核验：RENDER_NORMALIZE_TARGET"
          },
          {
            "label": "field 3",
            "type": "float",
            "description": "限制器阈值，线性增益刻度；需要启用限制。 已通过实机两值核验：RENDER_BRICKWALL"
          },
          {
            "label": "field 4",
            "type": "float",
            "description": "渲染淡入时长，单位秒。 已通过实机两值核验：RENDER_FADEIN"
          },
          {
            "label": "field 5",
            "type": "float",
            "description": "渲染淡出时长，单位秒。 已通过实机两值核验：RENDER_FADEOUT"
          },
          {
            "label": "field 6",
            "type": "int",
            "description": "渲染淡入曲线编号；本轮未验证编号到曲线名称的映射。 已通过实机两值核验：RENDER_FADEINSHAPE"
          },
          {
            "label": "field 7",
            "type": "int",
            "description": "渲染淡出曲线编号；本轮未验证编号到曲线名称的映射。 已通过实机两值核验：RENDER_FADEOUTSHAPE"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "RENDER_TRIM",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：RENDER_TRIM 0.000001 0.000001 0 0",
        "fields": [
          {
            "label": "field 1",
            "type": "float",
            "description": "开头静音裁剪阈值，线性增益刻度；不是裁剪时长。 已通过实机两值核验：RENDER_TRIMSTART"
          },
          {
            "label": "field 2",
            "type": "float",
            "description": "末尾静音裁剪阈值，线性增益刻度；不是裁剪时长。 已通过实机两值核验：RENDER_TRIMEND"
          },
          {
            "label": "field 3",
            "type": "float",
            "description": "开头补静音的时长，单位秒。 已通过实机两值核验：RENDER_PADSTART"
          },
          {
            "label": "field 4",
            "type": "float",
            "description": "末尾补静音的时长，单位秒。 已通过实机两值核验：RENDER_PADEND"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "TCPUIFLAGS",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：TCPUIFLAGS 0",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "工程级轨道显示覆盖选项，包含置顶与隐藏状态的覆盖。 已通过实机两值核验：PROJECT_TCP_UI_FLAGS"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "TIMEBASE_EXTRAFLAGS",
        "description": "作用域：project。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：TIMEBASE_EXTRAFLAGS 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      }
    ]
  },
  {
    "id": "supplement-track",
    "title": "track · verified additions",
    "subtitle": "7z 增补 / 结构核验",
    "description": "以 ReaperDoc 为基准。以下新条目已验证出现位置与一个实际参数布局；明确标有实机核验的字段另已验证API映射。其余含义、默认值及其他版本布局未独立证实。支持资料与实验记录仅保留在本地。",
    "entries": [
      {
        "name": "WIDTH",
        "description": "作用域：track。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：WIDTH 0.5",
        "fields": [
          {
            "label": "field 1",
            "type": "float",
            "description": "轨道立体声宽度；本轮在 I_PANMODE=5 下验证。 已通过实机两值核验：D_WIDTH"
          }
        ],
        "tags": [
          "结构已验证",
          "含实机语义验证"
        ]
      },
      {
        "name": "SPACER",
        "description": "作用域：track。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：SPACER 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      }
    ]
  },
  {
    "id": "supplement-envelope",
    "title": "envelope · verified additions",
    "subtitle": "7z 增补 / 结构核验",
    "description": "以 ReaperDoc 为基准。以下新条目已验证出现位置与一个实际参数布局；明确标有实机核验的字段另已验证API映射。其余含义、默认值及其他版本布局未独立证实。支持资料与实验记录仅保留在本地。",
    "entries": [
      {
        "name": "VOLTYPE",
        "description": "作用域：envelope。本机 7.48 格式串与真实 RPP 样例交叉核验；明确标注的字段语义已实机核验，其余待证实。示例：VOLTYPE 1",
        "fields": [
          {
            "label": "field 1",
            "type": "int",
            "description": "已验证词法类型；含义、单位、枚举及默认值未独立验证。"
          }
        ],
        "tags": [
          "结构已验证",
          "语义待验证"
        ]
      }
    ]
  }
];
