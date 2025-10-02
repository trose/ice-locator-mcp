import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { DeleteMonitoringSubscriptionRequest, DeleteMonitoringSubscriptionResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link DeleteMonitoringSubscriptionCommand}.
 */
export interface DeleteMonitoringSubscriptionCommandInput extends DeleteMonitoringSubscriptionRequest {
}
/**
 * @public
 *
 * The output of {@link DeleteMonitoringSubscriptionCommand}.
 */
export interface DeleteMonitoringSubscriptionCommandOutput extends DeleteMonitoringSubscriptionResult, __MetadataBearer {
}
/**
 * @public
 * <p>Disables additional CloudWatch metrics for the specified CloudFront
 * 			distribution.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, DeleteMonitoringSubscriptionCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, DeleteMonitoringSubscriptionCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // DeleteMonitoringSubscriptionRequest
 *   DistributionId: "STRING_VALUE", // required
 * };
 * const command = new DeleteMonitoringSubscriptionCommand(input);
 * const response = await client.send(command);
 * // {};
 *
 * ```
 *
 * @param DeleteMonitoringSubscriptionCommandInput - {@link DeleteMonitoringSubscriptionCommandInput}
 * @returns {@link DeleteMonitoringSubscriptionCommandOutput}
 * @see {@link DeleteMonitoringSubscriptionCommandInput} for command's `input` shape.
 * @see {@link DeleteMonitoringSubscriptionCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchDistribution} (client fault)
 *  <p>The specified distribution does not exist.</p>
 *
 * @throws {@link NoSuchMonitoringSubscription} (client fault)
 *  <p>A monitoring subscription does not exist for the specified distribution.</p>
 *
 * @throws {@link UnsupportedOperation} (client fault)
 *  <p>This operation is not supported in this region.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class DeleteMonitoringSubscriptionCommand extends $Command<DeleteMonitoringSubscriptionCommandInput, DeleteMonitoringSubscriptionCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: DeleteMonitoringSubscriptionCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: DeleteMonitoringSubscriptionCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<DeleteMonitoringSubscriptionCommandInput, DeleteMonitoringSubscriptionCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
