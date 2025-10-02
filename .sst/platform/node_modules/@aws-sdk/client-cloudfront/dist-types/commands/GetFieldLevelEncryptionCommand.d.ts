import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetFieldLevelEncryptionRequest, GetFieldLevelEncryptionResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetFieldLevelEncryptionCommand}.
 */
export interface GetFieldLevelEncryptionCommandInput extends GetFieldLevelEncryptionRequest {
}
/**
 * @public
 *
 * The output of {@link GetFieldLevelEncryptionCommand}.
 */
export interface GetFieldLevelEncryptionCommandOutput extends GetFieldLevelEncryptionResult, __MetadataBearer {
}
/**
 * @public
 * <p>Get the field-level encryption configuration information.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetFieldLevelEncryptionCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetFieldLevelEncryptionCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetFieldLevelEncryptionRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetFieldLevelEncryptionCommand(input);
 * const response = await client.send(command);
 * // { // GetFieldLevelEncryptionResult
 * //   FieldLevelEncryption: { // FieldLevelEncryption
 * //     Id: "STRING_VALUE", // required
 * //     LastModifiedTime: new Date("TIMESTAMP"), // required
 * //     FieldLevelEncryptionConfig: { // FieldLevelEncryptionConfig
 * //       CallerReference: "STRING_VALUE", // required
 * //       Comment: "STRING_VALUE",
 * //       QueryArgProfileConfig: { // QueryArgProfileConfig
 * //         ForwardWhenQueryArgProfileIsUnknown: true || false, // required
 * //         QueryArgProfiles: { // QueryArgProfiles
 * //           Quantity: Number("int"), // required
 * //           Items: [ // QueryArgProfileList
 * //             { // QueryArgProfile
 * //               QueryArg: "STRING_VALUE", // required
 * //               ProfileId: "STRING_VALUE", // required
 * //             },
 * //           ],
 * //         },
 * //       },
 * //       ContentTypeProfileConfig: { // ContentTypeProfileConfig
 * //         ForwardWhenContentTypeIsUnknown: true || false, // required
 * //         ContentTypeProfiles: { // ContentTypeProfiles
 * //           Quantity: Number("int"), // required
 * //           Items: [ // ContentTypeProfileList
 * //             { // ContentTypeProfile
 * //               Format: "URLEncoded", // required
 * //               ProfileId: "STRING_VALUE",
 * //               ContentType: "STRING_VALUE", // required
 * //             },
 * //           ],
 * //         },
 * //       },
 * //     },
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetFieldLevelEncryptionCommandInput - {@link GetFieldLevelEncryptionCommandInput}
 * @returns {@link GetFieldLevelEncryptionCommandOutput}
 * @see {@link GetFieldLevelEncryptionCommandInput} for command's `input` shape.
 * @see {@link GetFieldLevelEncryptionCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchFieldLevelEncryptionConfig} (client fault)
 *  <p>The specified configuration for field-level encryption doesn't exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetFieldLevelEncryptionCommand extends $Command<GetFieldLevelEncryptionCommandInput, GetFieldLevelEncryptionCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetFieldLevelEncryptionCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetFieldLevelEncryptionCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetFieldLevelEncryptionCommandInput, GetFieldLevelEncryptionCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
