# CSS Architecture

This document outlines the CSS architecture for the Bribery game application.

## CSS Structure

The CSS is organized as follows:

- Main CSS files:
  - `game.css`: Contains all styles for the game page
  - `index.css`: Contains all styles for the landing page

- Component CSS files (in the `components/` directory):
  - Reusable UI components (buttons, forms, etc.)
  - Game-specific components (phases, scoreboard, etc.)
  - Layout components (lobby, player list, etc.)

## CSS Consolidation (August 2025)

In August 2025, the CSS structure was simplified by consolidating "enhanced" CSS files with their base counterparts. This resolved issues with style conflicts and overlapping rules.

The following files were consolidated:
- `buttons.css` + `enhanced-buttons.css` → `buttons.css`
- `game-phases.css` + `enhanced-phases.css` → `game-phases.css`
- `landing-page.css` + `enhanced-landing.css` → `landing-page.css`
- `results-display.css` + `enhanced-results.css` → `results-display.css`

Original files were backed up in:
- `components/original_backup/`
- `components/enhanced_backup/`

## CSS Best Practices

1. Mobile-first approach - styles are designed for mobile and then enhanced for larger screens
2. Component-based architecture - styles are organized by UI component
3. BEM naming convention for class names (Block, Element, Modifier)
4. Use of utility classes for common spacing, typography, and layout
5. Use of CSS variables for consistent color schemes and spacing
6. Minimal use of nested selectors to avoid specificity issues

## Adding New Styles

When adding new styles:
1. Determine if the styles belong to an existing component
2. If yes, add the styles to the appropriate component CSS file
3. If no, create a new component CSS file and import it in the main CSS file
4. Use the existing utility classes when possible to maintain consistency

## Browser Support

The CSS is designed to support:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)
