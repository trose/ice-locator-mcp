"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.waitUntilStreamingDistributionDeployed = exports.waitForStreamingDistributionDeployed = void 0;
const util_waiter_1 = require("@smithy/util-waiter");
const GetStreamingDistributionCommand_1 = require("../commands/GetStreamingDistributionCommand");
const checkState = async (client, input) => {
    let reason;
    try {
        const result = await client.send(new GetStreamingDistributionCommand_1.GetStreamingDistributionCommand(input));
        reason = result;
        try {
            const returnComparator = () => {
                return result.StreamingDistribution.Status;
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
const waitForStreamingDistributionDeployed = async (params, input) => {
    const serviceDefaults = { minDelay: 60, maxDelay: 120 };
    return (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
};
exports.waitForStreamingDistributionDeployed = waitForStreamingDistributionDeployed;
const waitUntilStreamingDistributionDeployed = async (params, input) => {
    const serviceDefaults = { minDelay: 60, maxDelay: 120 };
    const result = await (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
    return (0, util_waiter_1.checkExceptions)(result);
};
exports.waitUntilStreamingDistributionDeployed = waitUntilStreamingDistributionDeployed;
