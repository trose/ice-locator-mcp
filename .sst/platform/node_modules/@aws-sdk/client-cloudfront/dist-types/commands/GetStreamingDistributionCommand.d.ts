import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetStreamingDistributionRequest, GetStreamingDistributionResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetStreamingDistributionCommand}.
 */
export interface GetStreamingDistributionCommandInput extends GetStreamingDistributionRequest {
}
/**
 * @public
 *
 * The output of {@link GetStreamingDistributionCommand}.
 */
export interface GetStreamingDistributionCommandOutput extends GetStreamingDistributionResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets information about a specified RTMP distribution, including the distribution
 * 			configuration.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetStreamingDistributionCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetStreamingDistributionCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetStreamingDistributionRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetStreamingDistributionCommand(input);
 * const response = await client.send(command);
 * // { // GetStreamingDistributionResult
 * //   StreamingDistribution: { // StreamingDistribution
 * //     Id: "STRING_VALUE", // required
 * //     ARN: "STRING_VALUE", // required
 * //     Status: "STRING_VALUE", // required
 * //     LastModifiedTime: new Date("TIMESTAMP"),
 * //     DomainName: "STRING_VALUE", // required
 * //     ActiveTrustedSigners: { // ActiveTrustedSigners
 * //       Enabled: true || false, // required
 * //       Quantity: Number("int"), // required
 * //       Items: [ // SignerList
 * //         { // Signer
 * //           AwsAccountNumber: "STRING_VALUE",
 * //           KeyPairIds: { // KeyPairIds
 * //             Quantity: Number("int"), // required
 * //             Items: [ // KeyPairIdList
 * //               "STRING_VALUE",
 * //             ],
 * //           },
 * //         },
 * //       ],
 * //     },
 * //     StreamingDistributionConfig: { // StreamingDistributionConfig
 * //       CallerReference: "STRING_VALUE", // required
 * //       S3Origin: { // S3Origin
 * //         DomainName: "STRING_VALUE", // required
 * //         OriginAccessIdentity: "STRING_VALUE", // required
 * //       },
 * //       Aliases: { // Aliases
 * //         Quantity: Number("int"), // required
 * //         Items: [ // AliasList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //       Comment: "STRING_VALUE", // required
 * //       Logging: { // StreamingLoggingConfig
 * //         Enabled: true || false, // required
 * //         Bucket: "STRING_VALUE", // required
 * //         Prefix: "STRING_VALUE", // required
 * //       },
 * //       TrustedSigners: { // TrustedSigners
 * //         Enabled: true || false, // required
 * //         Quantity: Number("int"), // required
 * //         Items: [ // AwsAccountNumberList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //       PriceClass: "PriceClass_100" || "PriceClass_200" || "PriceClass_All",
 * //       Enabled: true || false, // required
 * //     },
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetStreamingDistributionCommandInput - {@link GetStreamingDistributionCommandInput}
 * @returns {@link GetStreamingDistributionCommandOutput}
 * @see {@link GetStreamingDistributionCommandInput} for command's `input` shape.
 * @see {@link GetStreamingDistributionCommandOutput} for command's `response` shape.
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
export declare class GetStreamingDistributionCommand extends $Command<GetStreamingDistributionCommandInput, GetStreamingDistributionCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetStreamingDistributionCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetStreamingDistributionCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetStreamingDistributionCommandInput, GetStreamingDistributionCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
