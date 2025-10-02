"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.waitUntilDistributionDeployed = exports.waitForDistributionDeployed = void 0;
const util_waiter_1 = require("@smithy/util-waiter");
const GetDistributionCommand_1 = require("../commands/GetDistributionCommand");
const checkState = async (client, input) => {
    let reason;
    try {
        const result = await client.send(new GetDistributionCommand_1.GetDistributionCommand(input));
        reason = result;
        try {
            const returnComparator = () => {
                return result.Distribution.Status;
            };
            if (returnComparator() === "Deployed") {
                return { state: util_waiter_1.WaiterState.SUCCESS, reason };
            }
        }
        catch (e) { }
    }
    catch (exception) {
        reason = exception;
    }
    return { state: util_waiter_1.WaiterState.RETRY, reason };
};
const waitForDistributionDeployed = async (params, input) => {
    const serviceDefaults = { minDelay: 60, maxDelay: 120 };
    return (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
};
exports.waitForDistributionDeployed = waitForDistributionDeployed;
const waitUntilDistributionDeployed = async (params, input) => {
    const serviceDefaults = { minDelay: 60, maxDelay: 120 };
    const result = await (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
    return (0, util_waiter_1.checkExceptions)(result);
};
exports.waitUntilDistributionDeployed = waitUntilDistributionDeployed;
