-- 主题配置：宿主键值存储 + 内存缓存。
-- 所有写入都是"尽力而为"：用户没授权 storage 时插件仍然能跑，只是每次启动回到默认值。
--
-- 这个插件只剩主题，所以配置也只剩主题相关的那些键。

local M = {}

local KEY = "parchment.config"

local DEFAULTS = {
  -- 皮肤的卡片圆角，单位 px：0 = 直角，16 = 原样，32 = 加倍。
  -- 客户端「设置 → 外观 → 圆角设置」选「跟随主题设置」时读的就是这个值。
  cornerPx = 0,
  -- 旧配置的写法（0–2 的系数），只在没读过 cornerPx 时用一次。
  cornerScale = 1,
}

local cache = nil

local function clone(source)
  local out = {}
  for key, value in pairs(source) do
    out[key] = value
  end
  return out
end

local function load()
  if cache then
    return cache
  end
  cache = clone(DEFAULTS)
  local ok, stored = pcall(host.storage_get, KEY)
  if ok and type(stored) == "table" then
    -- 老版本的配置里还有前端用的键（portMode / lyricScale / …）：
    -- 只挑本插件还认的，其余当历史残留忽略。
    for key, value in pairs(DEFAULTS) do
      local saved = stored[key]
      if type(saved) == type(value) then
        cache[key] = saved
      elseif type(saved) == "number" and type(value) == "number" then
        cache[key] = saved
      end
    end
  end
  return cache
end

local function save()
  if not cache then
    return
  end
  pcall(host.storage_set, KEY, cache)
end

function M.get(key)
  local data = load()
  if key == nil then
    return clone(data)
  end
  return data[key]
end

function M.set(key, value)
  local data = load()
  data[key] = value
  save()
  return value
end

function M.reset()
  cache = clone(DEFAULTS)
  pcall(host.storage_set, KEY, nil)
  return clone(cache)
end

function M.json()
  local data = load()
  return host.json_encode({
    cornerPx = data.cornerPx,
    cornerScale = data.cornerScale,
  })
end

return M
