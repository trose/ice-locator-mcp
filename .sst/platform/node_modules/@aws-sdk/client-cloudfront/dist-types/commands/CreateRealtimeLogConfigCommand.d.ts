import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { CreateRealtimeLogConfigRequest, CreateRealtimeLogConfigResult } from "../models/models_0";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link CreateRealtimeLogConfigCommand}.
 */
export interface CreateRealtimeLogConfigCommandInput extends CreateRealtimeLogConfigRequest {
}
/**
 * @public
 *
 * The output of {@link CreateRealtimeLogConfigCommand}.
 */
export interface CreateRealtimeLogConfigCommandOutput extends CreateRealtimeLogConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Creates a real-time log configuration.</p>
 *          <p>After you create a real-time log configuration, you can attach it to one or more cache
 * 			behaviors to send real-time log data to the specified Amazon Kinesis data stream.</p>
 *          <p>For more information about real-time log configurations, see <a href="https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/real-time-logs.html">Real-time logs</a> in the
 * 				<i>Amazon CloudFront Developer Guide</i>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, CreateRealtimeLogConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, CreateRealtimeLogConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // CreateRealtimeLogConfigRequest
 *   EndPoints: [ // EndPointList // required
 *     { // EndPoint
 *       StreamType: "STRING_VALUE", // required
 *       KinesisStreamConfig: { // KinesisStreamConfig
 *         RoleARN: "STRING_VALUE", // required
 *         StreamARN: "STRING_VALUE", // required
 *       },
 *     },
 *   ],
 *   Fields: [ // FieldList // required
 *     "STRING_VALUE",
 *   ],
 *   Name: "STRING_VALUE", // required
 *   SamplingRate: Number("long"), // required
 * };
 * const command = new CreateRealtimeLogConfigCommand(input);
 * const response = await client.send(command);
 * // { // CreateRealtimeLogConfigResult
 * //   RealtimeLogConfig: { // RealtimeLogConfig
 * //     ARN: "STRING_VALUE", // required
 * //     Name: "STRING_VALUE", // required
 * //     SamplingRate: Number("long"), // required
 * //     EndPoints: [ // EndPointList // required
 * //       { // EndPoint
 * //         StreamType: "STRING_VALUE", // required
 * //         KinesisStreamConfig: { // KinesisStreamConfig
 * //           RoleARN: "STRING_VALUE", // required
 * //           StreamARN: "STRING_VALUE", // required
 * //         },
 * //       },
 * //     ],
 * //     Fields: [ // FieldList // required
 * //       "STRING_VALUE",
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param CreateRealtimeLogConfigCommandInput - {@link CreateRealtimeLogConfigCommandInput}
 * @returns {@link CreateRealtimeLogConfigCommandOutput}
 * @see {@link CreateRealtimeLogConfigCommandInput} for command's `input` shape.
 * @see {@link CreateRealtimeLogConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link RealtimeLogConfigAlreadyExists} (client fault)
 *  <p>A real-time log configuration with this name already exists. You must provide a unique
 * 			name. To modify an existing real-time log configuration, use
 * 				<code>UpdateRealtimeLogConfig</code>.</p>
 *
 * @throws {@link TooManyRealtimeLogConfigs} (client fault)
 *  <p>You have reached the maximum number of real-time log configurations for this
 * 			Amazon Web Services account. For more information, see <a href="https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html">Quotas</a> (formerly known as limits) in the
 * 				<i>Amazon CloudFront Developer Guide</i>.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class CreateRealtimeLogConfigCommand extends $Command<CreateRealtimeLogConfigCommandInput, CreateRealtimeLogConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: CreateRealtimeLogConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: CreateRealtimeLogConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<CreateRealtimeLogConfigCommandInput, CreateRealtimeLogConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
