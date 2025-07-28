import React, { useState } from "react";
import "../App.css";

const baseSigns = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
];

const planetColors: Record<string, string> = {
  Su: "#FFD700", // Sun - gold
  Mo: "#FFF",    // Moon - white
  Ma: "#FF3333", // Mars - red
  Me: "#00BFFF", // Mercury - blue
  Ju: "#FFA500", // Jupiter - orange
  Ve: "#FF69B4", // Venus - pink
  Sa: "#c3924f", // Saturn - dark brown
  Ra: "#CBC3E3", // Rahu - light purple
  Ke: "#888",    // Ketu - gray
  Ur: "#90ee90", // Uranus - light green
  Ne: "#00ffff", // Neptune - aqua
  Pl: "#a0522d", // Pluto - brown
};

const statusSymbols: Record<string, string> = {
  exalted: "↑",
  debilitated: "↓",
  combust: "🔥",
  retrograde: "℞",
  peak: "★"
};

const statusLabels: Record<string, string> = {
  exalted: "Exalted (↑)",
  debilitated: "Debilitated (↓)",
  combust: "Combust (🔥)",
  retrograde: "Retrograde (℞)",
  peak: "Peak (★)"
};

// North Indian chart: 12 house positions (x, y) for a 700x700 square
const houseCenters = [
  { x: 350, y: 160},   // 1 (top middle)
  { x: 200, y: 100},  // 2 (top left)
  { x: 100,  y: 180 },  // 3 (left top)
  { x: 200, y: 300},  // 4 (left bottom)
  { x: 100,  y: 470 }, // 5 (bottom middle)
  { x: 200, y: 570 }, // 6 (bottom right)
  { x: 350, y: 460 }, // 7 (right bottom)
  { x: 500, y: 570 }, // 8 (right top)
  { x: 600, y: 470 }, // 9 (top right inside)
  { x: 500, y: 300 }, // 10 (top left inside)
  { x: 600, y: 180 }, // 11 (bottom left inside)
  { x: 500, y: 100 }, // 12 (bottom right inside)
];

// Each house's diamond vertices (for clickable area)
const housePolygons = [
  // These are rough, you can adjust for your grid
  [ {x:350,y:50}, {x:390,y:130}, {x:350,y:170}, {x:310,y:130} ], // 1
  [ {x:310,y:130}, {x:350,y:170}, {x:230,y:220}, {x:170,y:140} ], // 2
  [ {x:170,y:140}, {x:230,y:220}, {x:130,y:310}, {x:90,y:350} ], // 3
  [ {x:90,y:350}, {x:130,y:310}, {x:250,y:470}, {x:140,y:530} ], // 4
  [ {x:140,y:530}, {x:250,y:470}, {x:350,y:650}, {x:350,y:610} ], // 5
  [ {x:350,y:610}, {x:350,y:650}, {x:470,y:570}, {x:530,y:560} ], // 6
  [ {x:530,y:560}, {x:470,y:570}, {x:610,y:390}, {x:610,y:350} ], // 7
  [ {x:610,y:350}, {x:610,y:390}, {x:570,y:270}, {x:560,y:170} ], // 8
  [ {x:560,y:170}, {x:570,y:270}, {x:470,y:200}, {x:390,y:130} ], // 9
  [ {x:390,y:130}, {x:470,y:200}, {x:350,y:170}, {x:350,y:130} ], // 10
  [ {x:350,y:170}, {x:470,y:450}, {x:250,y:470}, {x:230,y:220} ], // 11
  [ {x:470,y:200}, {x:570,y:270}, {x:470,y:450}, {x:470,y:200} ], // 12
];

function rotateArray<T>(arr: T[], start: string): T[] {
  const idx = arr.indexOf(start as any);
  if (idx === -1) return arr;
  return [...arr.slice(idx), ...arr.slice(0, idx)];
}

const houseOrder = [1,2,3,4,5,6,7,8,9,10,11,12];

