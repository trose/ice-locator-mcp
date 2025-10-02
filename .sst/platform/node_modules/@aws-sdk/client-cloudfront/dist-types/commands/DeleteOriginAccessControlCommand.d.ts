import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { DeleteOriginAccessControlRequest } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link DeleteOriginAccessControlCommand}.
 */
export interface DeleteOriginAccessControlCommandInput extends DeleteOriginAccessControlRequest {
}
/**
 * @public
 *
 * The output of {@link DeleteOriginAccessControlCommand}.
 */
export interface DeleteOriginAccessControlCommandOutput extends __MetadataBearer {
}
/**
 * @public
 * <p>Deletes a CloudFront origin access control.</p>
 *          <p>You cannot delete an origin access control if it's in use. First, update all
 * 			distributions to remove the origin access control from all origins, then delete the
 * 			origin access control.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, DeleteOriginAccessControlCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, DeleteOriginAccessControlCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // DeleteOriginAccessControlRequest
 *   Id: "STRING_VALUE", // required
 *   IfMatch: "STRING_VALUE",
 * };
 * const command = new DeleteOriginAccessControlCommand(input);
 * const response = await client.send(command);
 * // {};
 *
 * ```
 *
 * @param DeleteOriginAccessControlCommandInput - {@link DeleteOriginAccessControlCommandInput}
 * @returns {@link DeleteOriginAccessControlCommandOutput}
 * @see {@link DeleteOriginAccessControlCommandInput} for command's `input` shape.
 * @see {@link DeleteOriginAccessControlCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link InvalidIfMatchVersion} (client fault)
 *  <p>The <code>If-Match</code> version is missing or not valid.</p>
 *
 * @throws {@link NoSuchOriginAccessControl} (client fault)
 *  <p>The origin access control does not exist.</p>
 *
 * @throws {@link OriginAccessControlInUse} (client fault)
 *  <p>Cannot delete the origin access control because it's in use by one or more
 * 			distributions.</p>
 *
 * @throws {@link PreconditionFailed} (client fault)
 *  <p>The precondition in one or more of the request fields evaluated to
 * 			<code>false</code>.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class DeleteOriginAccessControlCommand extends $Command<DeleteOriginAccessControlCommandInput, DeleteOriginAccessControlCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: DeleteOriginAccessControlCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: DeleteOriginAccessControlCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<DeleteOriginAccessControlCommandInput, DeleteOriginAccessControlCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
