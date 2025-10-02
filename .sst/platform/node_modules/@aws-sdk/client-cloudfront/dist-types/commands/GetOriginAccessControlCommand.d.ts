import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetOriginAccessControlRequest, GetOriginAccessControlResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetOriginAccessControlCommand}.
 */
export interface GetOriginAccessControlCommandInput extends GetOriginAccessControlRequest {
}
/**
 * @public
 *
 * The output of {@link GetOriginAccessControlCommand}.
 */
export interface GetOriginAccessControlCommandOutput extends GetOriginAccessControlResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets a CloudFront origin access control, including its unique identifier.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetOriginAccessControlCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetOriginAccessControlCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetOriginAccessControlRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetOriginAccessControlCommand(input);
 * const response = await client.send(command);
 * // { // GetOriginAccessControlResult
 * //   OriginAccessControl: { // OriginAccessControl
 * //     Id: "STRING_VALUE", // required
 * //     OriginAccessControlConfig: { // OriginAccessControlConfig
 * //       Name: "STRING_VALUE", // required
 * //       Description: "STRING_VALUE",
 * //       SigningProtocol: "sigv4", // required
 * //       SigningBehavior: "never" || "always" || "no-override", // required
 * //       OriginAccessControlOriginType: "s3" || "mediastore", // required
 * //     },
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetOriginAccessControlCommandInput - {@link GetOriginAccessControlCommandInput}
 * @returns {@link GetOriginAccessControlCommandOutput}
 * @see {@link GetOriginAccessControlCommandInput} for command's `input` shape.
 * @see {@link GetOriginAccessControlCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchOriginAccessControl} (client fault)
 *  <p>The origin access control does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetOriginAccessControlCommand extends $Command<GetOriginAccessControlCommandInput, GetOriginAccessControlCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetOriginAccessControlCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetOriginAccessControlCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetOriginAccessControlCommandInput, GetOriginAccessControlCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
