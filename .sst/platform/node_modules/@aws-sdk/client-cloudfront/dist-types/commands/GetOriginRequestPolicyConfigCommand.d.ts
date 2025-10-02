import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetOriginRequestPolicyConfigRequest, GetOriginRequestPolicyConfigResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetOriginRequestPolicyConfigCommand}.
 */
export interface GetOriginRequestPolicyConfigCommandInput extends GetOriginRequestPolicyConfigRequest {
}
/**
 * @public
 *
 * The output of {@link GetOriginRequestPolicyConfigCommand}.
 */
export interface GetOriginRequestPolicyConfigCommandOutput extends GetOriginRequestPolicyConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets an origin request policy configuration.</p>
 *          <p>To get an origin request policy configuration, you must provide the policy's
 * 			identifier. If the origin request policy is attached to a distribution's cache behavior,
 * 			you can get the policy's identifier using <code>ListDistributions</code> or
 * 				<code>GetDistribution</code>. If the origin request policy is not attached to a
 * 			cache behavior, you can get the identifier using
 * 			<code>ListOriginRequestPolicies</code>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetOriginRequestPolicyConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetOriginRequestPolicyConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetOriginRequestPolicyConfigRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetOriginRequestPolicyConfigCommand(input);
 * const response = await client.send(command);
 * // { // GetOriginRequestPolicyConfigResult
 * //   OriginRequestPolicyConfig: { // OriginRequestPolicyConfig
 * //     Comment: "STRING_VALUE",
 * //     Name: "STRING_VALUE", // required
 * //     HeadersConfig: { // OriginRequestPolicyHeadersConfig
 * //       HeaderBehavior: "none" || "whitelist" || "allViewer" || "allViewerAndWhitelistCloudFront" || "allExcept", // required
 * //       Headers: { // Headers
 * //         Quantity: Number("int"), // required
 * //         Items: [ // HeaderList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //     },
 * //     CookiesConfig: { // OriginRequestPolicyCookiesConfig
 * //       CookieBehavior: "none" || "whitelist" || "all" || "allExcept", // required
 * //       Cookies: { // CookieNames
 * //         Quantity: Number("int"), // required
 * //         Items: [ // CookieNameList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //     },
 * //     QueryStringsConfig: { // OriginRequestPolicyQueryStringsConfig
 * //       QueryStringBehavior: "none" || "whitelist" || "all" || "allExcept", // required
 * //       QueryStrings: { // QueryStringNames
 * //         Quantity: Number("int"), // required
 * //         Items: [ // QueryStringNamesList
 * //           "STRING_VALUE",
 * //         ],
 * //       },
 * //     },
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetOriginRequestPolicyConfigCommandInput - {@link GetOriginRequestPolicyConfigCommandInput}
 * @returns {@link GetOriginRequestPolicyConfigCommandOutput}
 * @see {@link GetOriginRequestPolicyConfigCommandInput} for command's `input` shape.
 * @see {@link GetOriginRequestPolicyConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link NoSuchOriginRequestPolicy} (client fault)
 *  <p>The origin request policy does not exist.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetOriginRequestPolicyConfigCommand extends $Command<GetOriginRequestPolicyConfigCommandInput, GetOriginRequestPolicyConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetOriginRequestPolicyConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetOriginRequestPolicyConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetOriginRequestPolicyConfigCommandInput, GetOriginRequestPolicyConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
