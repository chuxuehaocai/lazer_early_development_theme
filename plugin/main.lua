-- 羊皮纸 · 田野笔记 —— parchment 设计阶段的宿主主题
--
-- 契约见 https://lazer.naominet.dev/docs （仓库内 docs/lua-plugins.md）。
--
-- 这个插件只做一件事：把 2026 parchment 阶段的排版、圆角、行高与歌词动效翻成
-- 宿主的声明式令牌，让客户端自身的界面回到那一版的几何比例。
--
-- 没有页面、没有设置项、没有播放器菜单项，也不起任何本地服务：随包的静态复刻
-- 前端（HTML/CSS/JS 那套）与它的 HTTP/WebSocket 服务已经整体移除，这里只剩
-- Lua 主题。插件不返回 Widget，也不申请网络、资料库或文件权限。

local tokens = require("lib.tokens")
local config = require("lib.config")

local function unsupported(operation)
  return { error = { code = 400, message = "unsupported operation: " .. tostring(operation) } }
end

local handlers = {}

handlers.describe = function()
  -- providers 明确为空：这个插件不接音乐平台，只换皮。
  --
  -- 注意类型：Lua 的空 table 经 JSON 编码后是 `{}`（对象），宿主以前只认
  -- 「providers 是数组」，于是把 manifest 里的 provider 名字升格成了一个音乐平台。
  -- 宿主那边也一起修了：空对象现在同样表示「没有平台」。
  return {
    providers = host.json_decode("[]"),
    theme = true,
  }
end

handlers.theme = function()
  return tokens.bundle()
end

-- 兼容旧宿主 / 调试探针
handlers.skin = function()
  return tokens.bundle()
end

handlers.session = function()
  return nil
end

return {
  call = function(operation, args)
    local handler = handlers[operation]
    if handler then
      return handler(args or {})
    end
    return unsupported(operation)
  end,
  -- 自查用：宿主或外部探针可以直接取令牌
  tokens = tokens,
}
