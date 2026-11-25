/**
 * _shot.mjs —— 用 CDP 精确控制视口截图（Windows headless Chrome 的 --screenshot
 * 会把窗口宽度夹到最小 500，480 的截图会被裁掉 20px，所以这里改用 Emulation 覆盖视口）。
 *
 * 用法：
 *   node _shot.mjs '<json 任务数组>'
 *   任务项：{ "url": "...", "w": 1440, "h": 900, "out": "shots/x.png" }
 *
 * 同时收集：控制台 error / 未捕获异常 / 资源 404（loading failed + status>=400）。
 */
import { spawn } from 'node:child_process';
import { writeFileSync, readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9333;

const specPath = process.argv[2];
const jobs = specPath.endsWith('.json')
  ? JSON.parse(readFileSync(specPath, 'utf8').replace(/^\uFEFF/, ''))
  : (await import(pathToFileURL(specPath).href)).default;
if (!Array.isArray(jobs) || !jobs.length) {
  console.error('no jobs');
  process.exit(2);
}

const chrome = spawn(CHROME, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${process.env.TEMP}\\lz-cdp-profile`,
  'about:blank'
], { stdio: 'ignore' });

async function waitForDevtools() {
  for (let i = 0; i < 80; i += 1) {
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (res.ok) return (await res.json()).webSocketDebuggerUrl;
    } catch (err) {
      /* 还没起来 */
    }
    await sleep(150);
  }
  throw new Error('devtools not reachable');
}

class Session {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.handlers = [];
    ws.addEventListener('message', (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
        return;
      }
      this.handlers.forEach((fn) => fn(msg));
    });
  }
  send(method, params = {}) {
    const id = (this.id += 1);
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  on(fn) {
    this.handlers.push(fn);
  }
}

async function openTarget(url) {
  const res = await fetch(`http://127.0.0.1:${PORT}/json/new?${encodeURIComponent('about:blank')}`, {
    method: 'PUT'
  });
  const target = await res.json();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true });
    ws.addEventListener('error', reject, { once: true });
  });
  const session = new Session(ws);
  session.on((msg) => {
    if (msg.method === 'Runtime.exceptionThrown') {
      const d = msg.params.exceptionDetails;
      session.errors.push(
        'EXCEPTION ' + (d.text || '') + ' :: ' +
        ((d.exception && (d.exception.description || d.exception.value)) || '') +
        ' @ ' + (d.url || '') + ':' + (d.lineNumber ?? '')
      );
    }
    if (msg.method === 'Runtime.consoleAPICalled') {
      const text = msg.params.args.map((a) => a.value ?? a.description ?? '').join(' ');
      if (msg.params.type === 'error') session.errors.push('CONSOLE ' + text);
      else session.console.push(msg.params.type + ' ' + text);
    }
    if (msg.method === 'Log.entryAdded' && msg.params.entry.level === 'error') {
      session.errors.push('LOG ' + msg.params.entry.text + ' ' + (msg.params.entry.url || ''));
    }
    if (msg.method === 'Network.loadingFailed') {
      session.errors.push('LOADFAIL ' + msg.params.errorText + ' ' + (msg.params.requestId || ''));
    }
    if (msg.method === 'Network.responseReceived' && msg.params.response.status >= 400) {
      session.errors.push('HTTP ' + msg.params.response.status + ' ' + msg.params.response.url);
    }
  });
  session.errors = [];
  session.console = [];
  session.close = () => ws.close();
  return { session, target };
}

try {
  await waitForDevtools();
  const report = [];

  for (const job of jobs) {
    const { session } = await openTarget(job.url);
    await session.send('Page.enable');
    await session.send('Runtime.enable');
    await session.send('Log.enable');
    await session.send('Network.enable');
    await session.send('Network.setCacheDisabled', { cacheDisabled: true });
    await session.send('Emulation.setDeviceMetricsOverride', {
      width: job.w,
      height: job.h,
      deviceScaleFactor: 1,
      mobile: false
    });
    await session.send('Page.navigate', { url: job.url });

    let ready = false;
    let info = null;
    for (let i = 0; i < 100; i += 1) {
      await sleep(120);
      try {
        const res = await session.send('Runtime.evaluate', {
          expression:
            'JSON.stringify({ready: document.documentElement.getAttribute("data-ready"), w: innerWidth, h: innerHeight, sw: document.documentElement.scrollWidth, sh: document.documentElement.scrollHeight})',
          returnByValue: true
        });
        info = JSON.parse(res.result.value || '{}');
        if (info.ready === '1') {
          ready = true;
          break;
        }
      } catch (err) {
        /* 页面还在导航 */
      }
    }
    await sleep(500);

    let evaluated = null;
    if (job.eval) {
      try {
        const res = await session.send('Runtime.evaluate', {
          expression: job.eval,
          returnByValue: true,
          awaitPromise: true
        });
        evaluated = res.result ? res.result.value : null;
      } catch (err) {
        evaluated = 'EVAL_ERROR ' + err.message;
      }
    }

    if (job.out) {
      const shot = await session.send('Page.captureScreenshot', { format: 'png', fromSurface: true });
      writeFileSync(job.out, Buffer.from(shot.data, 'base64'));
    }

    report.push({
      url: job.url,
      out: job.out || null,
      viewport: info,
      ready,
      evaluated,
      console: session.console.slice(),
      errors: session.errors.slice()
    });
    session.close();
  }

  console.log(JSON.stringify(report, null, 1));
} finally {
  chrome.kill();
}
