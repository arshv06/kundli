import React from 'react';
import './HouseAnalysis.css';

interface Planet {
  name: string;
  deg: number;
  sign: string;
  status: string[];
}

interface HouseAnalysisProps {
  houseNumber: number;
  sign: string;
  planets: Planet[];
  aspects: Array<{
    planet: string;
    fromHouse: number;
    toHouse: number;
    aspectType: string;
    nature: string;
    color: string;
  }>;
  dataset: any;
  ascSign: string;
}

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
};

const planetNames: Record<string, string> = {
  Su: 'Sun', Mo: 'Moon', Ma: 'Mars', Me: 'Mercury', 
  Ju: 'Jupiter', Ve: 'Venus', Sa: 'Saturn', Ra: 'Rahu', Ke: 'Ketu'
};

const HouseAnalysis: React.FC<HouseAnalysisProps> = ({
  houseNumber,
  sign,
  planets,
  aspects,
  dataset,
  ascSign
}) => {
  const houseData = dataset?.houses?.[houseNumber.toString()];
  const aspectsToHouse = aspects.filter(a => a.toHouse === houseNumber);
  
  // Calculate house strength based on planets and aspects
  const calculateHouseStrength = () => {
    let strength = 0;
    let totalInfluence = 0;
    
    // Analyze planets in the house
    planets.forEach(planet => {
      const planetData = houseData?.planets[planetNames[planet.name]];
      if (planetData) {
        // Check planet status
        const isExalted = planet.status.includes('exalted');
        const isDebilitated = planet.status.includes('debilitated');
        const isCombust = planet.status.includes('combust');
        const isRetrograde = planet.status.includes('retrograde');
        
        // Base strength based on planet nature
        let planetStrength = 0;
        if (['Ju', 'Ve', 'Mo'].includes(planet.name)) {
          planetStrength = isExalted ? 2 : isDebilitated ? -1 : 1;
        } else if (['Ma', 'Sa', 'Ra', 'Ke'].includes(planet.name)) {
          planetStrength = isExalted ? 1 : isDebilitated ? -2 : -1;
        } else {
          planetStrength = isExalted ? 1.5 : isDebilitated ? -1.5 : 0;
        }
        
        // Adjust for combustion and retrograde
        if (isCombust) planetStrength *= 0.5;
        if (isRetrograde) planetStrength *= 0.8;
        
        strength += planetStrength;
        totalInfluence++;
      }
    });
    
    // Analyze aspects to the house
    aspectsToHouse.forEach(aspect => {
      const aspectStrength = aspect.nature === 'benefic' ? 0.5 : aspect.nature === 'malefic' ? -0.5 : 0;
      strength += aspectStrength;
      totalInfluence++;
    });
    
    // Normalize strength
    const avgStrength = totalInfluence > 0 ? strength / totalInfluence : 0;
    
    if (avgStrength >= 0.5) return { strength: 'strong', color: '#90EE90', label: 'Strong House' };
    if (avgStrength <= -0.5) return { strength: 'weak', color: '#FFB6C1', label: 'Challenging House' };
    return { strength: 'neutral', color: '#FFD700', label: 'Neutral House' };
  };
  
  const houseStrength = calculateHouseStrength();
  


  return (
    <div className="house-analysis">
      <div className="house-header" style={{ backgroundColor: houseStrength.color }}>
        <h3>House {houseNumber} - {sign}</h3>
        <span className="house-strength-label">{houseStrength.label}</span>
      </div>
      
      <div className="house-content">
        {/* House Description */}
        <div className="section">
          <h4>House Meaning</h4>
          <p>{houseData?.about || 'No description available'}</p>
        </div>
        
        {/* Planets in House */}
        <div className="section">
          <h4>Planets in House {houseNumber}</h4>
          {planets.length === 0 ? (
            <p className="no-planets">No planets in this house</p>
          ) : (
            <div className="planets-list">
              {planets.map((planet, index) => {
                const planetData = houseData?.planets[planetNames[planet.name]];
                const statusText = planet.status.length > 0 
                  ? ` (${planet.status.join(', ')})` 
                  : '';
                
                return (
                  <div key={index} className="planet-item">
                    <div className="planet-header">
                      <span 
                        className="planet-name" 
                        style={{ color: planetColors[planet.name] }}
                      >
                        {planet.name} - {planetNames[planet.name]}
                      </span>
                      <span className="planet-details">
                        {planet.deg}° in {sign}{statusText}
                      </span>
                    </div>
                    {planetData && (
                      <div className="planet-effect">
                        <p>{planetData}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {/* Aspects to House */}
        <div className="section">
          <h4>Aspects to House {houseNumber}</h4>
          {aspectsToHouse.length === 0 ? (
            <p className="no-aspects">No aspects to this house</p>
          ) : (
            <div className="aspects-list">
              {aspectsToHouse.map((aspect, index) => (
                <div key={index} className="aspect-item">
                  <span 
                    className="aspect-planet" 
                    style={{ color: aspect.color }}
                  >
                    {aspect.planet}
                  </span>
                  <span className="aspect-details">
                    {aspect.aspectType} aspect from House {aspect.fromHouse} ({aspect.nature})
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Planetary Interactions */}
        <div className="section">
          <h4>Planetary Interactions</h4>
          {planets.length > 1 ? (
            <div className="interactions">
              <p>Multiple planets in this house create complex interactions:</p>
              <ul>
                {planets.map((planet1, i) => 
                  planets.slice(i + 1).map((planet2, j) => (
                    <li key={`${i}-${j}`}>
                      <span style={{ color: planetColors[planet1.name] }}>{planet1.name}</span> {' '}
                      and 
                      <span style={{ color: planetColors[planet2.name] }}> {planet2.name}</span> {' '}
                                             combine their energies in {houseNumber === 1 ? 'personality and self' : 
                         houseNumber === 2 ? 'wealth and family' :
                         houseNumber === 3 ? 'communication and siblings' :
                         houseNumber === 4 ? 'home and mother' :
                         houseNumber === 5 ? 'intelligence and children' :
                         houseNumber === 6 ? 'health and enemies' :
                         houseNumber === 7 ? 'marriage and partnerships' :
                         houseNumber === 8 ? 'longevity and transformation' :
                         houseNumber === 9 ? 'spirituality and father' :
                         houseNumber === 10 ? 'career and profession' :
                         houseNumber === 11 ? 'income and gains' :
                         houseNumber === 12 ? 'expenses and losses' : 'life'} matters
                    </li>
                  ))
                )}
              </ul>
            </div>
          ) : (
            <p>Single planet placement provides focused energy in this area of life.</p>
          )}
        </div>
        

        
        {/* House Strength Analysis */}
        <div className="section">
          <h4>House Strength Analysis</h4>
          <div className="strength-analysis">
            <p>
              <strong>Overall Assessment:</strong> This house is {houseStrength.strength}{' '}
              due to the combination of planetary placements and aspects.
            </p>
            {houseStrength.strength === 'strong' && (
              <p>This indicates favorable circumstances and positive outcomes in this area of life.</p>
            )}
            {houseStrength.strength === 'weak' && (
              <p>This suggests challenges and obstacles that require effort and patience to overcome.</p>
            )}
            {houseStrength.strength === 'neutral' && (
              <p>This indicates a balanced influence with both opportunities and challenges.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HouseAnalysis; 