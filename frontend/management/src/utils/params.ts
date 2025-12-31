import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

/**
 * Parses a string ID parameter and converts it to a number or null.
 * Returns null if the string is undefined, empty, or cannot be parsed as a valid number.
 * 
 * @param id - The string ID to parse (typically from useParams)
 * @returns The parsed number, or null if invalid
 * 
 * @example
 * const { id } = useParams<{ id?: string }>();
 * const campaignId = parseIdParam(id);
 */
export const parseIdParam = (id: string | undefined): number | null => {
    if (!id) return null;
    const parsed = parseInt(id, 10);
    return isNaN(parsed) ? null : parsed;
};

/**
 * Custom hook that gets a parsed ID parameter from the route.
 * Returns a stateful value that updates when the param changes.
 * 
 * @param paramName - The name of the route parameter to parse (default: 'id')
 * @returns A tuple of [parsedId, setParsedId] where parsedId is number | null
 * 
 * @example
 * const [campaignId, setCampaignId] = useParsedParam('id');
 */
export const useParsedParam = (paramName: string = 'id'): [number | null, (value: number | null) => void] => {
    const params = useParams<Record<string, string | undefined>>();
    const paramValue = params[paramName];
    const [parsedId, setParsedId] = useState<number | null>(() => parseIdParam(paramValue));

    useEffect(() => {
        setParsedId(parseIdParam(paramValue));
    }, [paramValue]);

    return [parsedId, setParsedId];
};

