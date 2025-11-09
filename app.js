// app.js
// Requires papaparse (included via CDN in index.html)

// Enhanced README injection with more professional content
const README_TEXT = `🎓 Study-Time Predictor

Faculty aim to estimate daily study time for each student to provide better mentoring and academic support.

📊 Project Objective:
Develop an advanced regression model to predict student study time using survey data. The model uses the number of books read in the past year as a proxy for study hours, enabling targeted mentorship allocation for students who may need additional academic support.

🔍 Key Features:
• Client-side k-Nearest Neighbors (k-NN) algorithm implementation
• Real-time prediction with weighted distance calculation
• Genre-based similarity matching with configurable penalties
• Interactive dataset preview and visualization
• Responsive design with modern UI/UX

📈 Model Inputs:
- screen_time_movies_series_hours_per_week: Weekly screen time in hours
- book_genre_top1: Primary book genre preference
- Additional numeric features (optional)

🎯 Output: Predicted reads_books value (study time proxy)`;

// DOM hooks
const readmeEl = document.getElementById('readme-content');
const fileInput = document.getElementById('file-input');
const loadStatus = document.getElementById('load-status');
const tableWrap = document.getElementById('table-wrap');
const predictBtn = document.getElementById('predict-btn');
const predResult = document.getElementById('prediction-result');

// Initialize UI
readmeEl.innerHTML = README_TEXT.replace(/\n/g, '<br>');

// dataset array
let dataset = []; // each row: {reads_books: Number, book_genre_top1: String, screen_time: Number, other: Number}

// function: try to auto load ./Test Data.csv
function tryAutoLoad() {
  loadStatus.textContent = '🔄 Loading dataset...';
  const path = './Test Data.csv';
  fetch(path).then(r => {
    if(!r.ok) throw new Error('not found');
    return r.text();
  }).then(csv => {
    parseAndLoad(csv);
    loadStatus.textContent = '✅ Dataset loaded successfully!';
    loadStatus.style.color = '#00d4ff';
  }).catch(err => {
    loadStatus.textContent = '⚠️ Auto-load failed. Please upload a CSV file manually.';
    loadStatus.style.color = '#ff6b6b';
  });
}

