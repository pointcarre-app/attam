/**
 * AccessibilityManager - Centralized state management for themes and fonts
 * Ensures consistency across all UI controls and persists settings in localStorage
 */
class AccessibilityManager {
    constructor() {
        // Priority: localStorage > current DOM > domain default > fallback default
        const savedTheme = localStorage.getItem('attam-theme');
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const defaultTheme = document.documentElement.getAttribute('data-default-theme');
        
        // Initialize state from localStorage first, then fall back to domain default or 'anchor'
        this.state = {
            theme: savedTheme || currentTheme || defaultTheme || 'anchor',
            fontType: localStorage.getItem('attam-font-type') || 'default'
        };
        
        // Store the domain's default theme for reference
        this.domainDefaultTheme = defaultTheme || 'anchor';
        
        // Track if theme is enforced
        this.enforcedTheme = null;
        
        // Subscribers for state changes
        this.listeners = [];
        
        // Font configurations
        this.fontConfigs = {
            'default': this.getDefaultFontConfig(),
            'dyslexic': {
                '--font-sans': 'var(--font-opendyslexic-regular)',
                '--font-body': 'var(--font-opendyslexic-regular)',
                '--font-heading': 'var(--font-opendyslexic-regular)'
            }
        };
        
        // Initialize the manager
        this.init();
    }
    
    init() {
        console.log('🎨 Initializing AccessibilityManager');
        console.log('   Domain default theme:', this.domainDefaultTheme);
        console.log('   Current theme:', this.state.theme);
        console.log('   Current font:', this.state.fontType);
        
        const savedTheme = localStorage.getItem('attam-theme');
        if (savedTheme) {
            console.log('   Using saved preference:', savedTheme);
        } else {
            console.log('   Using domain default (no saved preference)');
        }
        
        // Apply initial state
        this.applyTheme(this.state.theme);
        this.applyFont(this.state.fontType);
        
        // IMPORTANT: Don't save to localStorage on init!
        // Only save when user explicitly changes theme via setTheme()
        // This allows domain defaults to work properly
        
        // Set up event delegation for all controls
        this.setupEventDelegation();
        
        // Update UI to reflect initial state
        this.updateAllUI();
        
        // Also update after a small delay to catch any late-loading elements
        setTimeout(() => {
            this.updateAllUI();
        }, 100);
        
        // Listen for system theme changes
        this.setupSystemThemeListener();
    }
    
    // ===== THEME MANAGEMENT =====
    
    setTheme(theme) {
        // Don't change if theme is enforced
        if (this.enforcedTheme) {
            console.log('⚠️ Theme is enforced as:', this.enforcedTheme);
            return false;
        }
        
        console.log('🎨 Setting theme from', this.state.theme, 'to', theme);
        
        if (this.state.theme !== theme) {
            this.state.theme = theme;
            this.applyTheme(theme);
            
            // If user selects the domain default theme, clear localStorage
            // so they follow the domain default on future visits
            if (theme === this.domainDefaultTheme) {
                console.log('   Clearing saved preference (using domain default)');
                localStorage.removeItem('attam-theme');
            } else {
                console.log('   Saving preference to localStorage');
                localStorage.setItem('attam-theme', theme);
            }
            
            // Force immediate UI update
            requestAnimationFrame(() => {
                this.updateAllUI();
            });
            
            this.notifyListeners('theme', theme);
        } else {
            console.log('✓ Theme already set to:', theme);
            // Even if theme is the same, update UI to ensure consistency
            this.updateAllUI();
        }
        return true;
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        console.log('✓ Applied theme:', theme);
    }
    
    enforceTheme(theme, message = null) {
        this.enforcedTheme = theme;
        this.setTheme(theme);
        this.disableThemeControls();
        
        if (message) {
            this.showToast(message, 'info');
        }
    }
    
    clearEnforcedTheme() {
        this.enforcedTheme = null;
        this.enableThemeControls();
    }
    
    resetToDefaultTheme() {
        console.log('🔄 Resetting to domain default theme:', this.domainDefaultTheme);
        // Clear localStorage first to ensure we're using domain default
        localStorage.removeItem('attam-theme');
        this.setTheme(this.domainDefaultTheme);
    }
    
    // ===== FONT MANAGEMENT =====
    
    /**
     * Reads default font configuration from CSS custom properties defined in root.css
     */
    getDefaultFontConfig() {
        const rootStyles = getComputedStyle(document.documentElement);
        
        const getFontVar = (prop) => {
            const value = rootStyles.getPropertyValue(prop).trim();
            return value || this.getDefaultFontFallback(prop);
        };
        
        return {
            '--font-sans': getFontVar('--font-sans'),
            '--font-body': getFontVar('--font-body'),
            '--font-heading': getFontVar('--font-heading')
        };
    }
    
    /**
     * Fallback values if CSS custom properties can't be read
     */
    getDefaultFontFallback(property) {
        const fallbacks = {
            '--font-sans': 'var(--font-lexend)',
            '--font-body': 'var(--font-lexend)',
            '--font-heading': 'var(--font-outfit)'
        };
        return fallbacks[property] || '';
    }
    
    setFont(fontType) {
        console.log('🔤 Setting font from', this.state.fontType, 'to', fontType);
        
        if (this.state.fontType !== fontType) {
            this.state.fontType = fontType;
            this.applyFont(fontType);
            localStorage.setItem('attam-font-type', fontType);
            
            // Force immediate UI update
            requestAnimationFrame(() => {
                this.updateAllUI();
            });
            
            this.notifyListeners('font', fontType);
        } else {
            console.log('✓ Font already set to:', fontType);
            // Even if font is the same, update UI to ensure consistency
            this.updateAllUI();
        }
    }
    
