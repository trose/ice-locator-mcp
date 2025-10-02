import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { ListFieldLevelEncryptionProfilesRequest, ListFieldLevelEncryptionProfilesResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link ListFieldLevelEncryptionProfilesCommand}.
 */
export interface ListFieldLevelEncryptionProfilesCommandInput extends ListFieldLevelEncryptionProfilesRequest {
}
/**
 * @public
 *
 * The output of {@link ListFieldLevelEncryptionProfilesCommand}.
 */
export interface ListFieldLevelEncryptionProfilesCommandOutput extends ListFieldLevelEncryptionProfilesResult, __MetadataBearer {
}
/**
 * @public
 * <p>Request a list of field-level encryption profiles that have been created in CloudFront for
 * 			this account.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, ListFieldLevelEncryptionProfilesCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, ListFieldLevelEncryptionProfilesCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // ListFieldLevelEncryptionProfilesRequest
 *   Marker: "STRING_VALUE",
 *   MaxItems: Number("int"),
 * };
 * const command = new ListFieldLevelEncryptionProfilesCommand(input);
 * const response = await client.send(command);
 * // { // ListFieldLevelEncryptionProfilesResult
 * //   FieldLevelEncryptionProfileList: { // FieldLevelEncryptionProfileList
 * //     NextMarker: "STRING_VALUE",
 * //     MaxItems: Number("int"), // required
 * //     Quantity: Number("int"), // required
 * //     Items: [ // FieldLevelEncryptionProfileSummaryList
 * //       { // FieldLevelEncryptionProfileSummary
 * //         Id: "STRING_VALUE", // required
 * //         LastModifiedTime: new Date("TIMESTAMP"), // required
 * //         Name: "STRING_VALUE", // required
 * //         EncryptionEntities: { // EncryptionEntities
 * //           Quantity: Number("int"), // required
 * //           Items: [ // EncryptionEntityList
 * //             { // EncryptionEntity
 * //               PublicKeyId: "STRING_VALUE", // required
 * //               ProviderId: "STRING_VALUE", // required
 * //               FieldPatterns: { // FieldPatterns
 * //                 Quantity: Number("int"), // required
 * //                 Items: [ // FieldPatternList
 * //                   "STRING_VALUE",
 * //                 ],
 * //               },
 * //             },
 * //           ],
 * //         },
 * //         Comment: "STRING_VALUE",
 * //       },
 * //     ],
 * //   },
 * // };
 *
 * ```
 *
 * @param ListFieldLevelEncryptionProfilesCommandInput - {@link ListFieldLevelEncryptionProfilesCommandInput}
 * @returns {@link ListFieldLevelEncryptionProfilesCommandOutput}
 * @see {@link ListFieldLevelEncryptionProfilesCommandInput} for command's `input` shape.
 * @see {@link ListFieldLevelEncryptionProfilesCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidArgument} (client fault)
 *  <p>An argument is invalid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class ListFieldLevelEncryptionProfilesCommand extends $Command<ListFieldLevelEncryptionProfilesCommandInput, ListFieldLevelEncryptionProfilesCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: ListFieldLevelEncryptionProfilesCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: ListFieldLevelEncryptionProfilesCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<ListFieldLevelEncryptionProfilesCommandInput, ListFieldLevelEncryptionProfilesCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
