import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetKeyGroupConfigRequest, GetKeyGroupConfigResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetKeyGroupConfigCommand}.
 */
export interface GetKeyGroupConfigCommandInput extends GetKeyGroupConfigRequest {
}
/**
 * @public
 *
 * The output of {@link GetKeyGroupConfigCommand}.
 */
export interface GetKeyGroupConfigCommandOutput extends GetKeyGroupConfigResult, __MetadataBearer {
}
/**
 * @public
 * <p>Gets a key group configuration.</p>
 *          <p>To get a key group configuration, you must provide the key group's identifier. If the
 * 			key group is referenced in a distribution's cache behavior, you can get the key group's
 * 			identifier using <code>ListDistributions</code> or <code>GetDistribution</code>. If the
 * 			key group is not referenced in a cache behavior, you can get the identifier using
 * 				<code>ListKeyGroups</code>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetKeyGroupConfigCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetKeyGroupConfigCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetKeyGroupConfigRequest
 *   Id: "STRING_VALUE", // required
 * };
 * const command = new GetKeyGroupConfigCommand(input);
 * const response = await client.send(command);
 * // { // GetKeyGroupConfigResult
 * //   KeyGroupConfig: { // KeyGroupConfig
 * //     Name: "STRING_VALUE", // required
 * //     Items: [ // PublicKeyIdList // required
 * //       "STRING_VALUE",
 * //     ],
 * //     Comment: "STRING_VALUE",
 * //   },
 * //   ETag: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetKeyGroupConfigCommandInput - {@link GetKeyGroupConfigCommandInput}
 * @returns {@link GetKeyGroupConfigCommandOutput}
 * @see {@link GetKeyGroupConfigCommandInput} for command's `input` shape.
 * @see {@link GetKeyGroupConfigCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link NoSuchResource} (client fault)
 *  <p>A resource that was specified is not valid.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetKeyGroupConfigCommand extends $Command<GetKeyGroupConfigCommandInput, GetKeyGroupConfigCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetKeyGroupConfigCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetKeyGroupConfigCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetKeyGroupConfigCommandInput, GetKeyGroupConfigCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
