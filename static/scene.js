import * as THREE from 'three';

const COLORS = [0xff2a6d, 0xff8c1a, 0xffe11a, 0x3ddc84, 0x1fb6ff, 0x8f5bff, 0xff3fa4];

function candy(color) {
  return new THREE.MeshPhysicalMaterial({
    color,
    roughness: 0.18,
    metalness: 0.05,
    clearcoat: 1,
    clearcoatRoughness: 0.06,
  });
}

function canvasTexture(draw, size = 256) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  draw(canvas.getContext('2d'), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const swirlTexture = () => canvasTexture((ctx, s) => {
  const c = s / 2;
  const conic = ctx.createConicGradient(0, c, c);
  ['#ff2a6d', '#ff8c1a', '#ffe11a', '#3ddc84', '#1fb6ff', '#8f5bff', '#ff2a6d']
    .forEach((color, i, all) => conic.addColorStop(i / (all.length - 1), color));
  ctx.fillStyle = conic;
  ctx.fillRect(0, 0, s, s);
  ctx.strokeStyle = 'rgba(255,255,255,0.85)';
  ctx.lineWidth = s * 0.035;
  ctx.beginPath();
  for (let t = 0; t < Math.PI * 8; t += 0.05) {
    const r = (t / (Math.PI * 8)) * c;
    ctx.lineTo(c + Math.cos(t) * r, c + Math.sin(t) * r);
  }
  ctx.stroke();
});

const stripeTexture = (a, b) => {
  const texture = canvasTexture((ctx, s) => {
    ctx.fillStyle = a;
    ctx.fillRect(0, 0, s, s);
    ctx.fillStyle = b;
    for (let x = -s; x < s * 2; x += s / 4) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x + s / 8, 0);
      ctx.lineTo(x + s / 8 + s / 2, s);
      ctx.lineTo(x + s / 2, s);
      ctx.fill();
    }
  });
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(10, 1);
  return texture;
};

function starShape(outer = 1, inner = 0.45, points = 5) {
  const shape = new THREE.Shape();
  for (let i = 0; i < points * 2; i++) {
    const r = i % 2 ? inner : outer;
    const a = (i / (points * 2)) * Math.PI * 2 + Math.PI / 2;
    const x = Math.cos(a) * r;
    const y = Math.sin(a) * r;
    if (i === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  }
  shape.closePath();
  return shape;
}

function heartShape() {
  const s = new THREE.Shape();
  s.moveTo(0, -0.9);
  s.bezierCurveTo(-1.4, -0.1, -1.0, 1.1, 0, 0.45);
  s.bezierCurveTo(1.0, 1.1, 1.4, -0.1, 0, -0.9);
  return s;
}

const extrude = { depth: 0.35, bevelEnabled: true, bevelThickness: 0.12, bevelSize: 0.08, bevelSegments: 4 };

const builders = [
  () => new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), candy(COLORS[Math.floor(Math.random() * COLORS.length)])),
  () => {
    const group = new THREE.Group();
    const disc = new THREE.Mesh(
      new THREE.CylinderGeometry(1.25, 1.25, 0.35, 64),
      [candy(0xffffff), new THREE.MeshPhysicalMaterial({ map: swirlTexture(), clearcoat: 1, roughness: 0.2 }),
        new THREE.MeshPhysicalMaterial({ map: swirlTexture(), clearcoat: 1, roughness: 0.2 })],
    );
    disc.rotation.x = Math.PI / 2;
    const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 3, 16), candy(0xfff6e8));
    stick.position.y = -2.1;
    group.add(disc, stick);
    return group;
  },
  () => new THREE.Mesh(new THREE.ExtrudeGeometry(starShape(), extrude), candy(COLORS[Math.floor(Math.random() * COLORS.length)])).translateZ(-0.2),
  () => new THREE.Mesh(new THREE.ExtrudeGeometry(heartShape(), extrude), candy(0xff2a6d)),
  () => {
    const group = new THREE.Group();
    COLORS.slice(0, 6).forEach((color, i) => {
      const arc = new THREE.Mesh(new THREE.TorusGeometry(2.0 - i * 0.24, 0.12, 16, 80, Math.PI), candy(color));
      group.add(arc);
    });
    return group;
  },
  () => {
    const group = new THREE.Group();
    const planet = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), candy(0x8f5bff));
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(1.75, 0.09, 12, 96),
      new THREE.MeshPhysicalMaterial({ map: stripeTexture('#ffe11a', '#ff3fa4'), clearcoat: 1, roughness: 0.25 }),
    );
    ring.rotation.x = Math.PI / 2.4;
    group.add(planet, ring);
    return group;
  },
  () => new THREE.Mesh(
    new THREE.TorusKnotGeometry(0.75, 0.24, 160, 18),
    new THREE.MeshPhysicalMaterial({ map: stripeTexture('#ffffff', '#ff2a6d'), clearcoat: 1, roughness: 0.2 }),
  ),
];

