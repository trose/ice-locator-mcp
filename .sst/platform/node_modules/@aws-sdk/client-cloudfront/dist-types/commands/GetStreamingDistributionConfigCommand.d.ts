import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetStreamingDistributionConfigRequest, GetStreamingDistributionConfigResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetStreamingDistributionConfigCommand}.
 */
export interface GetStreamingDistributionConfigCommandInput extends GetStreamingDistributionConfigRequest {
}
/**
 * @public
 *
 * The output of {@link GetStreamingDistributionConfigCommand}.
 */
export interface GetStreamingDistributionConfigCommandOutput extends GetStreamingDistributionConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Get the configuration information about a streaming distribution.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetStreamingDistributionConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetStreamingDistributionConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetStreamingDistributionConfigRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetStreamingDistributionConfigCommand(input);
 * const response = await client.send(command);
 * // { // GetStreamingDistributionConfigResult
 * //   StreamingDistributionConfig: { // StreamingDistributionConfig
 * //     CallerReference: "STRING_VALUE", // required
 * //     S3Origin: { // S3Origin
 * //       DomainName: "STRING_VALUE", // required
 * //       OriginAccessIdentity: "STRING_VALUE", // required
 * //     },
 * //     Aliases: { // Aliases
 * //       Quantity: Number("int"), // required
 * //       Items: [ // AliasList
 * //         "STRING_VALUE",
 * //       ],
 * //     },
 * //     Comment: "STRING_VALUE", // required
 * //     Logging: { // StreamingLoggingConfig
 * //       Enabled: true || false, // required
 * //       Bucket: "STRING_VALUE", // required
 * //       Prefix: "STRING_VALUE", // required
 * //     },
 * //     TrustedSigners: { // TrustedSigners
 * //       Enabled: true || false, // required
 * //       Quantity: Number("int"), // required
 * //       Items: [ // AwsAccountNumberList
 * //         "STRING_VALUE",
 * //       ],
 * //     },
 * //     PriceClass: "PriceClass_100" || "PriceClass_200" || "PriceClass_All",
 * //     Enabled: true || false, // required
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetStreamingDistributionConfigCommandInput - {@link GetStreamingDistributionConfigCommandInput}
 * @returns {@link GetStreamingDistributionConfigCommandOutput}
 * @see {@link GetStreamingDistributionConfigCommandInput} for command's `input` shape.
 * @see {@link GetStreamingDistributionConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchStreamingDistribution} (client fault)
 *  <p>The specified streaming distribution does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetStreamingDistributionConfigCommand extends $Command<GetStreamingDistributionConfigCommandInput, GetStreamingDistributionConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetStreamingDistributionConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetStreamingDistributionConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetStreamingDistributionConfigCommandInput, GetStreamingDistributionConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
