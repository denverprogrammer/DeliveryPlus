import _ from 'lodash';
import type { Campaign, Recipient } from '../types/api';

/**
 * Type guard to check if a value is a Campaign object (not just a number)
 */
export const isCampaignObject = (campaign: number | Campaign): campaign is Campaign => {
    return !_.isNumber(campaign) && campaign !== null && 'id' in campaign;
};

/**
 * Type guard to check if a value is a Recipient object (not just a number or null)
 */
export const isRecipientObject = (recipient: number | null | Recipient): recipient is Recipient => {
    return !_.isNumber(recipient) && recipient !== null && 'id' in recipient;
};

/**
 * Type guard to check if a value is a non-empty array
 */
export const isNonEmptyArray = <T>(value: T[] | undefined | null): value is T[] => {
    return _.isArray(value) && !_.isEmpty(value);
};

