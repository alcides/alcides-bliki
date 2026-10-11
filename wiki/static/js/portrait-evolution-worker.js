/* Ten-member, elitist genetic algorithm. Fitness is grayscale pixel MSE. */
const SIZE = 48, POPULATION = 10, TRIANGLES = 100;
let target, population, generation = 0, timer;
const surface = new OffscreenCanvas(SIZE, SIZE);
const ctx = surface.getContext('2d', {willReadFrequently: true});
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
function triangle() {
  const x = Math.random() * SIZE, y = Math.random() * SIZE;
  const radius = 3 + Math.random() * 25;
  return {vertices: Array.from({length: 6}, (_, i) => (i % 2 ? y : x) + (Math.random() - .5) * radius * 2), tone: Math.random() * 255, alpha: .25 + Math.random() * .65};
}
function evaluate(genes) {
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, SIZE, SIZE);
  for (const g of genes) {
    ctx.fillStyle = `rgba(${g.tone},${g.tone},${g.tone},${g.alpha})`;
    ctx.beginPath();ctx.moveTo(g.vertices[0],g.vertices[1]);
    ctx.lineTo(g.vertices[2],g.vertices[3]);ctx.lineTo(g.vertices[4],g.vertices[5]);ctx.closePath();ctx.fill();
  }
  const pixels = ctx.getImageData(0, 0, SIZE, SIZE).data;
  let error = 0;
  for (let i = 0; i < target.length; i++) error += (pixels[i * 4] - target[i]) ** 2;
  return {genes, error: error / target.length};
}
function parent() {
  const a = population[Math.floor(Math.random() * POPULATION)];
  const b = population[Math.floor(Math.random() * POPULATION)];
  return a.error < b.error ? a : b;
}
function breed() {
  const a = parent(), b = parent();
  // Mostly inherit one parent to avoid disrupting overlapping triangle layers.
  const genes = a.genes.map((g, i) => {
    const source = Math.random() < .08 ? b.genes[i] : g;
    return {...source, vertices: source.vertices.slice()};
  });
  const count = 1 + Math.floor(Math.random() * 4);
  for (let i = 0; i < count; i++) {
    const index = Math.floor(Math.random() * TRIANGLES), g = genes[index];
    if (Math.random() < .08) {genes[index] = triangle(); continue;}
    if (Math.random() < .65) {
      const coordinate = Math.floor(Math.random() * 6);
      g.vertices[coordinate] = clamp(g.vertices[coordinate] + (Math.random() - .5) * 10, -SIZE / 2, SIZE * 1.5);
    } else g.tone = clamp(g.tone + (Math.random() - .5) * 65, 0, 255);
    g.alpha = clamp(g.alpha + (Math.random() - .5) * .15, .1, 1);
  }
  return evaluate(genes);
}
function publish() {
  postMessage({genes: population[0].genes, error: population[0].error, generation, population: POPULATION, size: SIZE});
}
function evolve() {
  const next = population.slice(0, 2); // Preserve the best: fitness cannot regress.
  while (next.length < POPULATION) next.push(breed());
  population = next.sort((a,b) => a.error - b.error);
  generation++;
  if (generation % 4 === 0) publish();
}
onmessage = ({data}) => {
  if (data.type === 'init') {
    target = data.target;
    population = Array.from({length: POPULATION}, () => evaluate(Array.from({length: TRIANGLES}, triangle))).sort((a,b)=>a.error-b.error);
    publish();
  } else if (data.type === 'run') {
    clearInterval(timer);
    if (data.running && population) timer = setInterval(evolve, 35);
  }
};
