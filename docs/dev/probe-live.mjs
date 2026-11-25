/**
 * probe-live.mjs —— 验证 core.js 的 WebSocket live bridge（配合 docs/dev/fake-ws.mjs）
 *   node docs/dev/fake-ws.mjs 11581
 *   node docs/dev/cdp-shot.mjs docs/dev/probe-live.mjs
 */
const BASE = 'http://127.0.0.1:8099/index.html';

const live = `
(function () {
  var s = LZ.getState();
  var root = getComputedStyle(document.documentElement);
  return JSON.stringify({
    source: LZ.transport && LZ.transport.source,
    bridgeUrl: LZ.bridge && LZ.bridge.url,
    bridgeOpen: !!(LZ.bridge && LZ.bridge.socket),
    title: s.track && s.track.title,
    artist: s.track && s.track.artist,
    positionMs: s.positionMs,
    playing: s.playing,
    volume: s.volume,
    repeat: s.repeat,
    queue: (s.queue || []).length,
    queueTotal: s.queueTotal,
    lyrics: (s.lyrics || []).length,
    theme: LZ.config.theme,
    lyricScale: LZ.config.lyricScale,
    inset: LZ.config.inset,
    follow: LZ.config.follow,
    cssLyricScale: root.getPropertyValue('--lyric-scale').trim(),
    cssInset: root.getPropertyValue('--lz-inset').trim(),
    playerbarTitle: (document.querySelector('.playerbar__title') || {}).textContent,
    playerbarArtist: (document.querySelector('.playerbar__artist') || {}).textContent,
    playerbarTime: (document.querySelector('.playerbar__time') || {}).textContent,
    nowLyricRows: document.querySelectorAll('.vn-lyric').length,
    nowFirstLyric: (document.querySelector('.vn-lyric__text') || {}).textContent,
    queueRows: document.querySelectorAll('.vq-row').length,
    queueHead: (document.querySelector('.vq-head .inline-label') || {}).textContent
  });
})()
`;

export default [
  {
    // 真实插件形态：?ws=PORT，页面停在 #/now，看歌词是否换成 live 的 52 行
    url: `${BASE}?ws=11581&still=1#/now`,
    w: 1440,
    h: 900,
    eval: live,
    out: 'E:/projects/lazer_early_development_theme/shots/live-now-1440.png'
  },
  {
    // 队列浮层 + live 30 条快照
    url: `${BASE}?ws=11581&still=1#/queue`,
    w: 1440,
    h: 900,
    eval: live,
    out: 'E:/projects/lazer_early_development_theme/shots/live-queue-1440.png'
  }
];
