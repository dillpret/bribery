// Cache busting for static resources
document.addEventListener('DOMContentLoaded', function() {
    // Get the version number displayed on the page
    const versionElement = document.getElementById('version-number');
    if (!versionElement) return;
    
    // Extract version string (format: "vX.Y.Z")
    const versionString = versionElement.textContent.trim();
    if (!versionString) return;
    
    // Use this as a cache-busting parameter
    const cacheParam = versionString.replace(/[^0-9.]/g, '');
    
    // Apply to all CSS links
    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
        if (link.href.includes('?')) {
            link.href = link.href + '&v=' + cacheParam;
        } else {
            link.href = link.href + '?v=' + cacheParam;
        }
    });
    
    // Apply to images loaded via <img> tags
    document.querySelectorAll('img').forEach(img => {
        if (img.src.includes('?')) {
            img.src = img.src + '&v=' + cacheParam;
        } else {
            img.src = img.src + '?v=' + cacheParam;
        }
    });
});