export function startScene(canvas, getView, { light = false } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: !light, powerPreference: 'low-power' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, light ? 1 : 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200);
  camera.position.set(0, 0, 30);

  scene.add(new THREE.HemisphereLight(0xffc6ec, 0x2a1460, 1.4));
  const key = new THREE.DirectionalLight(0xffffff, 2.4);
  key.position.set(8, 12, 14);
  const rim = new THREE.DirectionalLight(0x1fb6ff, 1.6);
  rim.position.set(-14, -6, 6);
  const warm = new THREE.PointLight(0xff8c1a, 60, 60);
  warm.position.set(10, -8, 10);
  scene.add(key, rim, warm);

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const objects = [];
  const count = light ? 12 : 26;
  for (let i = 0; i < count; i++) {
    const mesh = builders[i % builders.length]();
    const scale = 0.55 + Math.random() * 0.9;
    mesh.scale.setScalar(scale);
    const home = new THREE.Vector3(
      (Math.random() - 0.5) * 64,
      (Math.random() - 0.5) * 38,
      -6 - Math.random() * 26,
    );
    mesh.position.copy(home);
    mesh.rotation.set(Math.random() * 6, Math.random() * 6, Math.random() * 6);
    scene.add(mesh);
    objects.push({
      mesh,
      home,
      spin: new THREE.Vector3((Math.random() - 0.5) * 0.6, (Math.random() - 0.5) * 0.6, (Math.random() - 0.5) * 0.3),
      bob: Math.random() * Math.PI * 2,
      orbit: Math.random() * Math.PI * 2,
    });
  }

  const pointer = { x: 0, y: 0 };
  window.addEventListener('pointermove', (event) => {
    pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
    pointer.y = (event.clientY / window.innerHeight) * 2 - 1;
  }, { passive: true });

  let paused = false;
  let lost = false;
  let pending = false;
  canvas.addEventListener('webglcontextlost', (event) => { event.preventDefault(); lost = true; });
  canvas.addEventListener('webglcontextrestored', () => { lost = false; schedule(); });

  function resize() {
    const { clientWidth: w, clientHeight: h } = canvas;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(canvas);
  resize();

  let busy = 0;
  let target = 0;
  let burst = 0;
  const clock = new THREE.Clock();

  function schedule() {
    if (pending || paused || lost) return;
    pending = true;
    requestAnimationFrame(frame);
  }

  function frame() {
    pending = false;
    if (paused || lost) return;
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;
    busy += (target - busy) * Math.min(1, dt * 3);
    burst *= Math.pow(0.15, dt);
    const motion = reduced ? 0.15 : 1;
    const speed = (1 + busy * 6 + burst * 10) * motion;

    const view = getView();
    camera.position.x += ((-view.x / 220) + pointer.x * 1.2 - camera.position.x) * Math.min(1, dt * 4);
    camera.position.y += ((view.y / 220) - pointer.y * 0.8 - camera.position.y) * Math.min(1, dt * 4);
    camera.position.z += ((30 / Math.pow(view.z, 0.35)) - camera.position.z) * Math.min(1, dt * 4);
    camera.lookAt(camera.position.x * 0.6, camera.position.y * 0.6, -12);

    for (const item of objects) {
      item.mesh.rotation.x += item.spin.x * dt * speed;
      item.mesh.rotation.y += item.spin.y * dt * speed;
      item.mesh.rotation.z += item.spin.z * dt * speed;
      item.orbit += dt * 0.25 * busy * motion;
      const swirl = busy * 3;
      item.mesh.position.set(
        item.home.x + Math.cos(item.orbit) * swirl,
        item.home.y + Math.sin(t * 0.6 * motion + item.bob) * 0.6 + Math.sin(item.orbit) * swirl,
        item.home.z + burst * 8,
      );
    }
    renderer.render(scene, camera);
    schedule();
  }
  schedule();

  return {
    setBusy(on) { target = on ? 1 : 0; },
    celebrate() { burst = 1; },
    setPaused(on) {
      paused = on;
      if (!on) { clock.getDelta(); schedule(); }
    },
  };
}
