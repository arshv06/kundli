# Kundli Generator

A comprehensive Vedic astrology chart generator with detailed planetary analysis, house strength assessment, and AI-powered interpretations.

## Features

### 🎯 Core Functionality
- **Birth Chart Generation**: Generate accurate D1 (birth) and D9 (navamsa) charts
- **Planetary Positions**: Real-time calculation of all 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- **House System**: 12-house Vedic astrology system with detailed interpretations
- **Aspect Analysis**: Complete planetary aspect calculations and visualization

### 🎨 Visual Features
- **Interactive Chart**: Click on any house to view detailed information
- **House Strength Coloring**: 
  - 🟢 Green: Strong houses (favorable)
  - 🟡 Yellow: Neutral houses (balanced)
  - 🔴 Red: Challenging houses (needs attention)
- **Planetary Status**: Visual indicators for exalted, debilitated, combust, and retrograde planets
- **Aspect Lines**: Dynamic aspect visualization with color-coded planetary influences

### 📊 Comprehensive Analysis
- **Detailed House Analysis**: Each house includes:
  - Planetary placements and their effects
  - Aspect influences from other planets
  - Planetary interactions within the house
  - House strength assessment
  - Yoga identification and effects

### 🤖 AI Integration
- **Intelligent Analysis**: Ask questions about your chart and get personalized interpretations
- **Contextual Responses**: AI considers planetary positions, aspects, and house strengths
- **Vedic Wisdom**: Responses based on traditional Vedic astrology principles

### 🧘‍♀️ Yoga Detection
The system identifies various yogas including:
- **Raj Yoga**: Lords of Kendra and Trikona houses
- **Gaj Kesari Yoga**: Jupiter in angular houses relative to Moon
- **Dhan Yoga**: Wealth-related planetary combinations
- **Kal Sarp Yoga**: All planets between Rahu and Ketu
- **Pancha Mahapurusha Yoga**: Strong planets in angular houses
- **Chandra Mangal Yoga**: Moon-Mars conjunction
- **Amala Yoga**: Benefic planets in 10th house
- **Saraswati Yoga**: Mercury, Jupiter, Venus in Kendras/Trikonas

## Dataset Integration

The application uses a comprehensive Vedic astrology dataset that includes:
- **House Meanings**: Detailed descriptions of all 12 houses
- **Planetary Effects**: How each planet influences each house
- **Aspect Interpretations**: Meaning of planetary aspects
- **Yoga Definitions**: Complete yoga conditions and effects

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kundli-generator
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up the backend**
   ```bash
   cd kundli-backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy the example environment file and add your Hugging Face API token:
   ```bash
   cd kundli-backend
   cp yay.env.example yay.env
   ```
   
   Edit `yay.env` and add your Hugging Face API token:
   ```
   HUGGING_FACE_TOKEN=your_huggingface_token_here
   ```
   
   **Important**: Never commit your actual API token to Git. The `yay.env` file is already in `.gitignore`.
   
   To get a Hugging Face token:
   1. Go to https://huggingface.co/settings/tokens
   2. Create a new token with "read" permissions
   3. Copy the token and paste it in your `yay.env` file

5. **Start the backend**
   ```bash
   cd kundli-backend
   python app.py
   ```

6. **Start the frontend**
   ```bash
   npm run dev
   ```

## Usage

1. **Enter Birth Details**: Provide name, date, time, location, and timezone
2. **Generate Chart**: Click "Generate Kundli" to create your birth chart
3. **Explore Houses**: Click on any house to see detailed analysis
4. **View Aspects**: Use the aspect filter to focus on specific planetary influences
5. **Detailed Analysis**: Toggle the "Show Analysis" button for comprehensive house-by-house breakdown
6. **Ask AI**: Use the AI analysis section for personalized interpretations

## Technical Details

### Frontend
- **React + TypeScript**: Modern, type-safe development
- **Vite**: Fast build tool and development server
- **CSS Grid/Flexbox**: Responsive design for all screen sizes

### Backend
- **Flask**: Python web framework
- **Swiss Ephemeris**: High-precision astronomical calculations
- **Hugging Face**: AI model integration for astrological interpretations

### Calculations
- **Ayanamsa**: Lahiri ayanamsa for accurate tropical to sidereal conversion
- **House System**: Placidus house system
- **Planetary Positions**: Swiss Ephemeris for precise calculations
- **Aspects**: Traditional Vedic aspect rules (7th, 4th, 8th, etc.)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Swiss Ephemeris for astronomical calculations
- Traditional Vedic astrology texts and interpretations
- Hugging Face for AI model hosting
