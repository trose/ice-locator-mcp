import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { DeleteOriginRequestPolicyRequest } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link DeleteOriginRequestPolicyCommand}.
 */
export interface DeleteOriginRequestPolicyCommandInput extends DeleteOriginRequestPolicyRequest {
}
/**
 * @public
 *
 * The output of {@link DeleteOriginRequestPolicyCommand}.
 */
export interface DeleteOriginRequestPolicyCommandOutput extends __MetadataBearer {
}
/**
 * @public
 * <p>Deletes an origin request policy.</p>
 *          <p>You cannot delete an origin request policy if it's attached to any cache behaviors.
 * 			First update your distributions to remove the origin request policy from all cache
 * 			behaviors, then delete the origin request policy.</p>
 *          <p>To delete an origin request policy, you must provide the policy's identifier and
 * 			version. To get the identifier, you can use <code>ListOriginRequestPolicies</code> or
 * 				<code>GetOriginRequestPolicy</code>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, DeleteOriginRequestPolicyCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, DeleteOriginRequestPolicyCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // DeleteOriginRequestPolicyRequest
 *   Id: "STRING_VALUE", // required
 *   IfMatch: "STRING_VALUE",
 * };
 * const command = new DeleteOriginRequestPolicyCommand(input);
 * const response = await client.send(command);
 * // {};
 *
 * ```
 *
 * @param DeleteOriginRequestPolicyCommandInput - {@link DeleteOriginRequestPolicyCommandInput}
 * @returns {@link DeleteOriginRequestPolicyCommandOutput}
 * @see {@link DeleteOriginRequestPolicyCommandInput} for command's `input` shape.
 * @see {@link DeleteOriginRequestPolicyCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link IllegalDelete} (client fault)
 *  <p>You cannot delete a managed policy.</p>
 *
 * @throws {@link InvalidIfMatchVersion} (client fault)
 *  <p>The <code>If-Match</code> version is missing or not valid.</p>
 *
 * @throws {@link NoSuchOriginRequestPolicy} (client fault)
 *  <p>The origin request policy does not exist.</p>
 *
 * @throws {@link OriginRequestPolicyInUse} (client fault)
 *  <p>Cannot delete the origin request policy because it is attached to one or more cache
 * 			behaviors.</p>
 *
 * @throws {@link PreconditionFailed} (client fault)
 *  <p>The precondition in one or more of the request fields evaluated to
 * 			<code>false</code>.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class DeleteOriginRequestPolicyCommand extends $Command<DeleteOriginRequestPolicyCommandInput, DeleteOriginRequestPolicyCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: DeleteOriginRequestPolicyCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: DeleteOriginRequestPolicyCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<DeleteOriginRequestPolicyCommandInput, DeleteOriginRequestPolicyCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
