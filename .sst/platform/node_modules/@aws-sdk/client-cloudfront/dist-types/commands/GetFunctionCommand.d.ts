import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import { Handler, HttpHandlerOptions as __HttpHandlerOptions, MetadataBearer as __MetadataBearer, MiddlewareStack } from "@smithy/types";
import { Uint8ArrayBlobAdapter } from "@smithy/util-stream";
import { CloudFrontClientResolvedConfig, ServiceInputTypes, ServiceOutputTypes } from "../CloudFrontClient";
import { GetFunctionRequest, GetFunctionResult } from "../models/models_1";
/**
 * @public
 */
export { __MetadataBearer, $Command };
/**
 * @public
 *
 * The input for {@link GetFunctionCommand}.
 */
export interface GetFunctionCommandInput extends GetFunctionRequest {
}
/**
 * @public
 */
export type GetFunctionCommandOutputType = Omit<GetFunctionResult, "FunctionCode"> & {
    FunctionCode?: Uint8ArrayBlobAdapter;
};
/**
 * @public
 *
 * The output of {@link GetFunctionCommand}.
 */
export interface GetFunctionCommandOutput extends GetFunctionCommandOutputType, __MetadataBearer {
}
/**
 * @public
 * <p>Gets the code of a CloudFront function. To get configuration information and metadata about
 * 			a function, use <code>DescribeFunction</code>.</p>
 *          <p>To get a function's code, you must provide the function's name and stage. To get these
 * 			values, you can use <code>ListFunctions</code>.</p>
 * @example
 * Use a bare-bones client and the command you need to make an API call.
 * ```javascript
 * import { CloudFrontClient, GetFunctionCommand } from "@aws-sdk/client-cloudfront"; // ES Modules import
 * // const { CloudFrontClient, GetFunctionCommand } = require("@aws-sdk/client-cloudfront"); // CommonJS import
 * const client = new CloudFrontClient(config);
 * const input = { // GetFunctionRequest
 *   Name: "STRING_VALUE", // required
 *   Stage: "DEVELOPMENT" || "LIVE",
 * };
 * const command = new GetFunctionCommand(input);
 * const response = await client.send(command);
 * // { // GetFunctionResult
 * //   FunctionCode: "BLOB_VALUE",
 * //   ETag: "STRING_VALUE",
 * //   ContentType: "STRING_VALUE",
 * // };
 *
 * ```
 *
 * @param GetFunctionCommandInput - {@link GetFunctionCommandInput}
 * @returns {@link GetFunctionCommandOutput}
 * @see {@link GetFunctionCommandInput} for command's `input` shape.
 * @see {@link GetFunctionCommandOutput} for command's `response` shape.
 * @see {@link CloudFrontClientResolvedConfig | config} for CloudFrontClient's `config` shape.
 *
 * @throws {@link NoSuchFunctionExists} (client fault)
 *  <p>The function does not exist.</p>
 *
 * @throws {@link UnsupportedOperation} (client fault)
 *  <p>This operation is not supported in this region.</p>
 *
 * @throws {@link CloudFrontServiceException}
 * <p>Base exception class for all service exceptions from CloudFront service.</p>
 *
 */
export declare class GetFunctionCommand extends $Command<GetFunctionCommandInput, GetFunctionCommandOutput, CloudFrontClientResolvedConfig> {
    readonly input: GetFunctionCommandInput;
    static getEndpointParameterInstructions(): EndpointParameterInstructions;
    /**
     * @public
     */
    constructor(input: GetFunctionCommandInput);
    /**
     * @internal
     */
    resolveMiddleware(clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>, configuration: CloudFrontClientResolvedConfig, options?: __HttpHandlerOptions): Handler<GetFunctionCommandInput, GetFunctionCommandOutput>;
    /**
     * @internal
     */
    private serialize;
    /**
     * @internal
     */
    private deserialize;
}
