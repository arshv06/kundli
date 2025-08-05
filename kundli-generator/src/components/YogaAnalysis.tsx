import React from 'react';
import './YogaAnalysis.css';

interface Planet {
  name: string;
  deg: number;
  sign: string;
  status: string[];
}

interface YogaAnalysisProps {
  signPlanets: Record<string, Planet[]>;
  ascSign: string;
  dataset: any;
}

const planetNames: Record<string, string> = {
  Su: 'Sun', Mo: 'Moon', Ma: 'Mars', Me: 'Mercury', 
  Ju: 'Jupiter', Ve: 'Venus', Sa: 'Saturn', Ra: 'Rahu', Ke: 'Ketu'
};

const YogaAnalysis: React.FC<YogaAnalysisProps> = ({
  signPlanets,
  ascSign,
  dataset
}) => {
  // Get all planets with their house positions
  const getAllPlanetsWithHouses = () => {
    const planetsWithHouses: Array<{planet: Planet, house: number, sign: string}> = [];
    const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
    const ascIndex = signs.indexOf(ascSign);
    
    Object.entries(signPlanets).forEach(([sign, planets]) => {
      const signIndex = signs.indexOf(sign);
      const house = ((signIndex - ascIndex + 12) % 12) + 1;
      
      planets.forEach(planet => {
        planetsWithHouses.push({ planet, house, sign });
      });
    });
    
    return planetsWithHouses;
  };

  // Detect all yogas in the chart
  const detectYogas = () => {
    const yogas: Array<{name: string, condition: string, effect: string, details: string}> = [];
    const allPlanets = getAllPlanetsWithHouses();
    
    if (!dataset.yogas) return yogas;
    
    Object.entries(dataset.yogas).forEach(([yogaName, yogaData]: [string, any]) => {
      let yogaDetected = false;
      let details = '';
      
      // Gaj Kesari Yoga - Jupiter in angular house (1,4,7,10)
      if (yogaName === 'GajKesariYog') {
        const jupiterInAngular = allPlanets.find(p => p.planet.name === 'Ju' && [1, 4, 7, 10].includes(p.house));
        if (jupiterInAngular) {
          yogaDetected = true;
          details = `Jupiter in House ${jupiterInAngular.house} (${jupiterInAngular.sign})`;
        }
      }
      
      // Kal Sarp Yoga - All planets between Rahu and Ketu
      if (yogaName === 'KalSarpYog') {
        const rahu = allPlanets.find(p => p.planet.name === 'Ra');
        const ketu = allPlanets.find(p => p.planet.name === 'Ke');
        if (rahu && ketu) {
          // Check if all planets are between Rahu and Ketu
          const rahuDeg = rahu.planet.deg + (rahu.house - 1) * 30;
          const ketuDeg = ketu.planet.deg + (ketu.house - 1) * 30;
          
          const allBetween = allPlanets.every(p => {
            if (p.planet.name === 'Ra' || p.planet.name === 'Ke') return true;
            const planetDeg = p.planet.deg + (p.house - 1) * 30;
            return (rahuDeg <= planetDeg && planetDeg <= ketuDeg) || 
                   (ketuDeg <= planetDeg && planetDeg <= rahuDeg);
          });
          
          if (allBetween) {
            yogaDetected = true;
            details = `Rahu in House ${rahu.house} (${rahu.sign}), Ketu in House ${ketu.house} (${ketu.sign})`;
          }
        }
      }
      
      // Pancha Mahapurusha Yoga - Strong planets in angular houses
      if (yogaName === 'PanchaMahapurushaYog') {
        const strongPlanets = allPlanets.filter(p => 
          ['Me', 'Ve', 'Ma', 'Ju', 'Sa'].includes(p.planet.name) && 
          p.planet.status.includes('exalted') &&
          [1, 4, 7, 10].includes(p.house)
        );
        if (strongPlanets.length > 0) {
          yogaDetected = true;
          details = strongPlanets.map(p => 
            `${planetNames[p.planet.name]} (exalted) in House ${p.house} (${p.sign})`
          ).join(', ');
        }
      }
      
      // Chandra Mangal Yoga - Moon and Mars in same house
      if (yogaName === 'ChandraMangalYog') {
        const moon = allPlanets.find(p => p.planet.name === 'Mo');
        const mars = allPlanets.find(p => p.planet.name === 'Ma');
        if (moon && mars && moon.house === mars.house) {
          yogaDetected = true;
          details = `Moon and Mars in House ${moon.house} (${moon.sign})`;
        }
      }
      
      // Amala Yoga - Benefic in 10th house
      if (yogaName === 'AmalaYog') {
        const beneficIn10th = allPlanets.find(p => 
          ['Ju', 'Ve', 'Mo'].includes(p.planet.name) && p.house === 10
        );
        if (beneficIn10th) {
          yogaDetected = true;
          details = `${planetNames[beneficIn10th.planet.name]} in House 10 (${beneficIn10th.sign})`;
        }
      }
      
      // Saraswati Yoga - Mercury, Jupiter, Venus in Kendras/Trikonas
      if (yogaName === 'SaraswatiYog') {
        const saraswatiPlanets = allPlanets.filter(p => 
          ['Me', 'Ju', 'Ve'].includes(p.planet.name) && 
          [1, 4, 5, 7, 9, 10].includes(p.house)
        );
        if (saraswatiPlanets.length >= 2) {
          yogaDetected = true;
          details = saraswatiPlanets.map(p => 
            `${planetNames[p.planet.name]} in House ${p.house} (${p.sign})`
          ).join(', ');
        }
      }
      
             // Raj Yoga - Lords of Kendra and Trikona in conjunction/aspect
       if (yogaName === 'RajYog') {
         // This is a complex yoga that requires lord calculations
         // For now, we'll check if we have planets in both Kendra and Trikona houses
         const kendraPlanets = allPlanets.filter(p => [1, 4, 7, 10].includes(p.house));
         const trikonaPlanets = allPlanets.filter(p => [1, 5, 9].includes(p.house));
         
         if (kendraPlanets.length > 0 && trikonaPlanets.length > 0) {
           yogaDetected = true;
           details = `Planets in Kendra houses (${kendraPlanets.map(p => p.house).join(',')}) and Trikona houses (${trikonaPlanets.map(p => p.house).join(',')})`;
         }
       }
       
       // Neecha Bhang Raj Yoga - Debilitated planet's debilitation is canceled
       if (yogaName === 'NeechBhangRajYog') {
         const debilitatedPlanets = allPlanets.filter(p => p.planet.status.includes('debilitated'));
         
         // Check if debilitated planet is in its own sign or exalted sign's house
         // This is a simplified check - in reality, it's more complex
         const neechaBhangPlanets = debilitatedPlanets.filter(p => {
           // Check if the debilitated planet is in a strong position
           // For example, if debilitated Mars is in Aries (its own sign) or Capricorn (exalted)
           const planetName = p.planet.name;
           const planetSign = p.sign;
           
           // Simplified logic: check if debilitated planet is in angular house or with benefics
           const isInAngularHouse = [1, 4, 7, 10].includes(p.house);
           const hasBeneficAspect = allPlanets.some(otherPlanet => 
             ['Ju', 'Ve', 'Mo'].includes(otherPlanet.planet.name) && 
             otherPlanet.house === p.house
           );
           
           return isInAngularHouse || hasBeneficAspect;
         });
         
         if (neechaBhangPlanets.length > 0) {
           yogaDetected = true;
           details = neechaBhangPlanets.map(p => 
             `${planetNames[p.planet.name]} (debilitated but strengthened) in House ${p.house} (${p.sign})`
           ).join(', ');
         }
       }
      
      if (yogaDetected) {
        yogas.push({
          name: yogaName,
          condition: yogaData.condition,
          effect: yogaData.effect,
          details
        });
      }
    });
    
    return yogas;
  };

  const detectedYogas = detectYogas();

  return (
    <div className="yoga-analysis">
      <div className="yoga-header">
        <h3>Chart Yogas</h3>
        <span className="yoga-count">{detectedYogas.length} Yogas Detected</span>
      </div>
      
      <div className="yoga-content">
        {detectedYogas.length === 0 ? (
          <div className="no-yogas">
            <p>No major yogas detected in this chart.</p>
            <p>This is normal - yogas are rare and specific planetary combinations.</p>
          </div>
        ) : (
          <div className="yogas-list">
            {detectedYogas.map((yoga, index) => (
              <div key={index} className="yoga-item">
                <div className="yoga-title">
                  <h4>{yoga.name}</h4>
                  <span className="yoga-type">Major Yoga</span>
                </div>
                <div className="yoga-details">
                  <p><strong>Condition:</strong> {yoga.condition}</p>
                  <p><strong>Effect:</strong> {yoga.effect}</p>
                  <p><strong>Formation:</strong> {yoga.details}</p>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div className="yoga-info">
          <h4>About Yogas</h4>
          <p>
            Yogas are special planetary combinations that create significant influences in Vedic astrology. 
            They can be auspicious (like Raj Yoga, Gaj Kesari Yoga) or challenging (like Kal Sarp Yoga). 
            The presence of yogas indicates specific life themes and potential outcomes.
          </p>
        </div>
      </div>
    </div>
  );
};

export default YogaAnalysis; 