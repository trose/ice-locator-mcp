import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListDistributionsByKeyGroupRequest, ListDistributionsByKeyGroupResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListDistributionsByKeyGroupCommand}.
 */
export interface ListDistributionsByKeyGroupCommandInput extends ListDistributionsByKeyGroupRequest {
}
/**
 * @public
 *
 * The output of {@link ListDistributionsByKeyGroupCommand}.
 */
export interface ListDistributionsByKeyGroupCommandOutput extends ListDistributionsByKeyGroupResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets a list of distribution IDs for distributions that have a cache behavior that
 * 			references the specified key group.</p>
 *          <p>You can optionally specify the maximum number of items to receive in the response. If
 * 			the total number of items in the list exceeds the maximum that you specify, or the
 * 			default maximum, the response is paginated. To get the next page of items, send a
 * 			subsequent request that specifies the <code>NextMarker</code> value from the current
 * 			response as the <code>Marker</code> value in the subsequent request.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListDistributionsByKeyGroupCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListDistributionsByKeyGroupCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListDistributionsByKeyGroupRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 *   KeyGroupId: "STRING_VALUE", // required
 * };
 * const command = new ListDistributionsByKeyGroupCommand(input);
 * const response = await client.send(command);
 * // { // ListDistributionsByKeyGroupResult
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
 * @param ListDistributionsByKeyGroupCommandInput - {@link ListDistributionsByKeyGroupCommandInput}
 * @returns {@link ListDistributionsByKeyGroupCommandOutput}
 * @see {@link ListDistributionsByKeyGroupCommandInput} for command's `input` shape.
 * @see {@link ListDistributionsByKeyGroupCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link NoSuchResource} (client fault)
 *  <p>A resource that was specified is not valid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListDistributionsByKeyGroupCommand extends $Command<ListDistributionsByKeyGroupCommandInput, ListDistributionsByKeyGroupCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListDistributionsByKeyGroupCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListDistributionsByKeyGroupCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListDistributionsByKeyGroupCommandInput, ListDistributionsByKeyGroupCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
