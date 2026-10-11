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
  document.querySelectorAll('nav a').forEach(a=>{
    if (a.pathname === location.pathname || (a.pathname !== '/' && location.pathname.startsWith(a.pathname))) a.setAttribute('aria-current','page');
  });
  const canvas = document.getElementById('research-particles');
  if (!canvas) return;
  const context = canvas.getContext('2d');
  if (!context) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let width = 0, height = 0, best, visible = true, worker, ready = false;
  function draw() {
    context.clearRect(0, 0, width, height);
    if (!best) return;
    const mobile = width < 700;
    const side = Math.max(height * 1.25, mobile ? width * 1.1 : Math.min(width * .55, 650));
    const x = mobile ? width - side * .85 : width - side;
    const y = (height - side) / 2;
    const dark = root.dataset.theme === 'dark';
    context.save();context.translate(x, y);context.scale(side / best.size, side / best.size);
    context.beginPath();context.rect(0,0,best.size,best.size);context.clip();
    context.fillStyle = dark ? '#f3ce42' : '#fff8f1';
    context.fillRect(0,0,best.size,best.size);
    for (const g of best.genes) {
      const t = g.tone / 255;
      const low = dark ? [0,0,0] : [110,38,0];
      const high = dark ? [243,206,66] : [255,248,241];
      const color = low.map((v,i)=>Math.round(v+(high[i]-v)*t));
      context.fillStyle = `rgba(${color.join(',')},${g.alpha})`;
      context.beginPath();context.moveTo(g.vertices[0],g.vertices[1]);
      context.lineTo(g.vertices[2],g.vertices[3]);context.lineTo(g.vertices[4],g.vertices[5]);context.closePath();context.fill();
    }
    context.restore();
    // Fade the portrait into the banner, without a visible rectangular frame.
    context.save();context.globalCompositeOperation = 'destination-in';
    const fade = context.createLinearGradient(0,0,width,0);
    fade.addColorStop(0,'rgba(0,0,0,0)');
    fade.addColorStop(mobile ? .25 : Math.max(.42, Math.min(.68, x / width + .04)),'rgba(0,0,0,0)');
    fade.addColorStop(mobile ? .75 : .72, mobile ? 'rgba(0,0,0,.16)' : 'rgba(0,0,0,.28)');
    fade.addColorStop(1,mobile ? 'rgba(0,0,0,.22)' : 'rgba(0,0,0,.42)');
    context.fillStyle=fade;context.fillRect(0,0,width,height);context.restore();
  }
  function resize() {
    width = canvas.clientWidth;height = canvas.clientHeight;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = width * ratio;canvas.height = height * ratio;
    context.setTransform(ratio,0,0,ratio,0,0);draw();
  }
  function sync() {
    if (ready) worker.postMessage({type: 'run', running: visible && !document.hidden && !reduced.matches});
  }
  reduced.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;sync();}).observe(canvas);
  new ResizeObserver(resize).observe(canvas);
  new MutationObserver(draw).observe(root,{attributes:true,attributeFilter:['data-theme']});
  const photo = new Image();
  photo.onload = () => {
    const targetCanvas = document.createElement('canvas');targetCanvas.width=48;targetCanvas.height=48;
    const targetContext = targetCanvas.getContext('2d',{willReadFrequently:true});
    // Match the square, centered crop used by the corner portrait.
    const side = Math.min(photo.naturalWidth,photo.naturalHeight);
    targetContext.drawImage(photo,(photo.naturalWidth-side)/2,(photo.naturalHeight-side)/2,side,side,0,0,48,48);
    const pixels=targetContext.getImageData(0,0,48,48).data;
    const target=Float32Array.from({length:48*48},(_,i)=>.2126*pixels[i*4]+.7152*pixels[i*4+1]+.0722*pixels[i*4+2]);
    worker = new Worker(new URL('portrait-evolution-worker.js',document.querySelector('script[src*="research-particles.js"]').src));
    worker.onmessage=({data})=>{
      best=data;canvas.dataset.generation=data.generation;canvas.dataset.error=data.error;canvas.dataset.population=data.population;
      draw();if (!ready) {ready=true;sync();}
    };
    worker.postMessage({type:'init',target},[target.buffer]);
  };
  photo.src=document.querySelector('header img.photo').src;
  window.addEventListener('pagehide',()=>worker?.postMessage({type:'run',running:false}));
  window.addEventListener('pageshow',sync);
  resize();
})();
