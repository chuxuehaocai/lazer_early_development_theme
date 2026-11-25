/**
 * probe-480.mjs —— 横向溢出探针（配合 cdp-shot.mjs 使用）
 *   node docs/dev/cdp-shot.mjs docs/dev/probe-480.mjs
 * 输出每个视口/路由下：#content 的 client/scroll 宽度、文档 scrollWidth、
 * 以及所有超出视口右边缘的元素（含其 min-width / width / flex / overflow 计算值）。
 */
const BASE = 'http://127.0.0.1:8099/index.html';

const expression = `
(function () {
  var vw = window.innerWidth;
  var content = document.querySelector('#content') || {};
  var out = {
    vw: vw,
    docCW: document.documentElement.clientWidth,
    docSW: document.documentElement.scrollWidth,
    bodySW: document.body.scrollWidth,
    contentCW: content.clientWidth,
    contentSW: content.scrollWidth,
    inset: LZ.contentInset || null
  };
  var wide = [];
  Array.prototype.forEach.call(document.querySelectorAll('body *'), function (el) {
    var box = el.getBoundingClientRect();
    if (box.width > 0 && box.right > vw + 0.5) {
      var cs = getComputedStyle(el);
      var name = el.tagName.toLowerCase() +
        (el.className ? '.' + String(el.className).trim().split(/\\s+/).join('.') : '');
      wide.push(name + ' w=' + Math.round(box.width) + ' right=' + Math.round(box.right) +
        ' min=' + cs.minWidth + ' width=' + cs.width + ' flex=' + cs.flex +
        ' pos=' + cs.position + ' ovx=' + cs.overflowX);
    }
  });
  out.wide = wide.slice(0, 14);
  return JSON.stringify(out);
})()
`;

export default [
  { url: `${BASE}#/home`, w: 480, h: 900, eval: expression },
  { url: `${BASE}#/home`, w: 420, h: 900, eval: expression },
  { url: `${BASE}#/home`, w: 360, h: 780, eval: expression },
  { url: `${BASE}#/settings`, w: 480, h: 900, eval: expression },
  { url: `${BASE}#/now`, w: 480, h: 900, eval: expression },
  { url: `${BASE}#/login`, w: 480, h: 900, eval: expression },
  { url: `${BASE}#/queue`, w: 480, h: 900, eval: expression }
];
