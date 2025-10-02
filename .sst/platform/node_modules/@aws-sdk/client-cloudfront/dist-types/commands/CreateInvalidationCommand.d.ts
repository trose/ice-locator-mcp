import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { CreateInvalidationRequest, CreateInvalidationResult } from "../models/models_0";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link CreateInvalidationCommand}.
 */
export interface CreateInvalidationCommandInput extends CreateInvalidationRequest {
}
/**
 * @public
 *
 * The output of {@link CreateInvalidationCommand}.
 */
export interface CreateInvalidationCommandOutput extends CreateInvalidationResult, __MetadataBearer {
}
/**
 * @public
 * <p>Create a new invalidation.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, CreateInvalidationCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, CreateInvalidationCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // CreateInvalidationRequest
 *   DistributionId: "STRING_VALUE", // required
 *   InvalidationBatch: { // InvalidationBatch
 *     Paths: { // Paths
 *       Quantity: Number("int"), // required
 *       Items: [ // PathList
 *         "STRING_VALUE",
 *       ],
 *     },
 *     CallerReference: "STRING_VALUE", // required
 *   },
 * };
 * const command = new CreateInvalidationCommand(input);
 * const response = await client.send(command);
 * // { // CreateInvalidationResult
 * //   Location: "STRING_VALUE",
 * //   Invalidation: { // Invalidation
 * //     Id: "STRING_VALUE", // required
 * //     Status: "STRING_VALUE", // required
 * //     CreateTime: new Date("TIMESTAMP"), // required
 * //     InvalidationBatch: { // InvalidationBatch
 * //       Paths: { // Paths
 * //         Quantity: Number("int"), // required
 * //         Items: [ // PathList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //       CallerReference: "STRING_VALUE", // required
 * //     },
 * //   },
 * // };
 *
 * ```
 *
 * @param CreateInvalidationCommandInput - {@link CreateInvalidationCommandInput}
 * @returns {@link CreateInvalidationCommandOutput}
 * @see {@link CreateInvalidationCommandInput} for command's `input` shape.
 * @see {@link CreateInvalidationCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link BatchTooLarge} (client fault)
 *  <p>Invalidation batch specified is too large.</p>
 *
 * @throws {@link InconsistentQuantities} (client fault)
 *  <p>The value of <code>Quantity</code> and the size of <code>Items</code> don't
 * 			match.</p>
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link MissingBody} (client fault)
 *  <p>This operation requires a body. Ensure that the body is present and the
 * 				<code>Content-Type</code> header is set.</p>
 *
 * @throws {@link NoSuchDistribution} (client fault)
 *  <p>The specified distribution does not exist.</p>
 *
 * @throws {@link TooManyInvalidationsInProgress} (client fault)
 *  <p>You have exceeded the maximum number of allowable InProgress invalidation batch
 * 			requests, or invalidation objects.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class CreateInvalidationCommand extends $Command<CreateInvalidationCommandInput, CreateInvalidationCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: CreateInvalidationCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: CreateInvalidationCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<CreateInvalidationCommandInput, CreateInvalidationCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
