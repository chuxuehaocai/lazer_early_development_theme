# tools

校验和打包用的几个脚本，都是 `python tools\脚本名.py` 直接跑。规则常量集中在
[`plugin_rules.py`](plugin_rules.py)，几个校验脚本不会各写一份上限值。

| 脚本 | 干什么 | 失败退出码 |
| --- | --- | --- |
| [`verify.py`](verify.py) | 把下面四段一次跑完，末尾打汇总 | 任一阶段非 0 |
| [`check_manifest.py`](check_manifest.py) | `plugin/manifest.json` 逐字段校验 | 1 |
| [`check_package.py`](check_package.py) | 包结构、路径安全、体积预算、manifest 位置 | 1 |
| [`check_lua.py`](check_lua.py) | `plugin/**/*.lua` 的 AST 与静态规则 | 1 |
| [`build_zip.py`](build_zip.py) | 产出 `build/<id>-<version>.zip` 与 SHA-256 | 1 |

纯主题插件，没有静态前端、没有本地服务，所以这里也就没有图标、抓图、起服务器那些脚本了。
