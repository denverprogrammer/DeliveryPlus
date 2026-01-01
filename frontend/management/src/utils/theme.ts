import {
    themeQuartz,
    themeBalham,
    themeAlpine,
    themeMaterial,
    colorSchemeLight,
    colorSchemeDark,
    colorSchemeVariable,
    colorSchemeLightWarm,
    colorSchemeLightCold,
    colorSchemeDarkWarm,
    colorSchemeDarkBlue,
    iconSetQuartz,
    iconSetMaterial,
    iconSetAlpine,
    iconSetQuartzBold,
    iconSetQuartzLight,
    iconSetQuartzRegular,
} from 'ag-grid-community';

export const getTheme = (themeName: string, colorScheme: string, iconSet: string) => {
    let theme;
    switch (themeName) {
        case 'quartz':
            theme = themeQuartz;
            break;
        case 'balham':
            theme = themeBalham;
            break;
        case 'alpine':
            theme = themeAlpine;
            break;
        case 'material':
            theme = themeMaterial;
            break;
        default:
            theme = themeQuartz;
    }

    // Apply color scheme
    switch (colorScheme) {
        case 'light':
            theme = theme.withPart(colorSchemeLight);
            break;
        case 'dark':
            theme = theme.withPart(colorSchemeDark);
            break;
        case 'variable':
            theme = theme.withPart(colorSchemeVariable);
            break;
        case 'light-warm':
            theme = theme.withPart(colorSchemeLightWarm);
            break;
        case 'light-cold':
            theme = theme.withPart(colorSchemeLightCold);
            break;
        case 'dark-warm':
            theme = theme.withPart(colorSchemeDarkWarm);
            break;
        case 'dark-blue':
            theme = theme.withPart(colorSchemeDarkBlue);
            break;
    }

    // Apply icon set
    switch (iconSet) {
        case 'quartz':
            theme = theme.withPart(iconSetQuartz);
            break;
        case 'material':
            theme = theme.withPart(iconSetMaterial);
            break;
        case 'alpine':
            theme = theme.withPart(iconSetAlpine);
            break;
        case 'quartz-bold':
            theme = theme.withPart(iconSetQuartzBold);
            break;
        case 'quartz-light':
            theme = theme.withPart(iconSetQuartzLight);
            break;
        case 'quartz-regular':
            theme = theme.withPart(iconSetQuartzRegular);
            break;
    }

    return theme;
};

