import { createContext, useContext, useState, useEffect, ReactNode, useMemo } from 'react';
import { getTheme } from '../utils/theme';

interface ThemePreferences {
    theme: string;
    colorScheme: string;
    iconSet: string;
}

interface ThemeContextType {
    theme: string;
    colorScheme: string;
    iconSet: string;
    setTheme: (theme: string) => void;
    setColorScheme: (colorScheme: string) => void;
    setIconSet: (iconSet: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'ag-grid-theme-preferences';
const DEFAULT_THEME = 'quartz';
const DEFAULT_COLOR_SCHEME = 'light';
const DEFAULT_ICON_SET = 'quartz';

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
    const [theme, setThemeState] = useState<string>(DEFAULT_THEME);
    const [colorScheme, setColorSchemeState] = useState<string>(DEFAULT_COLOR_SCHEME);
    const [iconSet, setIconSetState] = useState<string>(DEFAULT_ICON_SET);

    // Load preferences from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem(THEME_STORAGE_KEY);
        if (stored) {
            try {
                const preferences: ThemePreferences = JSON.parse(stored);
                setThemeState(preferences.theme || DEFAULT_THEME);
                setColorSchemeState(preferences.colorScheme || DEFAULT_COLOR_SCHEME);
                setIconSetState(preferences.iconSet || DEFAULT_ICON_SET);
            } catch (error) {
                console.error('Failed to parse theme preferences:', error);
            }
        }
    }, []);

    const setTheme = (newTheme: string) => {
        setThemeState(newTheme);
        const preferences: ThemePreferences = { theme: newTheme, colorScheme, iconSet };
        localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(preferences));
    };

    const setColorScheme = (newColorScheme: string) => {
        setColorSchemeState(newColorScheme);
        const preferences: ThemePreferences = { theme, colorScheme: newColorScheme, iconSet };
        localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(preferences));
    };

    const setIconSet = (newIconSet: string) => {
        setIconSetState(newIconSet);
        const preferences: ThemePreferences = { theme, colorScheme, iconSet: newIconSet };
        localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(preferences));
    };

    const value: ThemeContextType = {
        theme,
        colorScheme,
        iconSet,
        setTheme,
        setColorScheme,
        setIconSet,
    };

    return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export const useGridTheme = () => {
    const { theme, colorScheme, iconSet, setTheme, setColorScheme, setIconSet } = useTheme();
    
    const gridTheme = useMemo(() => {
        return getTheme(theme, colorScheme, iconSet);
    }, [theme, colorScheme, iconSet]);

    return {
        gridTheme,
        theme,
        colorScheme,
        iconSet,
        setTheme,
        setColorScheme,
        setIconSet,
    };
};