// Aspect rules and nature
const aspectRules: Record<string, number[]> = {
  Su: [7],
  Mo: [7],
  Ma: [4, 7, 8],
  Me: [7],
  Ju: [5, 7, 9],
  Ve: [7],
  Sa: [3, 7, 10],
  Ra: [5, 7, 9],
  Ke: [5, 7, 9],
  Ur: [7],
  Ne: [7],
  Pl: [7],
};
const planetNature: Record<string, 'benefic'|'malefic'|'neutral'> = {
  Su: 'malefic',
  Mo: 'benefic',
  Ma: 'malefic',
  Me: 'benefic', // Mercury is benefic unless with malefics
  Ju: 'benefic',
  Ve: 'benefic',
  Sa: 'malefic',
  Ra: 'malefic',
  Ke: 'malefic',
  Ur: 'malefic',
  Ne: 'malefic',
  Pl: 'malefic',
};
const aspectTypeLabel: Record<number, string> = {
  3: '3rd', 4: '4th', 5: '5th', 7: '7th', 8: '8th', 9: '9th', 10: '10th'
};

// Calculate aspects for all planets
function getAspects(signPlanets: Record<string, any[]>, signs: string[]) {
  const aspects: any[] = [];
  // Map sign to house number (1-based)
  const signToHouse: Record<string, number> = {};
  signs.forEach((sign, i) => { signToHouse[sign] = i + 1; });
  Object.entries(signPlanets).forEach(([sign, planets]) => {
    const fromHouse = signToHouse[sign];
    planets.forEach((p: any) => {
      const rules = aspectRules[p.name] || [];
      rules.forEach(offset => {
        const toHouse = ((fromHouse + offset - 1) % 12) + 1;
        aspects.push({
          planet: p.name,
          fromHouse,
          toHouse,
          aspectType: aspectTypeLabel[offset] || `${offset}th`,
          nature: planetNature[p.name] || 'neutral',
          color: planetColors[p.name] || '#fff',
        });
      });
    });
  });
  return aspects;
}

const allPlanets = [
  'Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'Ur', 'Ne', 'Pl'
];
const planetLabels: Record<string, string> = {
  Su: 'Sun', Mo: 'Moon', Ma: 'Mars', Me: 'Mercury', Ju: 'Jupiter', Ve: 'Venus',
  Sa: 'Saturn', Ra: 'Rahu', Ke: 'Ketu', Ur: 'Uranus', Ne: 'Neptune', Pl: 'Pluto'
};

