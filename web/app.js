const SWATCHES = {
  mix: 'linear-gradient(135deg,#ff2a6d,#ff8c1a,#ffe11a,#3ddc84,#1fb6ff,#8f5bff)',
  peter_max: 'radial-gradient(circle at 50% 60%,#fff6a8 0 12%,#ffc21a 12% 22%,#ff5e1f 22% 34%,#c2187a 34% 48%,#1fb6ff 48% 62%,#3ddc84 62% 76%,#8f5bff 76%)',
  warhol: 'conic-gradient(from 90deg at 50% 50%,#ff006e 0 25%,#2ec4b6 0 50%,#ffd60a 0 75%,#7209b7 0)',
  lichtenstein: 'radial-gradient(#e8333a 32%,transparent 34%) 0 0/8px 8px,#ffd31a',
  haring: 'radial-gradient(circle at 50% 55%,#ff2a1a 0 30%,#111 30% 34%,transparent 34%),repeating-conic-gradient(#111 0 4deg,transparent 4deg 22deg),#00a651',
  fairey: 'linear-gradient(90deg,#70969f 0 50%,#d71a21 50%) top/100% 82% no-repeat,linear-gradient(#112e51,#112e51)',
  hockney: 'linear-gradient(8deg,transparent 46%,#fff 46% 49%,transparent 49%),linear-gradient(-80deg,transparent 46%,#fff 46% 49%,transparent 49%),linear-gradient(135deg,#ffb88c,#4cc9f0)',
  mondrian: 'linear-gradient(90deg,transparent 58%,#111 58% 62%,transparent 62%),linear-gradient(transparent 40%,#111 40% 44%,transparent 44%),linear-gradient(90deg,#d40920 0 58%,#f2efe6 58%) top/100% 40% no-repeat,linear-gradient(90deg,#f2efe6 0 58%,#1356a2 58%) bottom/100% 56% no-repeat,#f7d842',
  kusama: 'radial-gradient(#fff 30%,transparent 33%) 0 0/10px 10px,#e60012',
  klimt: 'radial-gradient(circle,#111 0 18%,#f4d26a 18% 30%,transparent 30%) 0 0/16px 16px,linear-gradient(135deg,#7a5a16,#f4d26a,#a47a1e)',
  banksy: 'radial-gradient(circle at 74% 26%,#d6001c 0 10%,transparent 11%),linear-gradient(#c9c5bd,#a9a59d)',
  van_gogh: 'radial-gradient(circle at 72% 28%,#ffe14d 0 9%,transparent 10%),repeating-radial-gradient(circle at 40% 40%,#1b3f8f 0 5px,#3d6fd1 5px 9px,#1b3f8f 9px 12px)',
  monet: 'radial-gradient(circle at 30% 30%,#f7c6d9 0 18%,transparent 30%),radial-gradient(circle at 70% 65%,#a8d8c0 0 20%,transparent 34%),linear-gradient(135deg,#b9c8f0,#f3e3b0)',
  seurat: 'radial-gradient(#ff8c42 30%,transparent 35%) 0 0/6px 6px,radial-gradient(#3a7bd5 30%,transparent 35%) 3px 3px/6px 6px,#e9f0c9',
  picasso: 'conic-gradient(from 20deg at 40% 55%,#c98b4b 0 70deg,#6f8fa6 0 150deg,#e7cfa0 0 220deg,#8a5a3c 0 290deg,#b7c4c9 0)',
  matisse: 'radial-gradient(ellipse 30% 18% at 70% 30%,#f2c12e 98%,transparent),radial-gradient(ellipse 22% 30% at 30% 70%,#2e9e6a 98%,transparent),#e85a8a',
  mucha: 'radial-gradient(circle at 50% 45%,transparent 0 30%,#c9a24a 30% 33%,transparent 33%),linear-gradient(#f3dfc4,#e7b9a5)',
  hokusai: 'radial-gradient(circle at 30% 100%,#f4ecd8 0 22%,#1d3f73 22% 40%,#f4ecd8 40% 44%,#2c5d9b 44% 60%,transparent 60%),#efe3c6',
  kandinsky: 'radial-gradient(circle at 30% 35%,#e8333a 0 14%,#111 14% 17%,#ffd31a 17% 26%,transparent 26%),linear-gradient(60deg,transparent 60%,#1356a2 60% 63%,transparent 63%),#f2ead9',
  kahlo: 'radial-gradient(circle at 30% 25%,#e63946 0 12%,transparent 13%),radial-gradient(circle at 65% 20%,#ff5ca8 0 10%,transparent 11%),linear-gradient(#1f6b3a,#2e8b4a)',
  dali: 'radial-gradient(ellipse 30% 16% at 68% 70%,#e5d36a 96%,transparent),linear-gradient(#2b3a8c 0 45%,#e8955a 45% 60%,#c9a26b 60%)',
  basquiat: 'linear-gradient(-30deg,transparent 40%,#ffcf1a 40% 46%,transparent 46%),radial-gradient(circle at 30% 30%,#e8333a 0 14%,transparent 15%),#1d1d1d',
  rothko: 'linear-gradient(#7a1414 0 8%,#e2671c 8% 48%,#7a1414 48% 54%,#f2b21b 54% 92%,#7a1414 92%)',
  pollock: 'linear-gradient(20deg,transparent 47%,#111 47% 50%,transparent 50%),linear-gradient(-40deg,transparent 30%,#d6c7a1 30% 32%,transparent 32%),linear-gradient(80deg,transparent 60%,#a32020 60% 62%,transparent 62%),#e9e1cf',
  hopper: 'linear-gradient(115deg,transparent 45%,rgba(255,225,150,.75) 45% 65%,transparent 65%),linear-gradient(#5b2c1f,#2e1a14)',
  magritte: 'radial-gradient(circle at 60% 55%,#3fb54a 0 16%,transparent 17%),radial-gradient(ellipse 30% 12% at 30% 25%,#fff 96%,transparent),linear-gradient(#5aa9ec,#bfe2fb)',
  escher: 'repeating-conic-gradient(from 0deg at 50% 50%,#111 0 20deg,#f2efe6 20deg 40deg)',
  hirst: 'radial-gradient(circle,#e8333a 0 28%,transparent 30%) 0 0/12px 12px,radial-gradient(circle,#1fb6ff 0 28%,transparent 30%) 6px 6px/12px 12px,#fff',
  murakami: 'radial-gradient(circle at 50% 50%,#ffe11a 0 12%,#ff5ca8 12% 22%,transparent 22%),repeating-conic-gradient(#ff2a6d 0 15deg,#ffe11a 0 30deg,#3ddc84 0 45deg,#1fb6ff 0 60deg)',
  vasarely: 'radial-gradient(circle at 50% 50%,#ffcf1a 0 20%,transparent 50%),repeating-conic-gradient(#e2671c 0 25%,#7a1414 0 50%) 0 0/10px 10px',
  britto: 'linear-gradient(45deg,transparent 48%,#111 48% 52%,transparent 52%),linear-gradient(-45deg,#ff2a9c 0 50%,#1fb6ff 50%) top/100% 50% no-repeat,linear-gradient(-45deg,#ffe11a 0 50%,#3ddc84 50%) bottom/100% 50% no-repeat',
  flattering: 'linear-gradient(135deg,#ffd1b3,#ff9a8b 50%,#a18cd1)',
  glitch: 'linear-gradient(90deg,#ff004c 0 33%,#00ffd5 33% 66%,#5b00ff 66%)',
};

