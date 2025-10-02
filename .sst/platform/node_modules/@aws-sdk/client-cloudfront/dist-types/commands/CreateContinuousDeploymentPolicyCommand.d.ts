import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { CreateContinuousDeploymentPolicyRequest, CreateContinuousDeploymentPolicyResult } from "../models/models_0";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link CreateContinuousDeploymentPolicyCommand}.
 */
export interface CreateContinuousDeploymentPolicyCommandInput extends CreateContinuousDeploymentPolicyRequest {
}
/**
 * @public
 *
 * The output of {@link CreateContinuousDeploymentPolicyCommand}.
 */
export interface CreateContinuousDeploymentPolicyCommandOutput extends CreateContinuousDeploymentPolicyResult, __MetadataBearer {
}
/**
 * @public
 * <p>Creates a continuous deployment policy that distributes traffic for a custom domain
 * 			name to two different CloudFront distributions.</p>
 *          <p>To use a continuous deployment policy, first use <code>CopyDistribution</code> to
 * 			create a staging distribution, then use <code>UpdateDistribution</code> to modify the
 * 			staging distribution's configuration.</p>
 *          <p>After you create and update a staging distribution, you can use a continuous
 * 			deployment policy to incrementally move traffic to the staging distribution. This
 * 			workflow enables you to test changes to a distribution's configuration before moving all
 * 			of your domain's production traffic to the new configuration.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, CreateContinuousDeploymentPolicyCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, CreateContinuousDeploymentPolicyCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // CreateContinuousDeploymentPolicyRequest
 *   ContinuousDeploymentPolicyConfig: { // ContinuousDeploymentPolicyConfig
 *     StagingDistributionDnsNames: { // StagingDistributionDnsNames
 *       Quantity: Number("int"), // required
 *       Items: [ // StagingDistributionDnsNameList
 *         "STRING_VALUE",
 *       ],
 *     },
 *     Enabled: true || false, // required
 *     TrafficConfig: { // TrafficConfig
 *       SingleWeightConfig: { // ContinuousDeploymentSingleWeightConfig
 *         Weight: Number("float"), // required
 *         SessionStickinessConfig: { // SessionStickinessConfig
 *           IdleTTL: Number("int"), // required
 *           MaximumTTL: Number("int"), // required
 *         },
 *       },
 *       SingleHeaderConfig: { // ContinuousDeploymentSingleHeaderConfig
 *         Header: "STRING_VALUE", // required
 *         Value: "STRING_VALUE", // required
 *       },
 *       Type: "SingleWeight" || "SingleHeader", // required
 *     },
 *   },
 * };
 * const command = new CreateContinuousDeploymentPolicyCommand(input);
 * const response = await client.send(command);
 * // { // CreateContinuousDeploymentPolicyResult
 * //   ContinuousDeploymentPolicy: { // ContinuousDeploymentPolicy
 * //     Id: "STRING_VALUE", // required
 * //     LastModifiedTime: new Date("TIMESTAMP"), // required
 * //     ContinuousDeploymentPolicyConfig: { // ContinuousDeploymentPolicyConfig
 * //       StagingDistributionDnsNames: { // StagingDistributionDnsNames
 * //         Quantity: Number("int"), // required
 * //         Items: [ // StagingDistributionDnsNameList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //       Enabled: true || false, // required
 * //       TrafficConfig: { // TrafficConfig
 * //         SingleWeightConfig: { // ContinuousDeploymentSingleWeightConfig
 * //           Weight: Number("float"), // required
 * //           SessionStickinessConfig: { // SessionStickinessConfig
 * //             IdleTTL: Number("int"), // required
 * //             MaximumTTL: Number("int"), // required
 * //           },
 * //         },
 * //         SingleHeaderConfig: { // ContinuousDeploymentSingleHeaderConfig
 * //           Header: "STRING_VALUE", // required
 * //           Value: "STRING_VALUE", // required
 * //         },
 * //         Type: "SingleWeight" || "SingleHeader", // required
 * //       },
 * //     },
 * //   },
 * //   Location: "STRING_VALUE",
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param CreateContinuousDeploymentPolicyCommandInput - {@link CreateContinuousDeploymentPolicyCommandInput}
 * @returns {@link CreateContinuousDeploymentPolicyCommandOutput}
 * @see {@link CreateContinuousDeploymentPolicyCommandInput} for command's `input` shape.
 * @see {@link CreateContinuousDeploymentPolicyCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link ContinuousDeploymentPolicyAlreadyExists} (client fault)
 *  <p>A continuous deployment policy with this configuration already exists.</p>
 *
 * @throws {@link InconsistentQuantities} (client fault)
 *  <p>The value of <code>Quantity</code> and the size of <code>Items</code> don't
 * 			match.</p>
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link StagingDistributionInUse} (client fault)
 *  <p>A continuous deployment policy for this staging distribution already exists.</p>
 *
 * @throws {@link TooManyContinuousDeploymentPolicies} (client fault)
 *  <p>You have reached the maximum number of continuous deployment policies for this
 * 			Amazon Web Services account.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class CreateContinuousDeploymentPolicyCommand extends $Command<CreateContinuousDeploymentPolicyCommandInput, CreateContinuousDeploymentPolicyCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: CreateContinuousDeploymentPolicyCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: CreateContinuousDeploymentPolicyCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<CreateContinuousDeploymentPolicyCommandInput, CreateContinuousDeploymentPolicyCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
