import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListInvalidationsRequest, ListInvalidationsResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListInvalidationsCommand}.
 */
export interface ListInvalidationsCommandInput extends ListInvalidationsRequest {
}
/**
 * @public
 *
 * The output of {@link ListInvalidationsCommand}.
 */
export interface ListInvalidationsCommandOutput extends ListInvalidationsResult, __MetadataBearer {
}
/**
 * @public
 * <p>Lists invalidation batches.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListInvalidationsCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListInvalidationsCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListInvalidationsRequest
 *   DistributionId: "STRING_VALUE", // required
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 * };
 * const command = new ListInvalidationsCommand(input);
 * const response = await client.send(command);
 * // { // ListInvalidationsResult
 * //   InvalidationList: { // InvalidationList
 * //     Marker: "STRING_VALUE", // required
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     IsTruncated: true || false, // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // InvalidationSummaryList
 * //       { // InvalidationSummary
 * //         Id: "STRING_VALUE", // required
 * //         CreateTime: new Date("TIMESTAMP"), // required
 * //         Status: "STRING_VALUE", // required
 * //       },
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListInvalidationsCommandInput - {@link ListInvalidationsCommandInput}
 * @returns {@link ListInvalidationsCommandOutput}
 * @see {@link ListInvalidationsCommandInput} for command's `input` shape.
 * @see {@link ListInvalidationsCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link NoSuchDistribution} (client fault)
 *  <p>The specified distribution does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListInvalidationsCommand extends $Command<ListInvalidationsCommandInput, ListInvalidationsCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListInvalidationsCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListInvalidationsCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListInvalidationsCommandInput, ListInvalidationsCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