const MESSAGES = [
  'Warming up the rainbow boilers…',
  'Stirring the river of paint…',
  'Polishing the gumball gears…',
  'Folding in everlasting color…',
  'Calibrating the groove-o-meter…',
  'Whipping up a cosmic backdrop…',
  'Sprinkling stardust on the edges…',
];

const INTENSITY = [['low', 'Mild'], ['medium', 'Wild'], ['high', 'Whoa']];
const PHOTO_STYLES = new Set(['flattering', 'glitch']);
const FRAME = 320;
const GAP = 48;
const ROW_GAP = 120;
const PER_ROW = 6;

function slot(k, y) {
  return {
    x: (k % PER_ROW) * (FRAME + GAP),
    y: y + Math.floor(k / PER_ROW) * (FRAME + GAP + 24),
  };
}

const $ = (id) => document.getElementById(id);
const viewport = $('viewport');
const world = $('world');
const grid = $('grid');
const inspector = $('inspector');
const fileInput = $('file');
const runBtn = $('run-btn');
const toast = $('toast');

const state = {
  file: null,
  fileUrl: null,
  styles: [],
  style: 'peter_max',
  variants: 4,
  intensity: 'medium',
  steps: 3,
  seed: '',
  frames: [],
  runs: [],
  selected: null,
  view: { x: 0, y: 0, z: 1 },
  tool: 'move',
  space: false,
  running: false,
  assetQuery: '',
};

const IS_MAC = /Mac|iPhone|iPad|iPod/.test(navigator.userAgentData?.platform || navigator.platform || navigator.userAgent);
const MOD = IS_MAC ? '⌘' : 'Ctrl';
const NARROW_LEFT = matchMedia('(max-width: 980px)');
const NARROW_RIGHT = matchMedia('(max-width: 720px)');
const UPLOAD_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const DEMO = Boolean(document.querySelector('meta[name="hp-demo"]'));

let scene = null;

function loadScene() {
  if (navigator.connection?.saveData) return;
  const light = NARROW_RIGHT.matches || matchMedia('(pointer: coarse)').matches || (navigator.hardwareConcurrency || 8) <= 4;
  import(new URL('./scene.js', import.meta.url).href)
    .then(({ startScene }) => { scene = startScene($('scene3d'), () => state.view, { light }); })
    .catch(() => {});
}

