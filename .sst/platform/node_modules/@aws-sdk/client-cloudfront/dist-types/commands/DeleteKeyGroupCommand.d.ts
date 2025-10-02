import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { DeleteKeyGroupRequest } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link DeleteKeyGroupCommand}.
 */
export interface DeleteKeyGroupCommandInput extends DeleteKeyGroupRequest {
}
/**
 * @public
 *
 * The output of {@link DeleteKeyGroupCommand}.
 */
export interface DeleteKeyGroupCommandOutput extends __MetadataBearer {
}
/**
 * @public
 * <p>Deletes a key group.</p>
 *          <p>You cannot delete a key group that is referenced in a cache behavior. First update
 * 			your distributions to remove the key group from all cache behaviors, then delete the key
 * 			group.</p>
 *          <p>To delete a key group, you must provide the key group's identifier and version. To get
 * 			these values, use <code>ListKeyGroups</code> followed by <code>GetKeyGroup</code> or
 * 				<code>GetKeyGroupConfig</code>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, DeleteKeyGroupCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, DeleteKeyGroupCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // DeleteKeyGroupRequest
 *   Id: "STRING_VALUE", // required
 *   IfMatch: "STRING_VALUE",
 * };
 * const command = new DeleteKeyGroupCommand(input);
 * const response = await client.send(command);
 * // {};
 *
 * ```
 *
 * @param DeleteKeyGroupCommandInput - {@link DeleteKeyGroupCommandInput}
 * @returns {@link DeleteKeyGroupCommandOutput}
 * @see {@link DeleteKeyGroupCommandInput} for command's `input` shape.
 * @see {@link DeleteKeyGroupCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link InvalidIfMatchVersion} (client fault)
 *  <p>The <code>If-Match</code> version is missing or not valid.</p>
 *
 * @throws {@link NoSuchResource} (client fault)
 *  <p>A resource that was specified is not valid.</p>
 *
 * @throws {@link PreconditionFailed} (client fault)
 *  <p>The precondition in one or more of the request fields evaluated to
 * 			<code>false</code>.</p>
 *
 * @throws {@link ResourceInUse} (client fault)
 *  <p>Cannot delete this resource because it is in use.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class DeleteKeyGroupCommand extends $Command<DeleteKeyGroupCommandInput, DeleteKeyGroupCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: DeleteKeyGroupCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: DeleteKeyGroupCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<DeleteKeyGroupCommandInput, DeleteKeyGroupCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
