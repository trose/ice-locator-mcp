import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetFieldLevelEncryptionProfileConfigRequest, GetFieldLevelEncryptionProfileConfigResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetFieldLevelEncryptionProfileConfigCommand}.
 */
export interface GetFieldLevelEncryptionProfileConfigCommandInput extends GetFieldLevelEncryptionProfileConfigRequest {
}
/**
 * @public
 *
 * The output of {@link GetFieldLevelEncryptionProfileConfigCommand}.
 */
export interface GetFieldLevelEncryptionProfileConfigCommandOutput extends GetFieldLevelEncryptionProfileConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Get the field-level encryption profile configuration information.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetFieldLevelEncryptionProfileConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetFieldLevelEncryptionProfileConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetFieldLevelEncryptionProfileConfigRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetFieldLevelEncryptionProfileConfigCommand(input);
 * const response = await client.send(command);
 * // { // GetFieldLevelEncryptionProfileConfigResult
 * //   FieldLevelEncryptionProfileConfig: { // FieldLevelEncryptionProfileConfig
 * //     Name: "STRING_VALUE", // required
 * //     CallerReference: "STRING_VALUE", // required
 * //     Comment: "STRING_VALUE",
 * //     EncryptionEntities: { // EncryptionEntities
 * //       Quantity: Number("int"), // required
 * //       Items: [ // EncryptionEntityList
 * //         { // EncryptionEntity
 * //           PublicKeyId: "STRING_VALUE", // required
 * //           ProviderId: "STRING_VALUE", // required
 * //           FieldPatterns: { // FieldPatterns
 * //             Quantity: Number("int"), // required
 * //             Items: [ // FieldPatternList
 * //               "STRING_VALUE",
 * //             ],
 * //           },
 * //         },
 * //       ],
 * //     },
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetFieldLevelEncryptionProfileConfigCommandInput - {@link GetFieldLevelEncryptionProfileConfigCommandInput}
 * @returns {@link GetFieldLevelEncryptionProfileConfigCommandOutput}
 * @see {@link GetFieldLevelEncryptionProfileConfigCommandInput} for command's `input` shape.
 * @see {@link GetFieldLevelEncryptionProfileConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchFieldLevelEncryptionProfile} (client fault)
 *  <p>The specified profile for field-level encryption doesn't exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetFieldLevelEncryptionProfileConfigCommand extends $Command<GetFieldLevelEncryptionProfileConfigCommandInput, GetFieldLevelEncryptionProfileConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetFieldLevelEncryptionProfileConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetFieldLevelEncryptionProfileConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetFieldLevelEncryptionProfileConfigCommandInput, GetFieldLevelEncryptionProfileConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