const whenIdle = (fn) => (window.requestIdleCallback ? requestIdleCallback(fn, { timeout: 1500 }) : setTimeout(fn, 200));
if (document.readyState === 'complete') whenIdle(loadScene);
else window.addEventListener('load', () => whenIdle(loadScene), { once: true });

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'class') node.className = value;
    else if (key === 'style') node.style.cssText = value;
    else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
    else if (value !== false && value != null) node.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) {
    if (child == null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function icon(path) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.classList.add('icon');
  const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  p.setAttribute('d', path);
  svg.append(p);
  return svg;
}

const ICONS = {
  frame: 'M7 3v18M17 3v18M3 7h18M3 17h18',
  image: 'M4 5h16v14H4zM4 15l4-4 4 4 3-3 5 5',
  group: 'M4 6h16M4 12h16M4 18h10',
  dice: 'M5 5h14v14H5zM9 9h.01M15 9h.01M12 12h.01M9 15h.01M15 15h.01',
};

function labelFor(style) {
  return state.styles.find((s) => s.id === style)?.label ?? style;
}

function swatch(style, extra = '') {
  return el('span', { class: `swatch ${extra}`, style: `background:${SWATCHES[style] ?? SWATCHES.mix}` });
}

/* ---------- view ---------- */

function applyView() {
  const { x, y, z } = state.view;
  world.style.transform = `translate(${x}px, ${y}px) scale(${z})`;
  document.documentElement.style.setProperty('--z', z);
  const size = 24 * z;
  grid.style.backgroundSize = `${size}px ${size}px`;
  grid.style.backgroundPosition = `${x}px ${y}px`;
  grid.style.opacity = z < 0.35 ? 0 : 0.6;
  $('zoom-btn').textContent = `${Math.round(z * 100)}%`;
  world.classList.add('moving');
  clearTimeout(applyView.timer);
  applyView.timer = setTimeout(() => world.classList.remove('moving'), 180);
}

function zoomAt(factor, cx, cy) {
  const { x, y, z } = state.view;
  const next = Math.min(4, Math.max(0.1, z * factor));
  const k = next / z;
  state.view = { x: cx - (cx - x) * k, y: cy - (cy - y) * k, z: next };
  applyView();
}

function fitTo(frames, animate = true) {
  const list = frames.length ? frames : state.frames;
  if (!list.length) return;
  const box = list.reduce(
    (b, f) => ({
      l: Math.min(b.l, f.x), t: Math.min(b.t, f.y - 24),
      r: Math.max(b.r, f.x + f.w), b: Math.max(b.b, f.y + f.h),
    }),
    { l: Infinity, t: Infinity, r: -Infinity, b: -Infinity },
  );
  const rect = viewport.getBoundingClientRect();
  const pad = 80;
  const z = Math.min(1.5, Math.max(0.1, Math.min(
    (rect.width - pad * 2) / (box.r - box.l),
    (rect.height - pad * 2) / (box.b - box.t),
  )));
  const target = {
    x: rect.width / 2 - ((box.l + box.r) / 2) * z,
    y: rect.height / 2 - ((box.t + box.b) / 2) * z,
    z,
  };
  if (!animate || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    state.view = target;
    applyView();
    return;
  }
  const start = { ...state.view };
  const t0 = performance.now();
  const step = (now) => {
    const t = Math.min(1, (now - t0) / 420);
    const e = 1 - Math.pow(1 - t, 3);
    state.view = {
      x: start.x + (target.x - start.x) * e,
      y: start.y + (target.y - start.y) * e,
      z: start.z + (target.z - start.z) * e,
    };
    applyView();
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ---------- the machine ---------- */

const CAMERA_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 5.5 13.3 3.8h-2.6L9.5 5.5H5A2.5 2.5 0 0 0 2.5 8v9A2.5 2.5 0 0 0 5 19.5h14a2.5 2.5 0 0 0 2.5-2.5V8A2.5 2.5 0 0 0 19 5.5h-4.5Z"/><circle cx="12" cy="12.5" r="3.5"/></svg>';

function press(handler) {
  return (event) => { event.stopPropagation(); handler(); };
}

function gauge(label) {
  return el('div', { class: 'gauge' },
    el('div', { class: 'dial' }, el('span', { class: 'needle' }), el('span', { class: 'hub' })),
    el('span', { class: 'gauge-label' }, label));
}

function wonkaMachine(image) {
  const core = el('div', { class: 'lens-core' });
  core.innerHTML = CAMERA_SVG;
  const screen = el('div', { class: 'atm-screen' },
    image || el('div', { class: 'scanner' },
      el('div', { class: 'holo-lens' }, core),
      el('p', { class: 'scanner-eyebrow' }, 'Pure imagination'),
      el('h2', { class: 'scanner-title' }, 'Insert one face'),
      el('p', { class: 'scanner-sub' }, 'Drop a portrait on the machine, or feed it through the slot below.'),
      el('button', { class: 'activate-key', onclick: press(() => fileInput.click()) }, 'Choose image'),
      el('p', { class: 'scanner-hint' }, 'JPEG · PNG · WebP · up to 10 MB'),
    ),
    el('div', { class: 'scan-line' }),
    el('div', { class: 'reticle' },
      el('span', { class: 'corner tl' }), el('span', { class: 'corner tr' }),
      el('span', { class: 'corner bl' }), el('span', { class: 'corner br' })),
  );

  const flavors = INTENSITY.map(([value, label], i) => el('button', {
    class: `gumdrop g${i} ${state.intensity === value ? 'on' : ''}`,
    title: `${label} intensity`,
    'aria-pressed': String(state.intensity === value),
    onclick: press(() => { state.intensity = value; renderInspector(); renderFrame(dropFrame); }),
  }, label));

  return el('div', { class: `wonka ${state.running ? 'busy' : ''}` },
    el('div', { class: 'marquee' },
      el('span', { class: 'bulbs a' }), el('span', { class: 'bulbs b' }),
      el('div', { class: 'marquee-title' }, 'Hyper Portraits'),
      el('div', { class: 'marquee-sub' }, 'Portrait ATM · Est. 1971')),
    el('div', { class: 'wonka-body' },
      screen,
      el('div', { class: 'wonka-side' },
        el('div', { class: 'gauges' }, gauge('Fizz'), gauge('Whimsy')),
        el('div', { class: 'side-label' }, 'Flavor'),
        el('div', { class: 'gumdrops' }, flavors),
        el('button', {
          class: 'dispense',
          disabled: !state.file || state.running,
          title: state.file ? 'Run the machine' : 'Insert a face first',
          onclick: press(() => run()),
        }, el('span', {}, state.running ? 'Whirring' : 'Dispense')))),
    el('div', { class: 'wonka-foot' },
      artistReel(),
      el('button', { class: 'card-slot', onclick: press(() => fileInput.click()) },
        el('span', { class: 'slot' }),
        el('span', { class: 'slot-label' }, state.file ? 'New face' : 'Insert face'))),
  );
}

function artistReel() {
  const index = Math.max(0, state.styles.findIndex((s) => s.id === state.style));
  const step = (delta) => {
    const next = state.styles[(index + delta + state.styles.length) % state.styles.length];
    if (next) setStyle(next.id);
  };
  return el('div', { class: 'reel' },
    el('div', { class: 'reel-head' },
      el('span', { class: 'reel-tag' }, 'Artist'),
      el('span', { class: 'reel-name' }, labelFor(state.style))),
    el('div', { class: 'reel-row' },
      el('button', { class: 'reel-arrow', 'aria-label': 'Previous artist', onclick: press(() => step(-1)) }, '◀'),
      el('div', { class: 'reel-strip', role: 'listbox', 'aria-label': 'Artist style' },
        state.styles.map((s) => el('button', {
          class: `gumball-pick ${s.id === state.style ? 'on' : ''}`,
          role: 'option',
          'aria-selected': String(s.id === state.style),
          'aria-label': s.label,
          title: s.label,
          style: `background:${SWATCHES[s.id] ?? SWATCHES.mix}`,
          onclick: press(() => setStyle(s.id)),
        }))),
      el('button', { class: 'reel-arrow', 'aria-label': 'Next artist', onclick: press(() => step(1)) }, '▶')),
  );
}

function centerReel(node) {
  const strip = node.querySelector('.reel-strip');
  const on = strip?.querySelector('.on');
  if (on) strip.scrollLeft = on.offsetLeft - (strip.clientWidth - on.offsetWidth) / 2;
}

function setStyle(id) {
  state.style = id;
  renderAssets();
  renderInspector();
  renderFrame(dropFrame);
}

/* ---------- frames ---------- */

function frameNode(frame) {
  const node = el('div', {
    class: `frame ${frame.kind === 'drop' ? 'drop' : ''}`,
    style: `left:${frame.x}px;top:${frame.y}px;width:${frame.w}px;height:${frame.h}px`,
    'data-id': frame.id,
  });
  node.append(
    el('div', { class: 'frame-label' }, frame.title),
    el('span', { class: 'handle tl' }), el('span', { class: 'handle tr' }),
    el('span', { class: 'handle bl' }), el('span', { class: 'handle br' }),
  );
  const image = frame.url && el('img', { src: frame.url, alt: frame.title, draggable: 'false', decoding: 'async' });
  if (frame.kind === 'drop') node.append(wonkaMachine(image));
  else if (image) node.append(image);
  if (frame.pending) node.classList.add('pending');
  frame.node = node;
  return node;
}

function renderFrame(frame) {
  const old = frame.node;
  const node = frameNode(frame);
  if (frame.kind === 'drop' && state.fileUrl) node.classList.add('filled');
  if (state.selected === frame.id) node.classList.add('selected');
  if (old) old.replaceWith(node);
  else world.append(node);
  if (frame.kind === 'drop') centerReel(node);
}

function addFrame(frame) {
  state.frames.push(frame);
  renderFrame(frame);
  return frame;
}

function frameById(id) {
  return state.frames.find((f) => f.id === id);
}

function select(id) {
  state.selected = id;
  for (const f of state.frames) f.node?.classList.toggle('selected', f.id === id);
  renderLayers();
  renderInspector();
}

function removeFrame(id) {
  const frame = frameById(id);
  if (!frame || frame.kind === 'drop') return;
  frame.node?.remove();
  state.frames = state.frames.filter((f) => f.id !== id);
  for (const run of state.runs) run.frames = run.frames.filter((fid) => fid !== id);
  state.runs = state.runs.filter((run) => run.frames.length);
  select(null);
}

const dropFrame = addFrame({
  id: 'input', kind: 'drop', title: 'Input', x: -FRAME - 220, y: 0, w: FRAME + 160, h: FRAME + 160,
});

function setFile(file) {
  if (!file) return;
  if (/hei[cf]/i.test(file.type) || /\.hei[cf]$/i.test(file.name)) {
    showToast('HEIC photos aren’t supported yet. Export it as JPEG first.', true);
    return;
  }
  if (!UPLOAD_TYPES.includes(file.type) && !(!file.type && /\.(jpe?g|png|webp)$/i.test(file.name))) {
    showToast('Use a JPEG, PNG, or WebP image.', true);
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast('That image is over 10 MB.', true);
    return;
  }
  if (state.fileUrl) URL.revokeObjectURL(state.fileUrl);
  state.file = file;
  state.fileUrl = URL.createObjectURL(file);
  dropFrame.url = state.fileUrl;
  dropFrame.title = `Input — ${file.name}`;
  renderFrame(dropFrame);
  $('file-title').textContent = file.name;
  runBtn.disabled = false;
  select('input');
  hideToast();
}

/* ---------- running the machine ---------- */

let messageTimer = null;

function showToast(text, error = false) {
  toast.classList.remove('hidden');
  toast.classList.toggle('error', error);
  $('toast-text').textContent = text;
  if (error) setTimeout(hideToast, 4200);
}

function hideToast() {
  toast.classList.add('hidden');
}

function nextRowY() {
  const rows = state.frames.filter((f) => f.kind !== 'drop');
  if (!rows.length) return 0;
  return Math.max(...rows.map((f) => f.y + f.h)) + ROW_GAP;
}

async function run(overrides = {}) {
  if (!state.file || state.running) return;
  if (DEMO) {
    showToast('Demo page: clone the GitHub repo and run it locally to make portraits.', true);
    return;
  }
  const settings = {
    style: state.style, variants: state.variants, intensity: state.intensity,
    steps: state.steps, seed: state.seed, ...overrides,
  };
  state.running = true;
  renderFrame(dropFrame);
  runBtn.disabled = true;
  runBtn.classList.add('pulled');
  runBtn.querySelector('.run-label').textContent = 'Whirring…';
  scene?.setBusy(true);

  let i = 0;
  showToast(MESSAGES[0]);
  messageTimer = setInterval(() => { $('toast-text').textContent = MESSAGES[++i % MESSAGES.length]; }, 1500);

  const runIndex = state.runs.length + 1;
  const y = nextRowY();
  const pending = [];
  for (let k = 0; k <= settings.variants; k++) {
    pending.push(addFrame({
      id: `pending-${runIndex}-${k}`, kind: 'pending', pending: true,
      title: k === 0 ? 'Aligned face' : 'Brewing…',
      ...slot(k, y), w: FRAME, h: FRAME,
    }));
  }
  fitTo(pending);

  const body = new FormData();
  body.append('file', state.file);
  body.append('style', settings.style);
  body.append('n_variants', settings.variants);
  body.append('n_transforms', settings.steps);
  body.append('intensity', settings.intensity);
  if (settings.seed !== '' && settings.seed != null) body.append('seed', settings.seed);

  try {
    const response = await fetch('/api/generate', { method: 'POST', body });
    const text = await response.text();
    if (!response.ok) {
      let message = text;
      try { message = JSON.parse(text).detail || text; } catch (_) { /* plain text */ }
      throw new Error(message);
    }
    const data = JSON.parse(text);
    for (const f of pending) f.node.remove();
    state.frames = state.frames.filter((f) => !pending.includes(f));

    const ids = [];
    const source = addFrame({
      id: `${data.job_id}-source`, kind: 'source', url: data.source_url,
      title: data.face_detected ? 'Aligned face' : 'Full frame (no face found)',
      ...slot(0, y), w: FRAME, h: FRAME, job: data.job_id, face: data.face_detected, seed: data.seed,
    });
    ids.push(source.id);
    data.variants.forEach((variant, k) => {
      const frame = addFrame({
        id: `${data.job_id}-${variant.id}`, kind: 'variant', url: variant.url,
        title: `${variant.label} — ${variant.id}`,
        ...slot(k + 1, y), w: FRAME, h: FRAME,
        job: data.job_id, variant,
      });
      frame.node.classList.add('pop');
      frame.node.style.animationDelay = `${k * 70}ms`;
      ids.push(frame.id);
    });
    state.runs.push({
      id: data.job_id, index: runIndex, label: labelFor(settings.style),
      seed: data.seed, frames: ids,
    });
    fitTo(ids.map(frameById));
    select(ids[1] ?? ids[0]);
    scene?.celebrate();
    hideToast();
  } catch (error) {
    for (const f of pending) f.node.remove();
    state.frames = state.frames.filter((f) => !pending.includes(f));
    showToast(error.message || 'The machine jammed.', true);
  } finally {
    clearInterval(messageTimer);
    state.running = false;
    renderFrame(dropFrame);
    runBtn.disabled = !state.file;
    runBtn.classList.remove('pulled');
    runBtn.querySelector('.run-label').textContent = 'Run the machine';
    scene?.setBusy(false);
    renderLayers();
  }
}

/* ---------- left panel ---------- */

function renderLayers() {
  const root = $('layers');
  root.replaceChildren();
  const layerRow = (frame, child, iconPath) => el('div', {
    class: `layer ${child ? 'child' : ''} ${state.selected === frame.id ? 'selected' : ''}`,
    onclick: () => { select(frame.id); fitTo([frame]); },
    ondblclick: () => { if (frame.url) openLightbox(frame); },
  }, icon(iconPath), frame.title);

  root.append(layerRow(dropFrame, false, ICONS.frame));
  if (!state.runs.length) {
    root.append(el('div', { class: 'layer-empty' },
      'Runs show up here. Feed the machine a face, pick an artist in Assets, then pull the lever.'));
    return;
  }
  for (const run of [...state.runs].reverse()) {
    const group = el('div', { class: 'layer-group' });
    group.append(el('div', {
      class: 'layer group-head',
      onclick: () => fitTo(run.frames.map(frameById).filter(Boolean)),
    }, icon(ICONS.group), `Run ${run.index} · ${run.label}`));
    for (const id of run.frames) {
      const frame = frameById(id);
      if (frame) group.append(layerRow(frame, true, ICONS.image));
    }
    root.append(group);
  }
}

function renderAssets() {
  const root = $('assets');
  root.replaceChildren();
  const query = state.assetQuery.trim().toLowerCase();
  const styles = state.styles.filter((s) => !query || s.label.toLowerCase().includes(query));
  if (!styles.length) root.append(el('div', { class: 'hint', style: 'grid-column:1/-1' }, 'No artists match.'));
  for (const style of styles) {
    root.append(el('button', {
      class: `asset ${state.style === style.id ? 'selected' : ''}`,
      onclick: () => setStyle(style.id),
      title: style.label,
    }, swatch(style.id), el('span', { class: 'asset-name' }, style.label)));
  }
}

function showTab(name) {
  document.querySelectorAll('.tab').forEach((t) => t.classList.toggle('active', t.dataset.tab === name));
  $('layers-tab').classList.toggle('hidden', name !== 'layers');
  $('assets-tab').classList.toggle('hidden', name !== 'assets');
}

/* ---------- inspector ---------- */

function section(title, ...children) {
  return el('div', { class: 'insp-section' }, el('div', { class: 'insp-title' }, title), ...children);
}

function row(label, control) {
  return el('div', { class: 'row' }, el('label', {}, label), control);
}

function machineSection() {
  const styleSelect = el('select', {
    class: 'select',
    onchange: (e) => setStyle(e.target.value),
  }, state.styles.map((s) => el('option', { value: s.id, selected: s.id === state.style }, s.label)));

  const intensity = el('div', { class: 'segmented', role: 'radiogroup' },
    INTENSITY.map(([value, label]) => el('button', {
      class: state.intensity === value ? 'on' : '',
      role: 'radio',
      'aria-checked': state.intensity === value ? 'true' : 'false',
      onclick: () => { state.intensity = value; renderInspector(); renderFrame(dropFrame); },
    }, label)));

  const ticket = el('div', { class: 'ticket' },
    el('input', {
      type: 'number', placeholder: 'Random', value: state.seed,
      'aria-label': 'Golden ticket seed',
      oninput: (e) => { state.seed = e.target.value; },
    }),
    el('button', {
      class: 'dice', title: 'Roll a new ticket',
      onclick: () => { state.seed = String(Math.floor(Math.random() * 2 ** 31)); renderInspector(); },
    }, icon(ICONS.dice)));

  return section('Machine',
    row('Style', el('div', {}, styleSelect)),
    row('Variants', el('input', {
      class: 'field', type: 'number', min: 1, max: 30, value: state.variants,
      oninput: (e) => { state.variants = Math.max(1, Math.min(30, Number(e.target.value) || 1)); },
    })),
    row('Intensity', intensity),
    PHOTO_STYLES.has(state.style) && row('Steps', el('input', {
      class: 'field', type: 'number', min: 1, max: 6, value: state.steps,
      oninput: (e) => { state.steps = Math.max(1, Math.min(6, Number(e.target.value) || 1)); },
    })),
    row('Ticket', ticket),
    el('div', { class: 'hint' }, 'The same golden ticket and photo always print the same portraits.'),
  );
}

function formatValue(value) {
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(2);
  if (Array.isArray(value)) return value.map(formatValue).join(', ');
  return String(value);
}

function selectionSection(frame) {
  if (frame.kind === 'drop') {
    return section('Input',
      el('div', { class: 'hint' }, state.file
        ? `${state.file.name} · ${(state.file.size / 1024 / 1024).toFixed(1)} MB`
        : 'No face yet. Drop a portrait on the Input frame.'),
      el('div', { class: 'btn-row single', style: 'margin-top:10px' },
        el('button', { class: 'btn', onclick: () => fileInput.click() }, state.file ? 'Replace image' : 'Choose image')));
  }
  if (frame.kind === 'source') {
    return section('Aligned face',
      el('div', { class: 'props' },
        el('div', { class: 'prop' }, el('span', {}, 'Face found'), el('span', {}, frame.face ? 'Yes' : 'No')),
        el('div', { class: 'prop' }, el('span', {}, 'Base ticket'), el('span', {}, frame.seed))),
      el('div', { class: 'btn-row single', style: 'margin-top:10px' },
        el('a', { class: 'btn', href: frame.url, download: 'aligned.png' }, 'Download PNG')));
  }
  if (frame.kind !== 'variant') return null;

  const { variant } = frame;
  const props = [];
  for (const step of variant.recipe) {
    for (const [key, value] of Object.entries(step.params)) {
      if (key === 'seed') continue;
      props.push(el('div', { class: 'prop' }, el('span', {}, key), el('span', { title: formatValue(value) }, formatValue(value))));
    }
  }
  return el('div', {},
    section('Selection',
      el('button', {
        class: 'style-chip',
        onclick: () => setStyle(variant.style),
        title: 'Use this style in the machine',
      }, swatch(variant.style), variant.label),
      el('div', { class: 'props', style: 'margin-top:10px' },
        el('div', { class: 'prop' }, el('span', {}, 'Ticket'), el('span', {}, variant.seed)),
        el('div', { class: 'prop' }, el('span', {}, 'Recipe'), el('span', {}, variant.recipe.map((s) => s.transform).join(' → ')))),
    ),
    section('Ingredients', props.length ? el('div', { class: 'props' }, props) : el('div', { class: 'hint' }, 'No parameters.')),
    section('Export',
      el('div', { class: 'btn-row' },
        el('a', { class: 'btn primary', href: variant.url, download: `${variant.style}-${variant.seed}.png` }, 'Download'),
        el('button', {
          class: 'btn',
          disabled: !state.file || state.running,
          onclick: () => run({ style: variant.style, variants: 1, seed: '' }),
        }, 'Remix')),
      el('div', { class: 'btn-row single', style: 'margin-top:8px' },
        el('button', {
          class: 'btn',
          onclick: () => {
            state.seed = String(variant.seed);
            state.variants = 1;
            setStyle(variant.style);
          },
        }, 'Load this golden ticket')),
    ),
  );
}

function shortcutsSection() {
  const pairs = [
    ['Run the machine', `${MOD} ↵`], ['Move / Hand', 'V / H'], ['Pan', 'Space + drag'],
    ['Zoom', `${MOD} + scroll`], ['Zoom to fit', '⇧ 1'], ['Delete frame', '⌫'],
    ['Enlarge image', 'Double-click'], ['Toggle panels', '[ / ]'], ['Hide all panels', `${MOD} \\`],
  ];
  return section('Shortcuts', el('div', { class: 'shortcuts' },
    pairs.flatMap(([label, keys]) => [el('span', {}, label), el('kbd', { class: 'k' }, keys)])));
}

function renderInspector() {
  const frame = frameById(state.selected);
  inspector.replaceChildren(
    ...(frame ? [selectionSection(frame)] : []),
    machineSection(),
    shortcutsSection(),
  );
}

/* ---------- canvas interaction ---------- */

let drag = null;
let pinch = null;
let lastTap = null;
let gesturing = false;
const pointers = new Map();

function frameAt(x, y) {
  const node = document.elementsFromPoint(x, y).map((n) => n.closest('.frame')).find(Boolean);
  return node && frameById(node.dataset.id);
}

function pinchState() {
  const [a, b] = [...pointers.values()];
  const rect = viewport.getBoundingClientRect();
  return {
    dist: Math.hypot(a.x - b.x, a.y - b.y) || 1,
    mx: (a.x + b.x) / 2 - rect.left,
    my: (a.y + b.y) / 2 - rect.top,
  };
}

viewport.addEventListener('pointerdown', (event) => {
  if (event.target.closest('button, a, input')) return;
  viewport.focus({ preventScroll: true });
  if (NARROW_LEFT.matches && panelOpen('left')) setPanel('left', false, false);
  if (NARROW_RIGHT.matches && panelOpen('right')) setPanel('right', false, false);
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  viewport.setPointerCapture(event.pointerId);

  if (pointers.size === 2) {
    drag = null;
    pinch = pinchState();
    return;
  }
  if (pointers.size > 2) return;

  const touch = event.pointerType !== 'mouse';
  const frameEl = event.target.closest('.frame');
  const panning = touch || state.tool === 'hand' || state.space || event.button === 1;
  const frame = frameEl && frameById(frameEl.dataset.id);
  if (frame) select(frame.id);
  else if (!panning || touch) select(null);

  if (!panning && frame) {
    drag = { kind: 'frame', frame, sx: event.clientX, sy: event.clientY, fx: frame.x, fy: frame.y, moved: false };
  } else {
    drag = { kind: 'pan', frame, sx: event.clientX, sy: event.clientY, vx: state.view.x, vy: state.view.y, moved: false };
    viewport.classList.add('panning');
  }
});

viewport.addEventListener('pointermove', (event) => {
  if (!pointers.has(event.pointerId)) return;
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
  if (pinch && pointers.size >= 2) {
    const next = pinchState();
    state.view.x += next.mx - pinch.mx;
    state.view.y += next.my - pinch.my;
    zoomAt(next.dist / pinch.dist, next.mx, next.my);
    pinch = next;
    return;
  }
  if (!drag) return;
  const dx = event.clientX - drag.sx;
  const dy = event.clientY - drag.sy;
  if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
  if (drag.kind === 'pan') {
    state.view.x = drag.vx + dx;
    state.view.y = drag.vy + dy;
    applyView();
  } else {
    drag.frame.x = drag.fx + dx / state.view.z;
    drag.frame.y = drag.fy + dy / state.view.z;
    drag.frame.node.style.left = `${drag.frame.x}px`;
    drag.frame.node.style.top = `${drag.frame.y}px`;
  }
});

function endDrag(event) {
  pointers.delete(event.pointerId);
  if (viewport.hasPointerCapture?.(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
  if (pointers.size < 2) pinch = null;
  if (!drag) {
    if (!pointers.size) viewport.classList.toggle('panning', state.tool === 'hand' || state.space);
    return;
  }
  const tapped = event.type === 'pointerup' && !drag.moved;
  if (tapped && drag.frame?.kind === 'drop' && !state.file) fileInput.click();
  if (tapped && event.pointerType !== 'mouse') {
    const now = performance.now();
    const near = lastTap && Math.hypot(event.clientX - lastTap.x, event.clientY - lastTap.y) < 30;
    if (near && now - lastTap.t < 320) {
      const frame = frameAt(event.clientX, event.clientY);
      if (frame?.url && !frame.pending) openLightbox(frame);
      lastTap = null;
    } else {
      lastTap = { t: now, x: event.clientX, y: event.clientY };
    }
  }
  drag = null;
  viewport.classList.toggle('panning', state.tool === 'hand' || state.space);
}

viewport.addEventListener('pointerup', endDrag);
viewport.addEventListener('pointercancel', endDrag);

viewport.addEventListener('wheel', (event) => {
  event.preventDefault();
  const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1;
  let dx = event.deltaX * unit;
  let dy = event.deltaY * unit;
  const rect = viewport.getBoundingClientRect();
  if (event.ctrlKey || event.metaKey) {
    if (gesturing) return;
    zoomAt(Math.exp(-Math.max(-50, Math.min(50, dy)) * 0.01), event.clientX - rect.left, event.clientY - rect.top);
    return;
  }
  if (event.shiftKey && !dx) [dx, dy] = [dy, 0];
  state.view.x -= dx;
  state.view.y -= dy;
  applyView();
}, { passive: false });

let gestureScale = 1;
viewport.addEventListener('gesturestart', (event) => {
  event.preventDefault();
  gesturing = true;
  gestureScale = 1;
});
viewport.addEventListener('gesturechange', (event) => {
  event.preventDefault();
  if (pointers.size >= 2) return;
  const rect = viewport.getBoundingClientRect();
  zoomAt(event.scale / gestureScale, event.clientX - rect.left, event.clientY - rect.top);
  gestureScale = event.scale;
});
viewport.addEventListener('gestureend', (event) => {
  event.preventDefault();
  gesturing = false;
});

viewport.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropFrame.node.classList.add('over');
});
viewport.addEventListener('dragleave', (event) => {
  if (!viewport.contains(event.relatedTarget)) dropFrame.node.classList.remove('over');
});
viewport.addEventListener('drop', (event) => {
  event.preventDefault();
  dropFrame.node.classList.remove('over');
  const file = event.dataTransfer.files[0];
  if (file) setFile(file);
});

fileInput.addEventListener('change', (event) => {
  if (event.target.files[0]) setFile(event.target.files[0]);
  fileInput.value = '';
});

viewport.addEventListener('dblclick', (event) => {
  if (state.tool === 'hand' || state.space || event.target.closest('button, a, input')) return;
  const frame = frameAt(event.clientX, event.clientY);
  if (frame?.url && !frame.pending) openLightbox(frame);
});

/* ---------- lightbox ---------- */

const lightbox = $('lightbox');
const lbImg = $('lightbox-img');
const BAR_SPACE = 76;
let lb = null;

function frameScreenRect(frame) {
  const rect = viewport.getBoundingClientRect();
  const { x, y, z } = state.view;
  return { left: rect.left + x + frame.x * z, top: rect.top + y + frame.y * z, width: frame.w * z, height: frame.h * z };
}

function placeImage(from) {
  const ratio = lbImg.naturalWidth / lbImg.naturalHeight || 1;
  const w = Math.min(innerWidth - 64, (innerHeight - 48 - BAR_SPACE) * ratio);
  const h = w / ratio;
  const left = (innerWidth - w) / 2;
  const top = (innerHeight - BAR_SPACE - h) / 2 + 12;
  lbImg.style.width = `${w}px`;
  lbImg.style.height = `${h}px`;
  if (from) {
    lbImg.style.transition = 'none';
    lbImg.style.transform = `translate(${from.left}px, ${from.top}px) scale(${from.width / w}, ${from.height / h})`;
    lbImg.getBoundingClientRect();
    lbImg.style.transition = '';
  }
  lbImg.style.transform = `translate(${left}px, ${top}px)`;
}

function downloadName(frame) {
  if (frame.variant) return `${frame.variant.style}-${frame.variant.seed}.png`;
  if (frame.kind === 'drop') return state.file?.name ?? 'input.png';
  return 'aligned.png';
}

async function showLightboxFrame(from) {
  const frame = lb.list[lb.index];
  lbImg.src = frame.url;
  lbImg.alt = frame.title;
  try { await lbImg.decode(); } catch (_) { /* show whatever loaded */ }
  placeImage(from);
  $('lb-title').textContent = frame.title;
  $('lb-count').textContent = lb.list.length > 1 ? `${lb.index + 1} / ${lb.list.length}` : '';
  $('lb-download').href = frame.url;
  $('lb-download').download = downloadName(frame);
  $('lb-prev').disabled = lb.index === 0;
  $('lb-next').disabled = lb.index === lb.list.length - 1;
  $('lb-prev').hidden = $('lb-next').hidden = lb.list.length < 2;
}

async function openLightbox(frame) {
  if (lb) return;
  const run = state.runs.find((r) => r.frames.includes(frame.id));
  const list = (run ? run.frames.map(frameById) : [frame]).filter((f) => f?.url);
  lb = { list, index: Math.max(0, list.indexOf(frame)) };
  select(frame.id);
  scene?.setPaused?.(true);
  lightbox.classList.remove('hidden');
  lightbox.classList.add('fading');
  await showLightboxFrame(frameScreenRect(frame));
  lightbox.classList.remove('fading');
  $('lb-close').focus({ preventScroll: true });
}

function stepLightbox(delta) {
  if (!lb) return;
  const index = Math.min(lb.list.length - 1, Math.max(0, lb.index + delta));
  if (index === lb.index) return;
  lb.index = index;
  select(lb.list[index].id);
  showLightboxFrame(null);
}

function closeLightbox() {
  if (!lb) return;
  const frame = lb.list[lb.index];
  lb = null;
  if (frame.node?.isConnected) {
    const r = frameScreenRect(frame);
    const w = parseFloat(lbImg.style.width);
    const h = parseFloat(lbImg.style.height);
    lbImg.style.transform = `translate(${r.left}px, ${r.top}px) scale(${r.width / w}, ${r.height / h})`;
  }
  lightbox.classList.add('fading');
  setTimeout(() => {
    if (lb) return;
    lightbox.classList.add('hidden');
    lbImg.removeAttribute('src');
    scene?.setPaused?.(false);
    viewport.focus({ preventScroll: true });
  }, 300);
}

lightbox.addEventListener('click', closeLightbox);
$('lightbox-bar').addEventListener('click', (event) => event.stopPropagation());
$('lightbox-bar').addEventListener('dblclick', (event) => event.stopPropagation());
$('lb-close').addEventListener('click', closeLightbox);
$('lb-prev').addEventListener('click', () => stepLightbox(-1));
$('lb-next').addEventListener('click', () => stepLightbox(1));
window.addEventListener('resize', () => { if (lb) placeImage(null); });

/* ---------- panels ---------- */

function setPanel(side, open, persist = true) {
  document.body.classList.toggle(`${side}-collapsed`, !open);
  $(`toggle-${side}`).setAttribute('aria-pressed', String(open));
  if (!persist || (side === 'left' ? NARROW_LEFT : NARROW_RIGHT).matches) return;
  try { localStorage.setItem(`hp-panel-${side}`, open ? '1' : '0'); } catch (_) { /* private mode */ }
}

function panelOpen(side) {
  return !document.body.classList.contains(`${side}-collapsed`);
}

function togglePanel(side) {
  setPanel(side, !panelOpen(side));
}

function toggleAllPanels() {
  const open = !(panelOpen('left') || panelOpen('right'));
  setPanel('left', open);
  setPanel('right', open);
}

document.body.style.transition = 'none';
for (const side of ['left', 'right']) {
  let stored = null;
  try { stored = localStorage.getItem(`hp-panel-${side}`); } catch (_) { /* private mode */ }
  const narrow = (side === 'left' ? NARROW_LEFT : NARROW_RIGHT).matches;
  if (narrow || stored === '0') setPanel(side, false, false);
  $(`toggle-${side}`).addEventListener('click', () => togglePanel(side));
}
document.body.getBoundingClientRect();
document.body.style.transition = '';

let viewportLeft = viewport.getBoundingClientRect().left;
new ResizeObserver(() => {
  const left = viewport.getBoundingClientRect().left;
  if (left !== viewportLeft) {
    state.view.x -= left - viewportLeft;
    viewportLeft = left;
    applyView();
  }
}).observe(viewport);

/* ---------- background switch ---------- */

function setBackdrop(on) {
  document.body.classList.toggle('backdrop', on);
  $('bg-switch').setAttribute('aria-checked', String(on));
  $('bg-switch').title = on ? 'Bring back the machine (B)' : 'Show just the background (B)';
  if (on) select(null);
}

const backdropOn = () => document.body.classList.contains('backdrop');
$('bg-switch').addEventListener('click', () => setBackdrop(!backdropOn()));

/* ---------- chrome ---------- */

function setTool(tool) {
  state.tool = tool;
  document.querySelectorAll('.tool[data-tool]').forEach((b) => b.classList.toggle('active', b.dataset.tool === tool));
  viewport.classList.toggle('hand', tool === 'hand');
}

document.querySelectorAll('.tool[data-tool]').forEach((b) => b.addEventListener('click', () => setTool(b.dataset.tool)));
document.querySelectorAll('.tab').forEach((t) => t.addEventListener('click', () => showTab(t.dataset.tab)));
$('upload-btn').addEventListener('click', () => fileInput.click());
$('asset-search').addEventListener('input', (event) => { state.assetQuery = event.target.value; renderAssets(); });
$('zoom-btn').addEventListener('click', () => fitTo([]));
runBtn.addEventListener('click', () => run());

function typing(event) {
  return event.target.closest('input, select, textarea');
}

window.addEventListener('keydown', (event) => {
  if (lb) {
    if (event.key === 'Escape' || event.code === 'Space') closeLightbox();
    else if (event.key === 'ArrowLeft') stepLightbox(-1);
    else if (event.key === 'ArrowRight') stepLightbox(1);
    else return;
    event.preventDefault();
    return;
  }
  if ((event.metaKey || event.ctrlKey) && event.key === '\\') {
    event.preventDefault();
    toggleAllPanels();
    return;
  }
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault();
    run();
    return;
  }
  if (typing(event)) return;
  if (event.code === 'Space' && !state.space) {
    state.space = true;
    viewport.classList.add('panning');
    event.preventDefault();
  } else if (event.key === '[') togglePanel('left');
  else if (event.key === ']') togglePanel('right');
  else if (event.key === 'v' || event.key === 'V') setTool('move');
  else if (event.key === 'h' || event.key === 'H') setTool('hand');
  else if (event.key === 'u' || event.key === 'U') fileInput.click();
  else if (event.key === 'b' || event.key === 'B') setBackdrop(!backdropOn());
  else if (event.key === 'Escape' && backdropOn()) setBackdrop(false);
  else if (event.shiftKey && event.code === 'Digit1') fitTo([]);
  else if (event.shiftKey && event.code === 'Digit0') {
    const rect = viewport.getBoundingClientRect();
    zoomAt(1 / state.view.z, rect.width / 2, rect.height / 2);
  } else if (event.key === '=' || event.key === '+') {
    const rect = viewport.getBoundingClientRect();
    zoomAt(1.2, rect.width / 2, rect.height / 2);
  } else if (event.key === '-') {
    const rect = viewport.getBoundingClientRect();
    zoomAt(1 / 1.2, rect.width / 2, rect.height / 2);
  } else if (event.key === 'Backspace' || event.key === 'Delete') removeFrame(state.selected);
  else if (event.key === 'Escape') select(null);
});

window.addEventListener('keyup', (event) => {
  if (event.code === 'Space') {
    state.space = false;
    viewport.classList.toggle('panning', state.tool === 'hand');
  }
});

window.addEventListener('dragover', (event) => event.preventDefault());
window.addEventListener('drop', (event) => event.preventDefault());

/* ---------- boot ---------- */

async function boot() {
  $('run-kbd').textContent = `${MOD === '⌘' ? '⌘' : 'Ctrl '}↵`;
  const rect = viewport.getBoundingClientRect();
  const z = Math.max(0.2, Math.min(1, (rect.width - 32) / dropFrame.w, (rect.height - 32) / dropFrame.h));
  state.view = {
    x: rect.width / 2 - (dropFrame.x + dropFrame.w / 2) * z,
    y: rect.height / 2 - (dropFrame.y + dropFrame.h / 2) * z,
    z,
  };
  applyView();
  renderLayers();
  renderInspector();

  try {
    const response = await fetch(DEMO ? 'static/styles.json' : '/api/styles');
    if (!response.ok) throw new Error(response.statusText);
    state.styles = await response.json();
  } catch (_) {
    state.styles = [{ id: 'peter_max', label: 'Peter Max' }];
  }
  renderAssets();
  renderInspector();
  renderFrame(dropFrame);
}

boot();
