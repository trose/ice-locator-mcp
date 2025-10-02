import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListFieldLevelEncryptionConfigsRequest, ListFieldLevelEncryptionConfigsResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListFieldLevelEncryptionConfigsCommand}.
 */
export interface ListFieldLevelEncryptionConfigsCommandInput extends ListFieldLevelEncryptionConfigsRequest {
}
/**
 * @public
 *
 * The output of {@link ListFieldLevelEncryptionConfigsCommand}.
 */
export interface ListFieldLevelEncryptionConfigsCommandOutput extends ListFieldLevelEncryptionConfigsResult, __MetadataBearer {
}
/**
 * @public
 * <p>List all field-level encryption configurations that have been created in CloudFront for this
 * 			account.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListFieldLevelEncryptionConfigsCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListFieldLevelEncryptionConfigsCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListFieldLevelEncryptionConfigsRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 * };
 * const command = new ListFieldLevelEncryptionConfigsCommand(input);
 * const response = await client.send(command);
 * // { // ListFieldLevelEncryptionConfigsResult
 * //   FieldLevelEncryptionList: { // FieldLevelEncryptionList
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // FieldLevelEncryptionSummaryList
 * //       { // FieldLevelEncryptionSummary
 * //         Id: "STRING_VALUE", // required
 * //         LastModifiedTime: new Date("TIMESTAMP"), // required
 * //         Comment: "STRING_VALUE",
 * //         QueryArgProfileConfig: { // QueryArgProfileConfig
 * //           ForwardWhenQueryArgProfileIsUnknown: true || false, // required
 * //           QueryArgProfiles: { // QueryArgProfiles
 * //             Quantity: Number("int"), // required
 * //             Items: [ // QueryArgProfileList
 * //               { // QueryArgProfile
 * //                 QueryArg: "STRING_VALUE", // required
 * //                 ProfileId: "STRING_VALUE", // required
 * //               },
 * //             ],
 * //           },
 * //         },
 * //         ContentTypeProfileConfig: { // ContentTypeProfileConfig
 * //           ForwardWhenContentTypeIsUnknown: true || false, // required
 * //           ContentTypeProfiles: { // ContentTypeProfiles
 * //             Quantity: Number("int"), // required
 * //             Items: [ // ContentTypeProfileList
 * //               { // ContentTypeProfile
 * //                 Format: "URLEncoded", // required
 * //                 ProfileId: "STRING_VALUE",
 * //                 ContentType: "STRING_VALUE", // required
 * //               },
 * //             ],
 * //           },
 * //         },
 * //       },
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListFieldLevelEncryptionConfigsCommandInput - {@link ListFieldLevelEncryptionConfigsCommandInput}
 * @returns {@link ListFieldLevelEncryptionConfigsCommandOutput}
 * @see {@link ListFieldLevelEncryptionConfigsCommandInput} for command's `input` shape.
 * @see {@link ListFieldLevelEncryptionConfigsCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListFieldLevelEncryptionConfigsCommand extends $Command<ListFieldLevelEncryptionConfigsCommandInput, ListFieldLevelEncryptionConfigsCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListFieldLevelEncryptionConfigsCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListFieldLevelEncryptionConfigsCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListFieldLevelEncryptionConfigsCommandInput, ListFieldLevelEncryptionConfigsCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
