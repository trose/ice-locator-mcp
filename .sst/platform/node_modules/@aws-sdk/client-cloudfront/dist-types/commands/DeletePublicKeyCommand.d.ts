import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { DeletePublicKeyRequest } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link DeletePublicKeyCommand}.
 */
export interface DeletePublicKeyCommandInput extends DeletePublicKeyRequest {
}
/**
 * @public
 *
 * The output of {@link DeletePublicKeyCommand}.
 */
export interface DeletePublicKeyCommandOutput extends __MetadataBearer {
}
/**
 * @public
 * <p>Remove a public key you previously added to CloudFront.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, DeletePublicKeyCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, DeletePublicKeyCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // DeletePublicKeyRequest
 *   Id: "STRING_VALUE", // required
 *   IfMatch: "STRING_VALUE",
 * };
 * const command = new DeletePublicKeyCommand(input);
 * const response = await client.send(command);
 * // {};
 *
 * ```
 *
 * @param DeletePublicKeyCommandInput - {@link DeletePublicKeyCommandInput}
 * @returns {@link DeletePublicKeyCommandOutput}
 * @see {@link DeletePublicKeyCommandInput} for command's `input` shape.
 * @see {@link DeletePublicKeyCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link AccessDenied} (client fault)
 *  <p>Access denied.</p>
 *
 * @throws {@link InvalidIfMatchVersion} (client fault)
 *  <p>The <code>If-Match</code> version is missing or not valid.</p>
 *
 * @throws {@link NoSuchPublicKey} (client fault)
 *  <p>The specified public key doesn't exist.</p>
 *
 * @throws {@link PreconditionFailed} (client fault)
 *  <p>The precondition in one or more of the request fields evaluated to
 * 			<code>false</code>.</p>
 *
 * @throws {@link PublicKeyInUse} (client fault)
 *  <p>The specified public key is in use.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class DeletePublicKeyCommand extends $Command<DeletePublicKeyCommandInput, DeletePublicKeyCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: DeletePublicKeyCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: DeletePublicKeyCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<DeletePublicKeyCommandInput, DeletePublicKeyCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
