"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.waitUntilInvalidationCompleted = exports.waitForInvalidationCompleted = void 0;
const util_waiter_1 = require("@smithy/util-waiter");
const GetInvalidationCommand_1 = require("../commands/GetInvalidationCommand");
const checkState = async (client, input) => {
    let reason;
    try {
        const result = await client.send(new GetInvalidationCommand_1.GetInvalidationCommand(input));
        reason = result;
        try {
            const returnComparator = () => {
                return result.Invalidation.Status;
            };
            if (returnComparator() === "Completed") {
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
const waitForInvalidationCompleted = async (params, input) => {
    const serviceDefaults = { minDelay: 20, maxDelay: 120 };
    return (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
};
exports.waitForInvalidationCompleted = waitForInvalidationCompleted;
const waitUntilInvalidationCompleted = async (params, input) => {
    const serviceDefaults = { minDelay: 20, maxDelay: 120 };
    const result = await (0, util_waiter_1.createWaiter)({ ...serviceDefaults, ...params }, input, checkState);
    return (0, util_waiter_1.checkExceptions)(result);
};
exports.waitUntilInvalidationCompleted = waitUntilInvalidationCompleted;
