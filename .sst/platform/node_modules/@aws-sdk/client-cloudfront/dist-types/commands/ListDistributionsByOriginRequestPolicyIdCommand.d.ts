import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListDistributionsByOriginRequestPolicyIdRequest, ListDistributionsByOriginRequestPolicyIdResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListDistributionsByOriginRequestPolicyIdCommand}.
 */
export interface ListDistributionsByOriginRequestPolicyIdCommandInput extends ListDistributionsByOriginRequestPolicyIdRequest {
}
/**
 * @public
 *
 * The output of {@link ListDistributionsByOriginRequestPolicyIdCommand}.
 */
export interface ListDistributionsByOriginRequestPolicyIdCommandOutput extends ListDistributionsByOriginRequestPolicyIdResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets a list of distribution IDs for distributions that have a cache behavior that's
 * 			associated with the specified origin request policy.</p>
 *          <p>You can optionally specify the maximum number of items to receive in the response. If
 * 			the total number of items in the list exceeds the maximum that you specify, or the
 * 			default maximum, the response is paginated. To get the next page of items, send a
 * 			subsequent request that specifies the <code>NextMarker</code> value from the current
 * 			response as the <code>Marker</code> value in the subsequent request.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListDistributionsByOriginRequestPolicyIdCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListDistributionsByOriginRequestPolicyIdCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListDistributionsByOriginRequestPolicyIdRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 *   OriginRequestPolicyId: "STRING_VALUE", // required
 * };
 * const command = new ListDistributionsByOriginRequestPolicyIdCommand(input);
 * const response = await client.send(command);
 * // { // ListDistributionsByOriginRequestPolicyIdResult
 * //   DistributionIdList: { // DistributionIdList
 * //     Marker: "STRING_VALUE", // required
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     IsTruncated: true || false, // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // DistributionIdListSummary
 * //       "STRING_VALUE",
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListDistributionsByOriginRequestPolicyIdCommandInput - {@link ListDistributionsByOriginRequestPolicyIdCommandInput}
 * @returns {@link ListDistributionsByOriginRequestPolicyIdCommandOutput}
 * @see {@link ListDistributionsByOriginRequestPolicyIdCommandInput} for command's `input` shape.
 * @see {@link ListDistributionsByOriginRequestPolicyIdCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link NoSuchOriginRequestPolicy} (client fault)
 *  <p>The origin request policy does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListDistributionsByOriginRequestPolicyIdCommand extends $Command<ListDistributionsByOriginRequestPolicyIdCommandInput, ListDistributionsByOriginRequestPolicyIdCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListDistributionsByOriginRequestPolicyIdCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListDistributionsByOriginRequestPolicyIdCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListDistributionsByOriginRequestPolicyIdCommandInput, ListDistributionsByOriginRequestPolicyIdCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
