/**
 * fake-ws.mjs —— 本地假 WebSocket 服务，模拟插件 host.websocket_server 的广播。
 *   node docs/dev/fake-ws.mjs [port]
 * 每秒两次推一帧，报文与 /api/state 同构（含 52 行歌词 / 30 条队列快照）。
 * 目的是在没有真实客户端时验证 core.js 的 live bridge：连接、合并状态、断线退避。
 */
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';

const PORT = Number(process.argv[2] || 11581);
const GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';

const lyricLines = Array.from({ length: 52 }, (_, i) => ({
  time: i * 4000,
  text: `实时歌词第 ${i + 1} 行`,
  translation: i % 2 ? `live lyric line ${i + 1}` : ''
}));

const queueTracks = Array.from({ length: 30 }, (_, i) => ({
  id: 'live-' + (i + 1),
  title: `队列曲目 ${i + 1}`,
  artist: '假服务',
  album: 'fake-ws',
  durationMs: 180000 + i * 1000,
  hue: 10 + (i % 40)
}));

let tick = 0;

function frame(payload) {
  const body = Buffer.from(payload, 'utf8');
  const length = body.length;
  let header;
  if (length < 126) {
    header = Buffer.from([0x81, length]);
  } else if (length < 65536) {
    header = Buffer.from([0x81, 126, (length >> 8) & 0xff, length & 0xff]);
  } else {
    header = Buffer.alloc(10);
    header[0] = 0x81;
    header[1] = 127;
    header.writeUInt32BE(0, 2);
    header.writeUInt32BE(length, 6);
  }
  return Buffer.concat([header, body]);
}

function snapshot() {
  tick += 1;
  const index = 7;
  return JSON.stringify({
    source: 'fake-ws',
    track: {
      title: '假服务正在播放',
      artist: 'IMAWANOKIWA — いよわ / 初音ミク',
      album: 'fake-ws',
      coverUrl: null,
      durationMs: 253000
    },
    positionMs: 2000 + tick * 360,
    durationMs: 253000,
    playing: true,
    volume: 0.62,
    shuffle: false,
    repeat: 'all',
    queue: { tracks: queueTracks, index: index, length: 1653 },
    lyrics: { loading: false, pureMusic: false, lines: lyricLines },
    view: { theme: 'light', lyricScale: 1.1, lyricGap: 6, focusDelta: 2, inset: 28, romanize: false, follow: true }
  });
}

const server = createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('fake-ws: upgrade only\n');
});

server.on('upgrade', (req, socket) => {
  const key = req.headers['sec-websocket-key'];
  if (!key) {
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
    return;
  }
  const accept = createHash('sha1').update(key + GUID).digest('base64');
  socket.write(
    'HTTP/1.1 101 Switching Protocols\r\n' +
      'Upgrade: websocket\r\n' +
      'Connection: Upgrade\r\n' +
      'Sec-WebSocket-Accept: ' + accept + '\r\n\r\n'
  );

  console.log('[fake-ws] client connected ' + req.url);
  const timer = setInterval(() => {
    try {
      socket.write(frame(snapshot()));
    } catch (err) {
      clearInterval(timer);
    }
  }, 360);

  socket.on('data', (chunk) => {
    // 只处理 close 帧（opcode 0x8）与 ping（0x9）
    const opcode = chunk[0] & 0x0f;
    if (opcode === 0x8) {
      clearInterval(timer);
      socket.end();
    } else if (opcode === 0x9) {
      socket.write(Buffer.from([0x8a, 0x00]));
    }
  });
  socket.on('close', () => clearInterval(timer));
  socket.on('error', () => clearInterval(timer));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('[fake-ws] listening ws://127.0.0.1:' + PORT + '/lazer');
});
