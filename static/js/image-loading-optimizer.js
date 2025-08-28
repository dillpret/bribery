/**
 * Image loading optimizer for Bribery game
 * Improves perceived performance by handling logo and images more efficiently
 * 
 * This file is included in both module and non-module contexts
 * It must be self-contained and not reference any external variables
 */

// Use an IIFE to avoid polluting global scope
(function() {
    // Initialize logo optimization when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        optimizeLogoLoading();
    });

    /**
     * Optimizes logo loading with better UX
     * - Gradually fades in the full logo when loaded
     * - Falls back to text if image fails to load
     */
    function optimizeLogoLoading() {
        const logoElements = document.querySelectorAll('.hero-logo');
        
        logoElements.forEach(logo => {
            // If logo is already loaded from cache, don't apply fade-in effect
            if (logo.complete && logo.naturalHeight !== 0) {
                logo.classList.add('logo-loaded');
                return;
            }
            
            // Handle successful load with smooth transition
            logo.addEventListener('load', () => {
                logo.classList.add('logo-loaded');
            });
            
            // Error already handled via onerror attribute
        });
    }
})();
