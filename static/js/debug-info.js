// Debug information for deployment issues
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Bribery Debug Information');

    // Logo debugging
    const logo = document.querySelector('.hero-logo');
    if (logo) {
        console.log('Logo found:', {
            src: logo.getAttribute('src'),
            complete: logo.complete,
            naturalWidth: logo.naturalWidth,
            naturalHeight: logo.naturalHeight,
            offsetWidth: logo.offsetWidth,
            offsetHeight: logo.offsetHeight,
            computedStyle: {
                maxWidth: getComputedStyle(logo).maxWidth,
                maxHeight: getComputedStyle(logo).maxHeight
            }
        });
    } else {
        console.log('Logo element not found');
    }

    // CSS debugging
    const cssFiles = Array.from(document.styleSheets)
        .filter(sheet => sheet.href && sheet.href.includes('css'))
        .map(sheet => sheet.href);
    
    console.log('Loaded CSS files:', cssFiles);
    
    // Check if specific CSS files are loaded
    const enhancedLandingLoaded = cssFiles.some(url => url.includes('enhanced-landing.css'));
    const logoStylesLoaded = cssFiles.some(url => url.includes('logo.css'));
    
    console.log('Enhanced landing CSS loaded:', enhancedLandingLoaded);
    console.log('Logo CSS loaded:', logoStylesLoaded);
});
