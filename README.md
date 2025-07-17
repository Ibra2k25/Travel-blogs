# Ghana Travel Website

A stunning glassmorphism travel website showcasing Ghana's beauty and culture with modern animations and responsive design.

## ✨ Features

### 🎨 Design & Aesthetics
- **Glassmorphism Effects**: Beautiful frosted glass design with backdrop filters
- **Black Gradient Background**: Sophisticated dark theme with animated gradients
- **Lemon Green Accents**: Vibrant green buttons and highlights (#9acd32, #32cd32)
- **Floating Animations**: Subtle animated shapes in the background
- **Smooth Transitions**: Buttery-smooth hover effects and page transitions

### 📱 Responsive Design
- Mobile-first approach
- Tablet and desktop optimized
- Hamburger menu for mobile navigation
- Flexible grid layouts

### 🏠 Pages Included

1. **Homepage (index.html)**
   - Hero section with animated title
   - Featured destinations preview
   - Why choose Ghana section
   - Call-to-action buttons

2. **Destinations (destinations.html)**
   - Filterable destination gallery
   - Categories: Historical, Nature, Beach, Culture
   - Detailed destination cards with ratings
   - Interactive filter animations

3. **Tours (tours.html)**
   - Tour package showcase
   - Heritage & History Tours
   - Adventure & Nature Tours
   - Beach & Relaxation Tours
   - Cultural Immersion Tours
   - Custom tour options

4. **Booking (booking.html)**
   - Interactive booking form
   - Real-time price calculation
   - Live booking summary
   - Form validation
   - Date selection with constraints

5. **Contact (contact.html)**
   - Contact form with validation
   - Company information
   - Social media links
   - Interactive FAQ section
   - Map placeholder

### 🚀 Interactive Features

- **Smart Navigation**: Auto-highlighting current page
- **Scroll Animations**: Elements animate in as you scroll
- **Filter System**: Dynamic content filtering on destinations page
- **Price Calculator**: Real-time booking cost calculation
- **Form Validation**: Client-side form validation with visual feedback
- **Ripple Effects**: Material design button interactions
- **FAQ Accordion**: Expandable frequently asked questions
- **Local Storage**: Remembers selected destinations across pages

## 🛠️ Technical Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern features including:
  - CSS Grid & Flexbox
  - Backdrop filters
  - CSS animations & transitions
  - Custom properties (CSS variables)
  - Media queries for responsiveness

- **Vanilla JavaScript**: No framework dependencies
  - ES6+ features
  - Intersection Observer API
  - Local Storage API
  - Form validation
  - DOM manipulation

- **External Resources**:
  - Font Awesome icons
  - Google Fonts (Inter)

## 📁 File Structure

```
ghana-travel-website/
├── index.html              # Homepage
├── destinations.html       # Destinations gallery
├── tours.html             # Tour packages
├── booking.html           # Booking form
├── contact.html           # Contact page
├── styles.css             # Main stylesheet
├── script.js              # Main JavaScript
├── destinations.js        # Destinations page logic
├── booking.js             # Booking form logic
├── contact.js             # Contact form logic
└── README.md              # This file
```

## 🎯 Key Animations & Effects

### Background Effects
- Animated gradient shifts
- Floating shapes with rotation
- Parallax scrolling effects

### Interactive Elements
- Hover elevations on cards
- Button ripple effects
- Smooth page transitions
- Loading animations

### Scroll Animations
- Fade-in effects
- Slide-in animations
- Staggered element reveals

## 🎨 Color Palette

- **Background**: Black gradients (#000000, #1a1a1a, #2d2d2d)
- **Primary Green**: #9acd32 (Yellow Green)
- **Secondary Green**: #32cd32 (Lime Green)
- **Text**: White with various opacity levels
- **Glass Effects**: White with 10-20% opacity
- **Accent Colors**: Gold stars (#ffd700), Error red (#ff4444)

## 🚀 Getting Started

1. **Download the files**: Copy all HTML, CSS, and JS files to your web server
2. **Open index.html**: Start with the homepage
3. **No build process required**: Pure HTML/CSS/JS - works immediately
4. **Web server recommended**: For best experience, serve from a web server

## 📱 Browser Support

- Chrome 88+
- Firefox 87+
- Safari 14+
- Edge 88+

*Note: Some glassmorphism effects require modern browser support for backdrop-filter*

## 🎨 Customization Guide

### Colors
Edit the CSS custom properties in `styles.css`:
```css
:root {
  --primary-green: #9acd32;
  --secondary-green: #32cd32;
  --glass-bg: rgba(255, 255, 255, 0.1);
}
```

### Destinations
Add new destinations in `destinations.html` and update the filter logic in `destinations.js`.

### Pricing
Update the price data object in `booking.js`:
```javascript
const prices = {
  destinations: {
    'new-destination': 100
  }
}
```

## 🔧 Features Overview

### Glassmorphism Implementation
```css
.glass {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
}
```

### Responsive Grid System
```css
.destinations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 30px;
}
```

### JavaScript Animations
- Intersection Observer for scroll animations
- CSS transforms for smooth transitions
- Local Storage for state persistence

## 📞 Support

For questions about customization or implementation, the code is well-commented and follows modern web development best practices.

## 🌟 Live Demo

Simply open `index.html` in your browser to see the website in action!

---

**Built with ❤️ for showcasing Ghana's beautiful destinations**