// PapaParse parse -> populate dataset and show preview
function parseAndLoad(csvString) {
  const parsed = Papa.parse(csvString, {header:true, skipEmptyLines:true});
  const rows = parsed.data;

  // Normalize header names: trim, remove newlines, and lowercase for matching
  const normalizedHeaders = {};
  for (const key in rows[0] || {}) {
    const normalized = key.replace(/\n/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
    normalizedHeaders[normalized] = key;
  }

  dataset = [];
  for (const r of rows) {
    // Map using normalized headers
    const readsKey = normalizedHeaders['books read past year provide in integer value between (0-50)'] ||
                     normalizedHeaders['books read past year'] ||
                     normalizedHeaders['reads books'] ||
                     normalizedHeaders['reads_books'] ||
                     normalizedHeaders['reads'];
    const genreKey = normalizedHeaders['book genre top 1'] ||
                     normalizedHeaders['book_genre_top1'] ||
                     normalizedHeaders['book_genre'] ||
                     normalizedHeaders['genre'];
    const screenKey = normalizedHeaders['screen time movies/series in hours per week (provide value between 0-40)'] ||
                      normalizedHeaders['screen time movies/series in hours per week'] ||
                      normalizedHeaders['screen_time_movies_series_hours_per_week'] ||
                      normalizedHeaders['screen_time'] ||
                      normalizedHeaders['screen'];
    const otherKey = normalizedHeaders['gaming hours per week (provide values in integer between 0-50)'] ||
                     normalizedHeaders['gaming hours per week'] ||
                     normalizedHeaders['gaming_hours_per_week'] ||
                     normalizedHeaders['other_numeric'] ||
                     normalizedHeaders['other'];

    const reads = toNumber(r[readsKey] ?? 0);
    const genre = (r[genreKey] ?? '').trim().toLowerCase();
    const screen = toNumber(r[screenKey] ?? 0);
    const other = toNumber(r[otherKey] ?? 0);

    // Only include rows with valid reads_books (numeric and >= 0) and non-empty genre
    if (!Number.isNaN(reads) && reads >= 0 && genre !== '') {
      dataset.push({
        reads_books: reads,
        book_genre_top1: genre,
        screen_time: screen,
        other: other
      });
    }
  }
  loadStatus.textContent = `📊 Loaded ${dataset.length} data points successfully!`;
  loadStatus.style.color = '#00d4ff';
  renderTablePreview();
}

function toNumber(v){
  if(v === undefined || v === null || v === '') return NaN;
  const n = Number(String(v).replace(/,/g,''));
  return Number.isFinite(n) ? n : NaN;
}

function renderTablePreview() {
  if (!dataset.length) {
    tableWrap.innerHTML = '<div style="text-align: center; padding: 40px; color: #b0b0b0;"><i class="fas fa-database" style="font-size: 3rem; margin-bottom: 20px;"></i><br>No dataset loaded yet.</div>';
    return;
  }
  const columns = ['reads_books','book_genre_top1','screen_time','other'];
  let html = '<table><thead><tr>' + columns.map(c=>`<th>${c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</th>`).join('') + '</tr></thead><tbody>';
  const max = Math.min(dataset.length, 50);
  for (let i=0;i<max;i++){
    const row = dataset[i];
    html += '<tr>' + columns.map(c=>`<td>${row[c] ?? '-'}</td>`).join('') + '</tr>';
  }
  html += '</tbody></table>';
  if (dataset.length > 50) {
    html += `<div style="text-align: center; margin-top: 15px; color: #b0b0b0; font-size: 0.9rem;">Showing first 50 of ${dataset.length} rows</div>`;
  }
  tableWrap.innerHTML = html;
}

// k-NN predictor (k=5), using numeric features: screen_time and other, and genre penalty
function predictUsingKNN(query, k=5) {
  if (!dataset.length) return {error:'No dataset loaded.'};
  if (!query.book_genre_top1?.trim()) return {error: 'Book genre is required'};
  if (Number.isNaN(query.screen_time)) return {error: 'Screen time must be a number'};
  if (Number.isNaN(query.other)) return {error: 'Other numeric feature must be a number'};

  const points = [];
  for (const row of dataset) {
    if (row.reads_books === null || row.reads_books === undefined || Number.isNaN(row.reads_books)) continue;

    // distance: Euclidean on numeric features
    const a = Number.isFinite(row.screen_time) ? row.screen_time : 0;
    const b = Number.isFinite(row.other) ? row.other : 0;
    const qa = Number.isFinite(query.screen_time) ? query.screen_time : 0;
    const qb = Number.isFinite(query.other) ? query.other : 0;
    let dist = Math.hypot(a-qa, b-qb);

    // genre penalty if mismatch
    const queryGenre = query.book_genre_top1.trim().toLowerCase();
    const rowGenre = (row.book_genre_top1 || '').trim().toLowerCase();
    if (queryGenre && rowGenre) {
      if (queryGenre !== rowGenre) {
        dist += 3.0; // genre mismatch penalty (tweakable)
      }
    } else {
      dist += 1.5;
    }
    points.push({dist, reads_books: row.reads_books, row});
  }

  if (points.length < k) return {error: `Not enough valid data points. Need at least ${k}, found ${points.length}`};

  points.sort((x,y)=>x.dist - y.dist);
  const neighbors = points.slice(0,k);

  // compute weighted average inversely proportional to distance (plus epsilon)
  const eps = 1e-6;
  let wsum = 0, val = 0;
  for (const n of neighbors) {
    const w = 1 / (n.dist + eps);
    if (!Number.isFinite(n.reads_books)) continue;
    val += n.reads_books * w;
    wsum += w;
  }
  const pred = wsum ? val / wsum : NaN;
  return {prediction: pred, neighbors};
}

// UI handlers
fileInput.addEventListener('change', (ev) => {
  const f = ev.target.files[0];
  if(!f) return;
  loadStatus.textContent = '🔄 Processing uploaded file...';
  const reader = new FileReader();
  reader.onload = () => {
    parseAndLoad(reader.result);
    loadStatus.textContent = '✅ File uploaded and processed successfully!';
    loadStatus.style.color = '#00d4ff';
  };
  reader.readAsText(f);
});

predictBtn.addEventListener('click', () => {
  if (!dataset.length) {
    predResult.innerHTML = '<div style="text-align: center; color: #ff6b6b;"><i class="fas fa-exclamation-triangle"></i> No dataset loaded. Please load a dataset first.</div>';
    return;
  }

  // Validate inputs
  const screenTimeInput = document.getElementById('input-screen-time').value;
  const genreInput = document.getElementById('input-genre').value;
  const otherInput = document.getElementById('input-other').value;

  const screenTime = toNumber(screenTimeInput);
  const genre = genreInput.trim();
  const other = toNumber(otherInput) || 0; // Optional, defaults to 0

  if (screenTimeInput === '' || isNaN(screenTime) || screenTime < 0) {
    predResult.innerHTML = '<div style="text-align: center; color: #ff6b6b;"><i class="fas fa-exclamation-circle"></i> Please enter a valid screen time (non-negative number).</div>';
    return;
  }

  if (!genre) {
    predResult.innerHTML = '<div style="text-align: center; color: #ff6b6b;"><i class="fas fa-exclamation-circle"></i> Please select a book genre.</div>';
    return;
  }

  const query = {
    screen_time: screenTime,
    book_genre_top1: genre,
    other: other
  };

  const out = predictUsingKNN(query, 5);
  if (out.error) {
    predResult.innerHTML = `<div style="text-align: center; color: #ff6b6b;"><i class="fas fa-times-circle"></i> ${out.error}</div>`;
    return;
  }

  const pred = Number.isFinite(out.prediction) ? out.prediction.toFixed(2) : 'N/A';
  let html = `<div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #00d4ff; margin-bottom: 10px;"><i class="fas fa-chart-line"></i> Prediction Result</h3>
                <div style="font-size: 2rem; font-weight: bold; color: #00d4ff; margin: 20px 0;">
                  ${pred} <span style="font-size: 1rem; font-weight: normal;">books/year</span>
                </div>
                <p style="color: #b0b0b0; font-size: 0.9rem;">Estimated study time proxy (weighted k=5 nearest neighbors)</p>
              </div>`;

  html += '<h4 style="color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 10px;"><i class="fas fa-users"></i> Nearest Neighbors Analysis</h4>';
  html += '<div style="overflow-x: auto;"><table style="width:100%; border-collapse: collapse;">';
  html += '<thead><tr style="background: rgba(0, 212, 255, 0.1);"><th style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">Distance</th><th style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">Books Read</th><th style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">Genre</th><th style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">Screen Time</th><th style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">Gaming Hours</th></tr></thead><tbody>';

  for(const n of out.neighbors) {
    html += `<tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
               <td style="padding: 10px; text-align: center;">${n.dist.toFixed(3)}</td>
               <td style="padding: 10px; text-align: center; font-weight: bold;">${n.reads_books ?? '-'}</td>
               <td style="padding: 10px; text-align: center;">${n.row.book_genre_top1 ?? '-'}</td>
               <td style="padding: 10px; text-align: center;">${n.row.screen_time ?? '-'}</td>
               <td style="padding: 10px; text-align: center;">${n.row.other ?? '-'}</td>
             </tr>`;
  }
  html += '</tbody></table></div>';
  predResult.innerHTML = html;
});

// attempt to auto load existing Test Data.csv in same folder
tryAutoLoad();
