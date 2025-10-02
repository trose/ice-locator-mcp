import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListOriginAccessControlsRequest, ListOriginAccessControlsResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListOriginAccessControlsCommand}.
 */
export interface ListOriginAccessControlsCommandInput extends ListOriginAccessControlsRequest {
}
/**
 * @public
 *
 * The output of {@link ListOriginAccessControlsCommand}.
 */
export interface ListOriginAccessControlsCommandOutput extends ListOriginAccessControlsResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets the list of CloudFront origin access controls in this Amazon Web Services account.</p>
 *          <p>You can optionally specify the maximum number of items to receive in the response. If
 * 			the total number of items in the list exceeds the maximum that you specify, or the
 * 			default maximum, the response is paginated. To get the next page of items, send another
 * 			request that specifies the <code>NextMarker</code> value from the current response as
 * 			the <code>Marker</code> value in the next request.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListOriginAccessControlsCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListOriginAccessControlsCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListOriginAccessControlsRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 * };
 * const command = new ListOriginAccessControlsCommand(input);
 * const response = await client.send(command);
 * // { // ListOriginAccessControlsResult
 * //   OriginAccessControlList: { // OriginAccessControlList
 * //     Marker: "STRING_VALUE", // required
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     IsTruncated: true || false, // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // OriginAccessControlSummaryList
 * //       { // OriginAccessControlSummary
 * //         Id: "STRING_VALUE", // required
 * //         Description: "STRING_VALUE", // required
 * //         Name: "STRING_VALUE", // required
 * //         SigningProtocol: "sigv4", // required
 * //         SigningBehavior: "never" || "always" || "no-override", // required
 * //         OriginAccessControlOriginType: "s3" || "mediastore", // required
 * //       },
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListOriginAccessControlsCommandInput - {@link ListOriginAccessControlsCommandInput}
 * @returns {@link ListOriginAccessControlsCommandOutput}
 * @see {@link ListOriginAccessControlsCommandInput} for command's `input` shape.
 * @see {@link ListOriginAccessControlsCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListOriginAccessControlsCommand extends $Command<ListOriginAccessControlsCommandInput, ListOriginAccessControlsCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListOriginAccessControlsCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListOriginAccessControlsCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListOriginAccessControlsCommandInput, ListOriginAccessControlsCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
