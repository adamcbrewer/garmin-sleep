const STAGE_COLORS = {
  0: { name: 'Deep', color: '#2563eb', bright: '#3b82f6' },
  1: { name: 'Light', color: '#5b9bd5', bright: '#7cc4f5' },
  2: { name: 'REM', color: '#c45a8a', bright: '#f472b6' },
  3: { name: 'Awake', color: '#d4a54a', bright: '#fbbf24' },
  '-1': { name: 'Unmeasurable', color: '#3a3a4a', bright: '#5a5a6a' },
};

const STAGE_ORDER = [0, 1, 2, 3];

function stageColor(level, bright = false) {
  const s = STAGE_COLORS[level] || STAGE_COLORS[1];
  return bright ? s.bright : s.color;
}

function stageName(level) {
  return (STAGE_COLORS[level] || STAGE_COLORS[1]).name;
}

function formatHour(h) {
  const hour = Math.floor(h) % 24;
  const min = Math.round((h % 1) * 60);
  const ampm = hour >= 12 ? 'pm' : 'am';
  const h12 = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return min === 0 ? `${h12}${ampm}` : `${h12}:${String(min).padStart(2, '0')}${ampm}`;
}

function formatDuration(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.round((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}

function formatDateLong(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
}

async function loadData(filename) {
  const resp = await fetch(`../data/${filename}`);
  if (!resp.ok) throw new Error(`Failed to load ${filename}`);
  return resp.json();
}

function createSVG(container, width, height, margin) {
  const svg = d3.select(container)
    .append('svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('width', '100%')
    .attr('preserveAspectRatio', 'xMidYMid meet');

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  return { svg, g, innerWidth, innerHeight };
}

function createTooltip(container) {
  const tip = document.createElement('div');
  tip.className = 'tooltip';
  (container || document.body).appendChild(tip);

  return {
    el: tip,
    show(html, x, y) {
      tip.innerHTML = html;
      tip.classList.add('visible');
      const rect = tip.getBoundingClientRect();
      const parentRect = (container || document.body).getBoundingClientRect();
      let left = x - rect.width / 2;
      let top = y - rect.height - 12;
      if (left < 4) left = 4;
      if (left + rect.width > parentRect.width - 4) left = parentRect.width - rect.width - 4;
      if (top < 4) top = y + 16;
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
    },
    hide() {
      tip.classList.remove('visible');
    }
  };
}

function sleepStageScale() {
  return d3.scaleOrdinal()
    .domain([0, 1, 2, 3, -1])
    .range(['#2563eb', '#5b9bd5', '#c45a8a', '#d4a54a', '#3a3a4a']);
}

function makeLegend(container, stages = STAGE_ORDER) {
  const legend = document.createElement('div');
  legend.className = 'legend';
  stages.forEach(s => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    const dot = document.createElement('span');
    dot.className = 'legend-dot';
    dot.style.background = stageColor(s);
    item.appendChild(dot);
    item.appendChild(document.createTextNode(stageName(s)));
    legend.appendChild(item);
  });
  container.appendChild(legend);
}

function pageShell(title, subtitle, category) {
  document.title = `${title} — Sleep Viz`;
  return `
    <div class="page">
      <nav class="nav">
        <a href="../index.html" class="nav-back">
          <svg viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          All Visualizations
        </a>
        <span class="nav-category">${category}</span>
      </nav>
      <h1>${title}</h1>
      <p class="subtitle">${subtitle}</p>
      <div id="viz-root"></div>
    </div>
  `;
}
