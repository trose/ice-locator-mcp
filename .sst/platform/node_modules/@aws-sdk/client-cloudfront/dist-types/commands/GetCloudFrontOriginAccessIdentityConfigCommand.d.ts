import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetCloudFrontOriginAccessIdentityConfigRequest, GetCloudFrontOriginAccessIdentityConfigResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetCloudFrontOriginAccessIdentityConfigCommand}.
 */
export interface GetCloudFrontOriginAccessIdentityConfigCommandInput extends GetCloudFrontOriginAccessIdentityConfigRequest {
}
/**
 * @public
 *
 * The output of {@link GetCloudFrontOriginAccessIdentityConfigCommand}.
 */
export interface GetCloudFrontOriginAccessIdentityConfigCommandOutput extends GetCloudFrontOriginAccessIdentityConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Get the configuration information about an origin access identity.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetCloudFrontOriginAccessIdentityConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetCloudFrontOriginAccessIdentityConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetCloudFrontOriginAccessIdentityConfigRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetCloudFrontOriginAccessIdentityConfigCommand(input);
 * const response = await client.send(command);
 * // { // GetCloudFrontOriginAccessIdentityConfigResult
 * //   CloudFrontOriginAccessIdentityConfig: { // CloudFrontOriginAccessIdentityConfig
 * //     CallerReference: "STRING_VALUE", // required
 * //     Comment: "STRING_VALUE", // required
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetCloudFrontOriginAccessIdentityConfigCommandInput - {@link GetCloudFrontOriginAccessIdentityConfigCommandInput}
 * @returns {@link GetCloudFrontOriginAccessIdentityConfigCommandOutput}
 * @see {@link GetCloudFrontOriginAccessIdentityConfigCommandInput} for command's `input` shape.
 * @see {@link GetCloudFrontOriginAccessIdentityConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchCloudFrontOriginAccessIdentity} (client fault)
 *  <p>The specified origin access identity does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetCloudFrontOriginAccessIdentityConfigCommand extends $Command<GetCloudFrontOriginAccessIdentityConfigCommandInput, GetCloudFrontOriginAccessIdentityConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetCloudFrontOriginAccessIdentityConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetCloudFrontOriginAccessIdentityConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetCloudFrontOriginAccessIdentityConfigCommandInput, GetCloudFrontOriginAccessIdentityConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
