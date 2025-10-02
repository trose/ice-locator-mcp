import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListPublicKeysRequest, ListPublicKeysResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListPublicKeysCommand}.
 */
export interface ListPublicKeysCommandInput extends ListPublicKeysRequest {
}
/**
 * @public
 *
 * The output of {@link ListPublicKeysCommand}.
 */
export interface ListPublicKeysCommandOutput extends ListPublicKeysResult, __MetadataBearer {
}
/**
 * @public
 * <p>List all public keys that have been added to CloudFront for this account.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListPublicKeysCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListPublicKeysCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListPublicKeysRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 * };
 * const command = new ListPublicKeysCommand(input);
 * const response = await client.send(command);
 * // { // ListPublicKeysResult
 * //   PublicKeyList: { // PublicKeyList
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // PublicKeySummaryList
 * //       { // PublicKeySummary
 * //         Id: "STRING_VALUE", // required
 * //         Name: "STRING_VALUE", // required
 * //         CreatedTime: new Date("TIMESTAMP"), // required
 * //         EncodedKey: "STRING_VALUE", // required
 * //         Comment: "STRING_VALUE",
 * //       },
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListPublicKeysCommandInput - {@link ListPublicKeysCommandInput}
 * @returns {@link ListPublicKeysCommandOutput}
 * @see {@link ListPublicKeysCommandInput} for command's `input` shape.
 * @see {@link ListPublicKeysCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListPublicKeysCommand extends $Command<ListPublicKeysCommandInput, ListPublicKeysCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListPublicKeysCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListPublicKeysCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListPublicKeysCommandInput, ListPublicKeysCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