const KundliFace: React.FC = () => {
  const [showChart, setShowChart] = useState(false);
  const [form, setForm] = useState({
    date: "1998-05-06",
    time: "09:20",
    lat: 30.7167,
    lon: 76.8833,
    tz: 5.5,
  });
  const [signPlanets, setSignPlanets] = useState<Record<string, any[]>>({
    Aries: [], Taurus: [], Gemini: [], Cancer: [], Leo: [], Virgo: [],
    Libra: [], Scorpio: [], Sagittarius: [], Capricorn: [], Aquarius: [], Pisces: []
  });
  const [ascSign, setAscSign] = useState<string>("Aries");
  const [houseDescriptions, setHouseDescriptions] = useState<Record<number, string>>({});
  const [modal, setModal] = useState<{open: boolean, house: number|null}>({open: false, house: null});
  // Aspect tooltip and selection
  const [aspectTooltip, setAspectTooltip] = React.useState<{x:number, y:number, text:string}|null>(null);
  const [selectedAspect, setSelectedAspect] = React.useState<number|null>(null);
  const [selectedPlanets, setSelectedPlanets] = useState<string[]>(allPlanets);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === "number" ? parseFloat(value) : value
    }));
  };

  const handleSlider = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(f => ({ ...f, tz: parseFloat(e.target.value) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Call backend
    const res = await fetch("http://localhost:5000/api/kundli", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    });
    const data = await res.json();
    setSignPlanets(data.sign_planets);
    setAscSign(data.asc_sign);
    setHouseDescriptions(data.house_descriptions);
    setShowChart(true);
  };

  // Rotate signs so ascSign is always at house 1 (top)
  const signs = rotateArray(baseSigns, ascSign);

  // Outer square corners
  const S = 700;
  const margin = 50;
  const corners = [
    { x: margin, y: margin }, // top-left
    { x: S - margin, y: margin }, // top-right
    { x: S - margin, y: S - margin }, // bottom-right
    { x: margin, y: S - margin }, // bottom-left
  ];
  // Diamond (inner square) corners (midpoints of outer square sides)
  const diamond = [
    { x: S / 2, y: margin }, // top
    { x: S - margin, y: S / 2 }, // right
    { x: S / 2, y: S - margin }, // bottom
    { x: margin, y: S / 2 }, // left
  ];

  // Show all aspects
  const aspects = getAspects(signPlanets, signs).filter(a => selectedPlanets.includes(a.planet));

  // For house modal: aspects to this house
  const aspectsToHouse = modal.open && modal.house
    ? aspects.filter(a => a.toHouse === modal.house)
    : [];

  // Mouse position for tooltip
  const svgRef = React.useRef<SVGSVGElement>(null);
  const [mousePos, setMousePos] = React.useState<{x:number, y:number}|null>(null);

  // Modal for house description
  const HouseModal = () => {
    if (!modal.open || modal.house == null) return null;
    const houseIdx = modal.house - 1;
    const sign = signs[houseIdx];
    const planets = signPlanets[sign] || [];
    return (
      <div className="kundli-modal-bg" onClick={()=>setModal({open:false,house:null})}>
        <div className="kundli-modal" onClick={e=>e.stopPropagation()}>
          <h3>House {modal.house}</h3>
          <div style={{marginBottom:8}}><b>Sign:</b> {sign}</div>
          <div style={{marginBottom:8}}><b>Description:</b> {houseDescriptions[modal.house]}</div>
          <div style={{marginBottom:8}}>
            <b>Planets:</b>
            {planets.length === 0 ? (
              <div style={{color:'#aaa'}}>None</div>
            ) : (
              <ul style={{listStyle:'none',padding:0,margin:0}}>
                {planets.map((p:any) => (
                  <li key={p.name} style={{color: planetColors[p.name] || '#fff', fontWeight:600, marginBottom:2}}>
                    {p.name} {p.deg}°{p.status && p.status.length > 0 ? " " + p.status.map((s:string) => statusSymbols[s] || "").join("") : ""}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <button onClick={()=>setModal({open:false,house:null})}>Close</button>
        </div>
      </div>
    );
  };

  // Legend box
  const LegendBox: React.FC = () => {
    const [open, setOpen] = useState(false);
    return (
      <div className="kundli-legend-toggle-box">
        <button className="kundli-legend-btn" onClick={() => setOpen(o => !o)}>
          Legend {open ? '▲' : '▼'}
        </button>
        {open && (
          <div className="kundli-legend-box-expanded">
            <div style={{fontWeight:700, marginBottom:6}}>Legend</div>
            <div style={{fontSize:'1.1em'}}>
              <div><span style={{marginRight:6}}>↑</span>Exalted</div>
              <div><span style={{marginRight:6}}>↓</span>Debilitated</div>
              <div><span style={{marginRight:6}}>🔥</span>Combust</div>
              <div><span style={{marginRight:6}}>℞</span>Retrograde</div>
              <div><span style={{marginRight:6}}>★</span>Peak</div>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Aspect filter logic
  const handlePlanetToggle = (planet: string) => {
    setSelectedPlanets(sel =>
      sel.includes(planet) ? sel.filter(p => p !== planet) : [...sel, planet]
    );
  };
  const handleAll = () => setSelectedPlanets(allPlanets);
  const handleNone = () => setSelectedPlanets([]);

  // Remove grid overlay, update aspect lines logic
  return (
    <div className="kundli-face-container">
      <header className="kundli-header">
        <span role="img" aria-label="kundli" className="kundli-logo">🔯</span>
        <h1>Kundli Generator</h1>
        <div style={{flex:1}} />
      </header>
      <main className="kundli-main-centered" style={{position:'relative',flexDirection:'row',display:'flex',alignItems:'flex-start',justifyContent:'center'}}>
        {showChart && <LegendBox />}
        {showChart && (
          <div className="kundli-aspect-sidebar">
            <div className="kundli-aspect-sidebar-title">Aspects</div>
            <div className="kundli-aspect-sidebar-btns">
              <button onClick={handleAll}>All</button>
              <button onClick={handleNone}>None</button>
            </div>
            <div className="kundli-aspect-sidebar-list">
              {allPlanets.map(p => (
                <label key={p} style={{display:'flex',alignItems:'center',marginBottom:6,cursor:'pointer',fontWeight:600}}>
                  <input
                    type="checkbox"
                    checked={selectedPlanets.includes(p)}
                    onChange={() => handlePlanetToggle(p)}
                    style={{accentColor: planetColors[p] || '#fff',marginRight:8}}
                  />
                  <span style={{color: planetColors[p] || '#fff',marginRight:4}}>{p}</span>
                  <span style={{color:'#fff',fontWeight:400}}>{planetLabels[p]}</span>
                </label>
              ))}
            </div>
          </div>
        )}
        {!showChart ? (
          <form className="kundli-form-centered" onSubmit={handleSubmit}>
            <h2>Enter Birth Details</h2>
            <label>Date<br/><input type="date" name="date" value={form.date} onChange={handleChange} required /></label>
            <label>Time<br/><input type="time" name="time" value={form.time} onChange={handleChange} required /></label>
            <label>Latitude<br/><input type="number" name="lat" step="0.0001" value={form.lat} onChange={handleChange} required /></label>
            <label>Longitude<br/><input type="number" name="lon" step="0.0001" value={form.lon} onChange={handleChange} required /></label>
            <label style={{marginBottom:8}}>Timezone (UTC offset)
              <div style={{display:'flex',alignItems:'center',gap:8}}>
                <input type="range" name="tz" min={-12} max={14} step={0.5} value={form.tz} onChange={handleSlider} style={{flex:1}} />
                <span style={{minWidth:60}}>{form.tz >= 0 ? `UTC+${form.tz}` : `UTC${form.tz}`}</span>
              </div>
            </label>
            <button type="submit">Generate Kundli</button>
          </form>
        ) : (
          <div className="kundli-flex-responsive">
            <div className="kundli-svg-outer">
              <button className="kundli-back-btn" onClick={()=>setShowChart(false)}>&larr; Back</button>
              <svg
                ref={svgRef}
                viewBox={`0 0 ${S} ${S}`}
                className="kundli-svg-responsive"
                width="98vw"
                height="98vw"
                style={{maxWidth:800,maxHeight:800,display:'block',margin:'0 auto'}}
                onMouseMove={e => {
                  const rect = svgRef.current?.getBoundingClientRect();
                  if (rect) {
                    setMousePos({
                      x: e.clientX - rect.left,
                      y: e.clientY - rect.top
                    });
                  }
                }}
                onMouseLeave={() => setMousePos(null)}
              >
                {/* Outer square */}
                <polygon points={corners.map(pt => `${pt.x},${pt.y}`).join(" ")} fill="#23243a" stroke="#fff" strokeWidth={7} />
                {/* Inner diamond */}
                <polygon points={diamond.map(pt => `${pt.x},${pt.y}`).join(" ")} fill="none" stroke="#fff" strokeWidth={5} />
                {/* Diagonals */}
                <line x1={corners[0].x} y1={corners[0].y} x2={corners[2].x} y2={corners[2].y} stroke="#fff" strokeWidth={4} />
                <line x1={corners[1].x} y1={corners[1].y} x2={corners[3].x} y2={corners[3].y} stroke="#fff" strokeWidth={4} />
                {/* House numbers, sign names, planets */}
                {houseCenters.map((coord, i) => (
                  <g key={i} style={{cursor:'pointer'}} onClick={()=>setModal({open:true,house:i+1})}>
                    {/* House number */}
                    <text
                      x={coord.x}
                      y={coord.y - 18}
                      textAnchor="middle"
                      fontSize="16"
                      fill="#b0b0b0"
                      fontWeight="bold"
                      style={{ fontFamily: 'monospace', userSelect: 'none' }}
                    >
                      {i + 1}
                    </text>
                    {/* Sign name */}
                    <text
                      x={coord.x}
                      y={coord.y + 2}
                      textAnchor="middle"
                      fontSize="20"
                      fill="#fff"
                      fontWeight="bold"
                      style={{ fontFamily: 'monospace', userSelect: 'none' }}
                    >
                      {signs[i]}
                    </text>
                    {/* Planets in sign */}
                    {signPlanets[signs[i]] && signPlanets[signs[i]].map((p, j) => (
                      <text
                        key={p.name}
                        x={coord.x}
                        y={coord.y + 22 + j * 18}
                        textAnchor="middle"
                        fontSize="15"
                        fill={planetColors[p.name] || "#fff"}
                        fontWeight="bold"
                        style={{ fontFamily: 'monospace', userSelect: 'none' }}
                      >
                        {p.name} {p.deg}°{p.status && p.status.length > 0 ? " " + p.status.map((s:string) => statusSymbols[s] || "").join("") : ""}
                      </text>
                    ))}
                  </g>
                ))}
                {/* Aspect lines/arrows */}
                {aspects.map((asp, idx) => {
                  const fromIdx = asp.fromHouse - 1;
                  const toIdx = asp.toHouse - 1;
                  const from = houseCenters[fromIdx];
                  const to = houseCenters[toIdx];
                  const startY = from.y + 22;
                  const endY = to.y;
                  return (
                    <g key={idx} style={{pointerEvents:'auto'}}>
                      <line
                        x1={from.x} y1={startY}
                        x2={to.x} y2={endY}
                        stroke={asp.color}
                        strokeWidth={2}
                        markerEnd="url(#arrowhead)"
                        opacity={0.5}
                        style={{cursor:'pointer'}}
                        onMouseEnter={e => setAspectTooltip({x: mousePos?.x || (from.x+to.x)/2, y: mousePos?.y || (from.y+to.y)/2, text:`${asp.planet} ${asp.aspectType} aspect to House ${asp.toHouse} (${asp.nature})`})}
                        onMouseMove={e => mousePos && setAspectTooltip({x: mousePos.x, y: mousePos.y, text:`${asp.planet} ${asp.aspectType} aspect to House ${asp.toHouse} (${asp.nature})`})}
                        onMouseLeave={() => setAspectTooltip(null)}
                      />
                    </g>
                  );
                })}
                <defs>
                  <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L8,3 z" fill="#fff" />
                  </marker>
                </defs>
                {/* Aspect tooltip (follows mouse) */}
                {aspectTooltip && (
                  <foreignObject x={aspectTooltip.x-100} y={aspectTooltip.y-50} width={200} height={60} pointerEvents="none">
                    <div style={{background:'#222',color:'#fff',borderRadius:8,padding:'8px 16px',fontSize:15,opacity:0.97,border:'1.5px solid #888',textAlign:'center',minWidth:120,maxWidth:200,whiteSpace:'pre-line'}}>
                      {aspectTooltip.text}
                    </div>
                  </foreignObject>
                )}
              </svg>
              <HouseModal />
            </div>
            <div className="kundli-aspect-table-outer">
              <h3>Planetary Aspects</h3>
              <table className="kundli-aspect-table">
                <thead>
                  <tr>
                    <th>Planet</th><th>From House</th><th>To House</th><th>Aspect</th><th>Nature</th>
                  </tr>
                </thead>
                <tbody>
                  {aspects.map((asp, i) => (
                    <tr key={i}>
                      <td style={{color: asp.color, fontWeight:600}}>{asp.planet}</td>
                      <td>{asp.fromHouse}</td>
                      <td>{asp.toHouse}</td>
                      <td>{asp.aspectType}</td>
                      <td style={{color: asp.nature==='benefic'?'#0f0':asp.nature==='malefic'?'#f44':'#ff0'}}>{asp.nature}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
      {/* House modal with aspects to this house */}
      {modal.open && modal.house && (
        <div className="kundli-modal-bg" onClick={()=>setModal({open:false,house:null})}>
          <div className="kundli-modal" onClick={e=>e.stopPropagation()}>
            <h3>House {modal.house}</h3>
            <div style={{marginBottom:8}}><b>Sign:</b> {signs[modal.house-1]}</div>
            <div style={{marginBottom:8}}><b>Description:</b> {houseDescriptions[modal.house]}</div>
            <div style={{marginBottom:8}}>
              <b>Planets:</b>
              {signPlanets[signs[modal.house-1]].length === 0 ? (
                <div style={{color:'#aaa'}}>None</div>
              ) : (
                <ul style={{listStyle:'none',padding:0,margin:0}}>
                  {signPlanets[signs[modal.house-1]].map((p:any) => (
                    <li key={p.name} style={{color: planetColors[p.name] || '#fff', fontWeight:600, marginBottom:2}}>
                      {p.name} {p.deg}°{p.status && p.status.length > 0 ? " " + p.status.map((s:string) => statusSymbols[s] || "").join("") : ""}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div style={{marginBottom:8}}>
              <b>Aspected by:</b>
              {aspects.filter(a => a.toHouse === modal.house).length === 0 ? (
                <div style={{color:'#aaa'}}>None</div>
              ) : (
                <ul style={{listStyle:'none',padding:0,margin:0}}>
                  {aspects.filter(a => a.toHouse === modal.house).map((a, i) => (
                    <li key={i} style={{color: planetColors[a.planet] || '#fff', fontWeight:600, marginBottom:2}}>
                      {a.planet} ({a.aspectType}, {a.nature}) from House {a.fromHouse}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <button onClick={()=>setModal({open:false,house:null})}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default KundliFace;