    applyFont(fontType) {
        const config = this.fontConfigs[fontType];
        if (config) {
            Object.entries(config).forEach(([property, value]) => {
                document.documentElement.style.setProperty(property, value);
            });
            console.log('✓ Applied font:', fontType);
        }
    }
    
    // ===== UI UPDATE METHODS =====
    
    updateAllUI() {
        this.updateThemeUI();
        this.updateFontUI();
    }
    
    updateThemeUI() {
        // Define contrast themes
        const contrastThemes = ['anchor', 'reinforced-contrast', 'inversed-contrast'];
        const isContrastTheme = contrastThemes.includes(this.state.theme);
        
        // Handle the "other theme" radio button for contrast section
        const otherThemeRadio = document.querySelector('[data-contrast-other="true"]');
        if (otherThemeRadio) {
            otherThemeRadio.disabled = true;
            
            if (!isContrastTheme) {
                otherThemeRadio.checked = true;
            } else {
                otherThemeRadio.checked = false;
            }
        }
        
        // Update all theme-related UI elements
        const themeElements = document.querySelectorAll('[data-theme-selector]');
        
        themeElements.forEach(element => {
            const theme = element.dataset.themeSelector;
            
            if (element.type === 'radio' || element.type === 'checkbox') {
                element.checked = (theme === this.state.theme);
            } else if (element.tagName === 'BUTTON') {
                if (theme === this.state.theme) {
                    element.classList.add('btn-active');
                } else {
                    element.classList.remove('btn-active');
                }
            }
            
            // Disable if theme is enforced
            if (this.enforcedTheme && element.tagName === 'BUTTON') {
                element.disabled = true;
                element.classList.add('btn-disabled');
            }
        });
    }
    
    updateFontUI() {
        // Update all font-related UI elements
        const fontElements = document.querySelectorAll('[data-font-selector]');
        
        fontElements.forEach(element => {
            const fontType = element.dataset.fontSelector;
            
            if (element.type === 'radio' || element.type === 'checkbox') {
                element.checked = (fontType === this.state.fontType);
            } else if (element.tagName === 'BUTTON') {
                if (fontType === this.state.fontType) {
                    element.classList.add('btn-active');
                } else {
                    element.classList.remove('btn-active');
                }
            }
        });
    }
    
    // ===== EVENT HANDLING =====
    
    setupEventDelegation() {
        // Use event delegation for all controls
        document.addEventListener('click', (e) => {
            // Theme selector - handle buttons
            const themeSelector = e.target.closest('[data-theme-selector]');
            if (themeSelector && themeSelector.tagName === 'BUTTON') {
                e.preventDefault();
                this.setTheme(themeSelector.dataset.themeSelector);
            }
            
            // Font selector - handle buttons
            const fontSelector = e.target.closest('[data-font-selector]');
            if (fontSelector && fontSelector.tagName === 'BUTTON') {
                e.preventDefault();
                this.setFont(fontSelector.dataset.fontSelector);
            }
        });
        
        // Handle radio button changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-theme-selector][type="radio"]')) {
                console.log('📻 Theme radio changed:', e.target.dataset.themeSelector);
                this.setTheme(e.target.dataset.themeSelector);
            }
            
            if (e.target.matches('[data-font-selector][type="radio"]')) {
                console.log('📻 Font radio changed:', e.target.dataset.fontSelector);
                this.setFont(e.target.dataset.fontSelector);
            }
        });
    }
    
    setupSystemThemeListener() {
        // Listen for system theme preference changes
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        darkModeQuery.addEventListener('change', (e) => {
            // Only apply system preference if user has never selected a theme
            if (!localStorage.getItem('attam-theme') && !this.enforcedTheme) {
                this.setTheme(e.matches ? 'night' : 'anchor');
            }
        });
    }
    
    // ===== CONTROL MANAGEMENT =====
    
    disableThemeControls() {
        document.querySelectorAll('[data-theme-selector]').forEach(element => {
            element.disabled = true;
            if (element.tagName === 'BUTTON') {
                element.classList.add('btn-disabled');
            }
        });
    }
    
    enableThemeControls() {
        document.querySelectorAll('[data-theme-selector]').forEach(element => {
            element.disabled = false;
            if (element.tagName === 'BUTTON') {
                element.classList.remove('btn-disabled');
            }
        });
    }
    
    // ===== OBSERVER PATTERN =====
    
    subscribe(callback) {
        this.listeners.push(callback);
        // Return unsubscribe function
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }
    
    notifyListeners(type, value) {
        this.listeners.forEach(callback => {
            try {
                callback(type, value);
            } catch (error) {
                console.error('Error in accessibility listener:', error);
            }
        });
    }
    
    // ===== UTILITY METHODS =====
    
    showToast(message, type = 'info') {
        console.log(`🔔 Toast [${type}]:`, message);
        // You can implement a toast UI here if needed
    }
    
    // ===== PUBLIC API =====
    
    getState() {
        return { ...this.state };
    }
    
    isThemeEnforced() {
        return this.enforcedTheme !== null;
    }
    
    getCurrentTheme() {
        return this.state.theme;
    }
    
    getCurrentFont() {
        return this.state.fontType;
    }
    
    getDomainDefaultTheme() {
        return this.domainDefaultTheme;
    }
}

// Initialize the manager when DOM is ready
let accessibilityManager = null;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        accessibilityManager = new AccessibilityManager();
        
        // Make it globally available
        window.accessibilityManager = accessibilityManager;
        
        console.log('✅ AccessibilityManager initialized and available as window.accessibilityManager');
    });
} else {
    // DOM already loaded
    accessibilityManager = new AccessibilityManager();
    window.accessibilityManager = accessibilityManager;
    
    console.log('✅ AccessibilityManager initialized and available as window.accessibilityManager');
}

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}
