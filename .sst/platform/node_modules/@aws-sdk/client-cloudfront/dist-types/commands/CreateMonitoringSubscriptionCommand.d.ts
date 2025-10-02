import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { CreateMonitoringSubscriptionRequest, CreateMonitoringSubscriptionResult } from "../models/models_0";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link CreateMonitoringSubscriptionCommand}.
 */
export interface CreateMonitoringSubscriptionCommandInput extends CreateMonitoringSubscriptionRequest {
}
/**
 * @public
 *
 * The output of {@link CreateMonitoringSubscriptionCommand}.
 */
export interface CreateMonitoringSubscriptionCommandOutput extends CreateMonitoringSubscriptionResult, __MetadataBearer {
}
/**
 * @public
 * <p>Enables additional CloudWatch metrics for the specified CloudFront distribution. The
 * 			additional metrics incur an additional cost.</p>
 *          <p>For more information, see <a href="https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/viewing-cloudfront-metrics.html#monitoring-console.distributions-additional">Viewing additional CloudFront distribution metrics</a> in
 * 			the <i>Amazon CloudFront Developer Guide</i>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, CreateMonitoringSubscriptionCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, CreateMonitoringSubscriptionCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // CreateMonitoringSubscriptionRequest
 *   DistributionId: "STRING_VALUE", // required
 *   MonitoringSubscription: { // MonitoringSubscription
 *     RealtimeMetricsSubscriptionConfig: { // RealtimeMetricsSubscriptionConfig
 *       RealtimeMetricsSubscriptionStatus: "Enabled" || "Disabled", // required
 *     },
 *   },
 * };
 * const command = new CreateMonitoringSubscriptionCommand(input);
 * const response = await client.send(command);
 * // { // CreateMonitoringSubscriptionResult
 * //   MonitoringSubscription: { // MonitoringSubscription
 * //     RealtimeMetricsSubscriptionConfig: { // RealtimeMetricsSubscriptionConfig
 * //       RealtimeMetricsSubscriptionStatus: "Enabled" || "Disabled", // required
 * //     },
 * //   },
 * // };
 *
 * ```
 *
 * @param CreateMonitoringSubscriptionCommandInput - {@link CreateMonitoringSubscriptionCommandInput}
 * @returns {@link CreateMonitoringSubscriptionCommandOutput}
 * @see {@link CreateMonitoringSubscriptionCommandInput} for command's `input` shape.
 * @see {@link CreateMonitoringSubscriptionCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link MonitoringSubscriptionAlreadyExists} (client fault)
 *  <p>A monitoring subscription already exists for the specified distribution.</p>
 *
 * @throws {@link NoSuchDistribution} (client fault)
 *  <p>The specified distribution does not exist.</p>
 *
 * @throws {@link UnsupportedOperation} (client fault)
 *  <p>This operation is not supported in this region.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class CreateMonitoringSubscriptionCommand extends $Command<CreateMonitoringSubscriptionCommandInput, CreateMonitoringSubscriptionCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: CreateMonitoringSubscriptionCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: CreateMonitoringSubscriptionCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<CreateMonitoringSubscriptionCommandInput, CreateMonitoringSubscriptionCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
