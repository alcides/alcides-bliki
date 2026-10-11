(() => {
  // Older pages store icon lists as one paragraph with line breaks.
  document.querySelectorAll('.entry-content p').forEach(paragraph => {
    const nodes = [...paragraph.childNodes];
    const rows = [[]];
    for (const node of nodes) {
      if (node.nodeName === 'BR') rows.push([]);
      else rows[rows.length - 1].push(node);
    }
    const iconSelector = 'img[src$="/paper.png"],img[src$="/talk.png"],img[src$="/service.png"]';
    if (rows.length < 2 || !rows.every(row => row.some(node => node.nodeType === 1 && node.matches(iconSelector)))) return;
    const list = document.createElement('ul');
    list.className = 'publication-list';
    rows.forEach(row => {
      const item = document.createElement('li');
      const text = document.createElement('span');
      row.forEach(node => {
        if (node.nodeType === 1 && node.matches(iconSelector)) item.append(node);
        else text.append(node);
      });
      item.append(text);list.append(item);
    });
    paragraph.replaceWith(list);
  });
  const root = document.documentElement;
  const themeButton = document.querySelector('.theme-toggle');
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  let explicitTheme = false;
  try { explicitTheme = ['light', 'dark'].includes(localStorage.getItem('research-theme')); } catch (_) {}
  function updateTheme(theme) {
    root.dataset.theme = theme;
    const label = theme === 'dark' ? 'Light mode' : 'Dark mode';
    themeButton.textContent = label;
    themeButton.setAttribute('aria-label', 'Switch to ' + label.toLowerCase());
  }
  themeButton.hidden = false;
  updateTheme(root.dataset.theme || (systemTheme.matches ? 'dark' : 'light'));
  themeButton.addEventListener('click', () => {
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    explicitTheme = true;
    try { localStorage.setItem('research-theme', theme); } catch (_) {}
    updateTheme(theme);
  });
  systemTheme.addEventListener('change', () => {
    if (!explicitTheme) updateTheme(systemTheme.matches ? 'dark' : 'light');
  });
  const canvas = document.getElementById('research-particles');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  if (!context) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let width, height, points = [], frame, last = 0, paused = reduced.matches;
  let visible = true;
  function resize() {
    width = canvas.clientWidth; height = canvas.clientHeight;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = width * ratio; canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    points = Array.from({length: width < 600 ? 34 : 65}, () => ({
      x: Math.random() * width, y: Math.random() * height,
      vx: (Math.random() - .5) * 18, vy: (Math.random() - .5) * 18,
      radius: Math.random() * 1.5 + 1.2
    }));
    draw(0);
  }
  function draw(delta) {
    context.clearRect(0, 0, width, height);
    const color = getComputedStyle(root).getPropertyValue('--particle-rgb').trim();
    for (const p of points) {
      p.x = (p.x + p.vx * delta + width) % width;
      p.y = (p.y + p.vy * delta + height) % height;
      // Keep the constellation faint behind the copy.
      const opacity = p.x < width * .55 ? .24 : .7;
      context.fillStyle = `rgba(${color},${opacity})`;
      context.beginPath(); context.arc(p.x,p.y,p.radius,0,Math.PI*2); context.fill();
      for (const q of points) {
        if (q === p) break;
        const d = Math.hypot(p.x-q.x,p.y-q.y);
        if (d < 145) {
          context.strokeStyle = `rgba(${color},${(1-d/145)*opacity*.55})`;
          context.beginPath(); context.moveTo(p.x,p.y); context.lineTo(q.x,q.y); context.stroke();
        }
      }
    }
  }
  function tick(time) {
    draw(last ? Math.min((time-last)/1000,.05) : 0); last=time;
    frame=requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame);last=0;
    if (!paused && visible && !document.hidden) frame=requestAnimationFrame(tick);
  }
  reduced.addEventListener('change',()=>{paused=reduced.matches;sync();});
  document.addEventListener('visibilitychange',sync);
  new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;sync();}).observe(canvas);
  new ResizeObserver(resize).observe(canvas);
  document.querySelectorAll('nav a').forEach(a=>{
    if (a.pathname === location.pathname || (a.pathname !== '/' && location.pathname.startsWith(a.pathname))) a.setAttribute('aria-current','page');
  });
  new MutationObserver(() => draw(0)).observe(root, {attributes: true, attributeFilter: ['data-theme']});
  resize();sync();
})();
